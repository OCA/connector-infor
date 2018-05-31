# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class InforJournal(models.Model):
    _name = 'infor.account.journal'
    _inherit = 'infor.binding'
    _inherits = {'account.journal': 'odoo_id'}
    _description = 'Infor Backend Journal'

    odoo_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=True,
        ondelete='cascade',
    )
    frequency = fields.Selection(
        [('manual', 'Manual'), ('realtime', 'Real-time'),
         ('hourly', 'Hourly'), ('daily', 'Daily'),
         ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        string='Frequency',
        default='manual',
    )
    use_summarize_entry = fields.Boolean(
        string='Summarize entries?'
    )

    _sql_constraints = [
        ('infor_uniq', 'unique(backend_id, odoo_id)',
         'This journal is already configured for this backend.'),
    ]

    def is_realtime(self):
        return self.frequency == 'realtime'
