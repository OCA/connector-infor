# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
    )
    infor_journal_id = fields.Many2one(
        comodel_name='infor.account.journal',
        compute='_compute_infor_journal_id',
        store=True,
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
        return self.infor_journal_id.is_realtime()


class InforMoveListener(Component):
    _name = 'infor.account.move.listener'
    _inherit = 'base.connector.listener'
    _apply_on = ['infor.account.move']

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        if record.is_realtime():
            record.with_delay().generate_message()


class InforMoveProducer(Component):
    _name = 'infor.invoice.producer'
    _inherit = 'infor.jinja.producer'
    _apply_on = ['infor.account.move']

    _template_path = 'connector_infor_account_move/messages/move.xml'

    def _render_context(self, record):
        """Return the context for jinja2 rendering

        Must be overridden to return a dict of values.
        """
        today = fields.Datetime.now()
        move = record

        move_lines = move.line_ids.filtered(
            lambda line: line.credit or line.debit
        )
        invoice = self.env['account.invoice'].search(
            [('move_id', '=', move.id)],
            limit=1,
        )
        # TODO: it's not complete, add:
        # BUSINESS_UNIT
        # FISCAL_PERIOD, FISCAL_YEAR
        # DESCRIPTION, TRANSACTION_DATE
        # LANGUAGE

        # TODO add custom fields
        # loop on backend.infor_journal_custom_field_ids
        # and generate 2 lists of (key, value), one for
        # dimensioncode and one for property, in the
        # invoice jinja template, loop on them
        context = super()._render_context(record)
        # TODO in the template, use a filter to show False as ''
        context.update({
            'CREATE_DATE': today,
            # TODO check the fields...
            'INVOICE_ID': invoice.id,
            'INVOICE_NUMBER': invoice.number,
            'ACCOUNTING_ENTITY_ID': move.id,
            'JOURNAL_CODE': move.journal_id.code,
            'SEC_CURRENCY': move.currency_id.name,
            'COMPANY_CURRENCY': move.company_id.currency_id.name,
            'JOURNAL_LINES': move_lines,
        })
        return context
