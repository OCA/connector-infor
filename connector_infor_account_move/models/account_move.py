# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from odoo import api, fields, models

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class AccountMove(models.Model):
    _inherit = 'account.move'

    infor_bind_ids = fields.One2many(
        comodel_name='infor.account.move',
        inverse_name='odoo_id',
        string='Bindings',
    )

    def post(self):
        result = super().post()
        self._infor_create_bindings()
        return result

    def _infor_prepare_binding(self, backend):
        return {
            'odoo_id': self.id,
            'backend_id': backend.id,
        }

    def _infor_create_bindings(self):
        """Create automatically bindings for moves to export to Infor"""
        backends = self.env['infor.backend'].search([])
        for backend in backends:
            sync_journal_ids = backend.mapped('infor_journal_ids.odoo_id')
            for move in self:
                if move.journal_id not in sync_journal_ids:
                    continue
                values = self._infor_prepare_binding(backend)
                self.env['infor.account.move'].create(values)


class InforAccountMove(models.Model):
    _name = 'infor.account.move'
    _inherit = 'infor.binding'
    _inherits = {'account.move': 'odoo_id'}
    _description = 'Infor Account Move'

    odoo_id = fields.Many2one(
        comodel_name='account.move',
        string='Move',
        required=True,
        ondelete='cascade',
    )
    # When not empty, indicate that we already generated an infor message for
    # this record so we will no longer export it. At some point, the infor
    # message will be dropped, and this field set to null, but we should have
    # an infor id returned by infor (in external_id)
    infor_message_id = fields.Many2one(
        comodel_name='infor.message',
        string='Infor Message',
        ondelete='set null',
        index=True,
    )
    infor_journal_id = fields.Many2one(
        comodel_name='infor.account.journal',
        compute='_compute_infor_journal_id',
        store=True,
        index=True,
    )

    @api.depends('backend_id', 'odoo_id.journal_id')
    def _compute_infor_journal_id(self):
        for binding in self:
            infor_journal_model = self.env['infor.account.journal']
            binding.infor_journal_id = infor_journal_model.search(
                [('backend_id', '=', self.backend_id.id),
                 ('odoo_id', '=', self.odoo_id.journal_id.id),
                 ],
                limit=1
            )

    def is_realtime(self):
        return self.infor_journal_id.is_realtime


class InforMoveListener(Component):
    _name = 'infor.account.move.listener'
    _inherit = 'base.connector.listener'
    _apply_on = ['infor.account.move']

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        if record.is_realtime():
            record.with_delay().generate_message()


class InforMoveProducer(Component):
    _name = 'infor.account.move.producer'
    _inherit = 'infor.jinja.producer'
    _apply_on = ['infor.account.move']

    _template_path = 'connector_infor_account_move/messages/move.xml.tmpl'

    @staticmethod
    def _format_numeric(n):
        """Format monetary value."""
        return '{0:.5f}'.format(n)

    @staticmethod
    def _default_text(moves):
        """Default description for some field."""
        dates = set(moves.mapped('date'))
        codes = set(moves.mapped('journal_id.code'))
        if len(dates) == 1 and len(codes) == 1:
            return '{}-{}'.format(
                next(iter(codes)),
                ''.join(next(iter(dates)).split('-'))
            )
        else:
            return ''

    def _prepare_custom_fields(self):
        """Prepare custom fields to be consumed by template.

        For the dynamic ones test that they are
        accesible in the specified model
        """
        dimension_codes = []
        properties = []
        account_move_line = self.env['account.move.line']
        for r in self.backend_record.infor_journal_custom_field_ids:
            base_object = ''
            field_chain = ''
            if r.data_type == 'dynamic' and r.field:
                base_object, field_chain = r.field.split('.', 1)
                try:
                    if base_object == 'object':
                        account_move_line.mapped(field_chain)
                    elif base_object == 'backend':
                        self.backend_record.mapped(field_chain)
                except:
                    field_chain = ''
                    pass
            custom_field = {
                'field_type': r.field_type,
                'data_type': r.data_type,
                'name': r.name,
                'value': (r.field_value if r.data_type == 'static'
                          else field_chain),
                'base_object': base_object or '',
                'default': r.field_default_value,
            }
            if r.field_type == 'dimensioncode':
                dimension_codes.append(custom_field)
            else:
                properties.append(custom_field)
        return dimension_codes, properties

    @staticmethod
    def _compute_fiscal_time(company, move_date_orm):
        """Compute accounting period and year.

        The period is the number of month to the next financial year end.
        The year is the year of the next financial deadline.
        """
        move_date = fields.Date.from_string(move_date_orm)
        fiscal_term = date(
            move_date.year,
            company.fiscalyear_last_month,
            company.fiscalyear_last_day,
        )
        if fiscal_term < move_date:
            fiscal_term = fiscal_term.replace(year=fiscal_term.year + 1)
        fiscal_period = 12 - abs(move_date.month - fiscal_term.month)
        return fiscal_term.year, fiscal_period

    @staticmethod
    def _compute_variation_id():
        """Compute the variation id

        Needs to be a unique value and each dispatch should have a higher
        value than the previous one.
        """
        return datetime.now().strftime('%Y%m%d%H%M%S%f')

    def _render_context_unique(self, context, move):
        """Jinja context for a single account move."""
        move_lines = move.line_ids.filtered(
            lambda line: line.credit or line.debit
        )
        invoice = self.env['account.invoice'].search(
            [('move_id', '=', move.odoo_id.id)],
            limit=1,
        )
        fiscalyear, fiscal_period = self._compute_fiscal_time(
            move.company_id, move.date)
        dimension_codes, properties = self._prepare_custom_fields()
        context.update({
            'CREATE_DATE': self._format_datetime(datetime.now()),
            'BUSINESS_UNIT': self.backend_record.accounting_entity_id,
            'COMPONENT_ID': self.backend_record.component_id,
            'VARIATION_ID': self._compute_variation_id(),
            'INVOICE_ID': invoice.id,
            'INVOICE_NUMBER': invoice.number or self._default_text(move),
            'ACCOUNTING_ENTITY_ID': move.id,
            'JOURNAL_CODE': move.journal_id.code,
            'CURRENCY': move.currency_id.name,
            'COMPANY_CURRENCY': move.company_id.currency_id.name,
            'JOURNAL_LINES': move_lines,
            'FISCAL_PERIOD': fiscal_period,
            'FISCAL_YEAR': fiscalyear,
            'DESCRIPTION': invoice.reference or self._default_text(move),
            # TODO Get default language of Odoo ?
            'LANGUAGE': 'en_US',
            'TRANSACTION_DATE': self._format_datetime(move.date),
            'DIMENSION_CODES': dimension_codes,
            'PROPERTIES': properties,
            'BACKEND': self.backend_record,
            'XML_VERSION': 'standard',
            'REPORTING_CURRENCY': 'EUR',
            'REPORTING_AMOUNT': 0,
        })
        return context

    def _render_context_summarized(self, context, moves):
        """Jinja context for multiple account move.

        Group the account move lines by account id  with amount sum.
        For all dynamic custom fields the default value is used.
        All value in the context that could be different are not set.
        """
        move_lines = moves.mapped('line_ids').filtered(
            lambda line: line.credit or line.debit
        )
        company = moves.mapped('company_id')
        if len(company) > 1:
            company = company[0]
            # log warning multiple company moves ?!
        fiscalyear = fiscal_period = ''

        dimension_codes, properties = self._prepare_custom_fields()

        currency = ''
        currencies = set(moves.mapped('currency_id.name'))
        if len(currencies) == 1:
            currency = next(iter(currencies))

        # Group lines by account number
        accounts = {}
        for line in move_lines:
            if line.account_id.id not in accounts:
                accounts[line.account_id.id] = line.balance
            else:
                accounts[line.account_id.id] += line.balance
        summarized_lines = []
        for account_id, amount in accounts.items():
            summarized_lines.append(
                {'account_id': self.env['account.account'].browse(account_id),
                 'credit': abs(amount) if amount < 0 else 0,
                 'debit': abs(amount) if amount > 0 else 0,
                 'currency_id': None,
                 })
        context.update({
            'CREATE_DATE': self._format_datetime(datetime.now()),
            'BUSINESS_UNIT': self.backend_record.accounting_entity_id,
            'COMPONENT_ID': self.backend_record.component_id,
            'VARIATION_ID': self._compute_variation_id(),
            'INVOICE_ID': '',
            'INVOICE_NUMBER': '',
            'ACCOUNTING_ENTITY_ID': '',
            'JOURNAL_CODE': '',
            'CURRENCY': currency,
            'COMPANY_CURRENCY': currency,
            'JOURNAL_LINES': summarized_lines,
            'FISCAL_PERIOD': fiscal_period,
            'FISCAL_YEAR': fiscalyear,
            'DESCRIPTION': self._default_text(move_lines),
            'LANGUAGE': 'en_US',
            'TRANSACTION_DATE': '',
            'DIMENSION_CODES': dimension_codes,
            'PROPERTIES': properties,
            'backend': self.backend_record,
            'XML_VERSION': 'summarized',
            'REPORTING_CURRENCY': 'EUR',
            'REPORTING_AMOUNT': 0,
        })
        return context

    def _render_context(self, records):
        """Return the context for jinja2 rendering

        Must be overridden to return a dict of values.
        """
        context = super()._render_context(records)
        if len(records) == 1:
            context.update(
                **self._render_context_unique(context, records)
            )
        else:
            context.update(
                **self._render_context_summarized(context, records)
            )
        return context
