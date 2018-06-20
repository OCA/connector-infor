# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
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

    _template_path = 'connector_infor_account_move/messages/move.xml'

    @staticmethod
    def _format_datetime(d):
        if isinstance(d, str):
            d = fields.Datetime.from_string(d)
        return d.isoformat() + 'Z'

    @staticmethod
    def _format_numeric(n):
        return '{0:.5f}'.format(n)

    @staticmethod
    def _default_text(moves):
        dates = moves.mapped('date')
        if len(dates) == 1:
            return 'STOCK-{}'.format(''.join(dates[0].split('-')))
        else:
            return ''

    def _render_context_unique(self, context, move):
        today = fields.Datetime.now()
        move_lines = move.line_ids.filtered(
            lambda line: line.credit or line.debit
        )
        invoice = self.env['account.invoice'].search(
            [('move_id', '=', move.odoo_id.id)],
            limit=1,
        )
        fiscalyear_end = datetime(
            datetime.now().year,
            int(move.company_id.fiscalyear_last_month),
            int(move.company_id.fiscalyear_last_day)
        )
        if fiscalyear_end < datetime.now():
            fiscalyear_end = fiscalyear_end.replace(
                    year=fiscalyear_end.year + 1)
        # Fiscal period is the number of month from the end of the fiscal year
        fiscal_period = (12 - fiscalyear_end.month + int(move.date[5:7]))
        # Prepare custom fields, for the dynamic ones test that they are
        # accesible in the specified model
        dimension_codes = []
        properties = []
        account_move_line = self.env['account.move.line']
        for r in self.backend_record.infor_journal_custom_field_ids:
            base_object = ''
            if r.data_type == 'dynamic':
                base_object, field_chain = r.field.split('.', 1)
                try:
                    if base_object == 'object':
                        account_move_line.mapped(field_chain)
                    elif base_object == 'backend':
                        self.backend_record.mapped(field_chain)
                except:
                    field_chain = ''
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

        context.update({
            'CREATE_DATE': self._format_datetime(today),
            'BUSINESS_UNIT': self.backend_record.accounting_entity_id,
            'INVOICE_ID': invoice.id,
            'INVOICE_NUMBER': invoice.number or self._default_text(move),
            # TODO Not in the xml template ?
            'ACCOUNTING_ENTITY_ID': move.id,
            'JOURNAL_CODE': move.journal_id.code,
            # TODO Could not find this one in the xml file !?
            'SEC_CURRENCY': move.currency_id.name,
            'CURRENCY': move.currency_id.name,
            # TODO Should not the amount be taken directely from the line
            #      in the template ?
            'SEC_AMOUNT': self._format_numeric(move.amount),
            'COMPANY_CURRENCY': move.company_id.currency_id.name,
            # TODO Convert
            'COMPANY_AMOUNT': self._format_numeric(move.amount),
            'JOURNAL_LINES': move_lines,
            'FISCAL_PERIOD': fiscal_period,
            'FISCAL_YEAR': fiscalyear_end.year,
            'DESCRIPTION': invoice.reference or self._default_text(move),
            # TODO Get default language of Odoo ?
            'LANGUAGE': 'en_US',
            'TRANSACTION_DATE': self._format_datetime(move.date),
            'DIMENSION_CODES': dimension_codes,
            'PROPERTIES': properties,
            'backend': self.backend_record,
        })
        return context

    def _render_context_summarized(self, context, moves):
        # TODO implement summarized context
        # the fields which can be different (description, ...) are
        # left empty. The amounts are summed.
        today = fields.Datetime.now()
        move_lines = moves.mapped('line_ids').filtered(
            lambda line: line.credit or line.debit
        )
        invoices = self.env['account.invoice'].search(
            [('move_id', 'in', moves.mapped('odoo_id').ids)],
            limit=1,
        )
        invoice = None
        if len(invoices) == 1:
            invoice = invoices[0]
        company = moves.mapped('company_id')
        if len(company) > 1:
            company = company[0]
            # log warning multiple company moves ?!

        fiscalyear_end = datetime(
            datetime.now().year,
            int(company.fiscalyear_last_month),
            int(company.fiscalyear_last_day)
        )
        if fiscalyear_end < datetime.now():
            fiscalyear_end = fiscalyear_end.replace(
                    year=fiscalyear_end.year + 1)
        move_months = list(set([d[5:7] for d in moves.mapped('date')]))
        if len(move_months) == 1:
            # Fiscal period is the number of month from the end of the
            # fiscal year
            fiscal_period = (12 - fiscalyear_end.month + int(move_months[0]))
        else:
            fiscal_period = ''
            # log warning account_move on multiple fiscal period
        # Prepare custom fields, for the dynamic ones test that they are
        # accesible in the specified model
        dimension_codes = []
        properties = []
        account_move_line = self.env['account.move.line']
        for r in self.backend_record.infor_journal_custom_field_ids:
            base_object = ''
            if r.data_type == 'dynamic':
                base_object, field_chain = r.field.split('.', 1)
                try:
                    if base_object == 'object':
                        account_move_line.mapped(field_chain)
                    elif base_object == 'backend':
                        self.backend_record.mapped(field_chain)
                except:
                    field_chain = ''
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
        # Only pass values that are the same for all account moves
        journal_code = ''
        journal_codes = moves.mapped('journal_id.code')
        if len(journal_codes) == 1:
            journal_code = journal_codes[0]
        move_date = ''
        move_dates = moves.mapped('date')
        if len(move_dates) == 1:
            move_date = move_dates[0]
        currency = ''
        currencies = moves.mapped('currency_id.name')
        if len(currencies) == 1:
            currency = currencies[0]
        # Group lines by account number
        accounts = {}
        for line in move_lines:
            if not line.account_id.id in accounts:
                accounts[line.account_id.id] = line.credit
            else:
                accounts[line.account_id.id] += line.credit
        context.update({
            'CREATE_DATE': self._format_datetime(today),
            'BUSINESS_UNIT': self.backend_record.accounting_entity_id,
            'INVOICE_ID': '',
            'INVOICE_NUMBER': (invoice.number if invoice
                               else self._default_text(moves)),
            # TODO Not in the xml template ?
            'ACCOUNTING_ENTITY_ID': '',
            'JOURNAL_CODE': journal_code,
            # TODO Could not find this one in the xml file !?
            # 'SEC_CURRENCY': move.currency_id.name,
            'CURRENCY': currency,
            'SEC_AMOUNT': self._format_numeric(sum(moves.mapped('amount'))),
            'COMPANY_CURRENCY': currency,
            'COMPANY_AMOUNT': self._format_numeric(
                sum(moves.mapped('amount'))),

            'JOURNAL_LINES': move_lines,
            'FISCAL_PERIOD': fiscal_period,
            'FISCAL_YEAR': fiscalyear_end.year,
            'DESCRIPTION': '',
            'LANGUAGE': 'en_US',
            'TRANSACTION_DATE': move_date,
            'DIMENSION_CODES': dimension_codes,
            'PROPERTIES': properties,
            'backend': self.backend_record,
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
