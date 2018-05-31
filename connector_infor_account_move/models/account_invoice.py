# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.queue_job.job import job
from odoo.addons.component.core import Component


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _infor_on_validate(self):
        """Initiate an export to Infor on validation of invoice

        We have to push to infor any posted journal entry in the
        journal configured on the backend.
        """
        for backend in self.env['infor.backend'].search([]):
            sync_journal_ids = backend.mapped('infor_journal_ids.journal_id')
            if self.move_id.journal_id in sync_journal_ids:
                continue
            self.with_delay().infor_generate_message(backend)

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            invoice._infor_on_validate()
        return res

    @job(default_channel='root.infor')
    def infor_generate_message(self, backend):
        if not self.exists():
            return
        self.ensure_one()
        with backend.work_on(self._name) as work:
            messager = work.component('messager')
            return messager.run(self)


class InforInvoiceProducer(Component):
    _name = 'infor.invoice.producer'
    _inherit = 'infor.jinja.producer'
    _apply_on = ['account.invoice']

    _template_path = 'connector_infor_account_move/messages/invoice.xml'

    def _render_context(self, record):
        """Return the context for jinja2 rendering

        Must be overridden to return a dict of values.
        """
        today = fields.Datetime.now()
        move = record.move_id
        move_lines = move.line_ids.filtered(
            lambda line: line.credit or line.debit
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
        context.update({
            'CREATE_DATE': today,
            'INVOICE_ID': record.id,
            'INVOICE_NUMBER': record.number,
            'ACCOUNTING_ENTITY_ID': move.id,
            'JOURNAL_CODE': move.journal_id.code,
            'SEC_CURRENCY': move.currency_id.name,
            'COMPANY_CURRENCY': move.company_id.currency_id.name,
            'JOURNAL_LINES': move_lines,
        })
        return context
