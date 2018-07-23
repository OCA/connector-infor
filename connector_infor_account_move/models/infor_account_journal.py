# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class InforJournal(models.Model):
    _name = 'infor.account.journal'
    _inherit = ['infor.binding', 'infor.frequency.mixin']
    _inherits = {'account.journal': 'odoo_id'}
    _description = 'Infor Backend Journal'

    odoo_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=True,
        ondelete='cascade',
    )
    use_summarize_entry = fields.Boolean(
        string='Summarize entries?'
    )

    _sql_constraints = [
        ('infor_uniq', 'unique(backend_id, odoo_id)',
         'This journal is already configured for this backend.'),
    ]

    @api.model
    def run_cron(self, binding_id):
        binding = self.browse(binding_id)
        binding.generate_all_messages()

    @api.multi
    def generate_all_messages(self):
        for infor_journal in self:
            # search moves for which we don't have a message yet
            domain = [
                ('infor_journal_id', '=', infor_journal.id),
                ('infor_message_id', '=', False),
                ('external_id', '=', False),
            ]
            move_bindings = self.env['infor.account.move'].search(domain)
            if infor_journal.use_summarize_entry:
                move_bindings.with_delay().generate_message()
            else:
                for binding in move_bindings:
                    binding.with_delay().generate_message()
