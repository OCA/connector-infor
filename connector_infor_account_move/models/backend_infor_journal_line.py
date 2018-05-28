# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BackendInforJournalLine(models.Model):
    _name = 'backend.infor.journal.line'
    _description = 'Backend Infor Journal Line'

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
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
    infor_backend_id = fields.Many2one(
        comodel_name='infor.backend',
        string='Infor Backend',
    )