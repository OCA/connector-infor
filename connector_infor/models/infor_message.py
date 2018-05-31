# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
    content = fields.Text(readonly=True)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence']
        vals['message_ident'] = seq.next_by_code('infor.message')
        return super().create(vals)

    # TODO on new, trigger export?
