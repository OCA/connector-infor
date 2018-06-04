# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # TODO replace by a binding model
    infor_journal = fields.Char(string='Infor Journal ID')
