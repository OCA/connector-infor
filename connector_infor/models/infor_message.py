# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class InforMessage(models.Model):
    _name = 'infor.message'

    _rec_name = 'message_ident'

    backend_id = fields.Many2one(
        comodel_name='infor.backend',
        string='Infor Backend',
        required=True,
        ondelete='restrict',
        readonly=True,
    )
    message_ident = fields.Integer(index=True, readonly=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('sent', 'Sent'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        default='new',
        required=True,
        readonly=True,
    )
    verb = fields.Char(readonly=True)
    content = fields.Text(readonly=True)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence']
        vals['message_ident'] = seq.next_by_code('infor.message')
        record = super().create(vals)
        record._on_new_post_to_infor()
        return record

    @api.multi
    def _on_new_post_to_infor(self):
        self.with_delay().post()

    @job(default_channel='root.infor')
    def post(self):
        """Post Infor message"""
        message = self.exists()
        if not message:
            return
        with message.backend_id.work_on(self._name) as work:
            poster = work.component('message.poster')
            return poster.post(message)
