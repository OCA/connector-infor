# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class InforBackendJournalCustomField(models.Model):
    _name = 'infor.account.journal.custom.field'
    _description = 'Infor Backend Journal Custom Field'

    name = fields.Char(string='Name')
    field_type = fields.Selection(
        [('dimensioncode', 'DimensionCode'), ('property', 'Property')],
        string='Type',
    )
    data_type = fields.Selection(
        [('static', 'Static'), ('dynamic', 'Dynamic')],
        string='Data Type',
    )
    field_value = fields.Char(string='Value')
    field = fields.Char(string='Field')
    field_default_value = fields.Char(string='Default Value')
    backend_id = fields.Many2one(
        comodel_name='infor.backend',
        string='Infor Backend',
    )
