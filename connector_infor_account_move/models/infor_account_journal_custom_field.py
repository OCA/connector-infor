# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class InforBackendJournalCustomField(models.Model):
    _name = 'infor.account.journal.custom.field'
    _description = 'Infor Backend Journal Custom Field'

    name = fields.Char()
    field_type = fields.Selection(
        [('dimensioncode', 'DimensionCode'), ('property', 'Property')],
        string='Type',
    )
    data_type = fields.Selection(
        [('static', 'Static'), ('dynamic', 'Dynamic')],
    )
    field_value = fields.Char(
        string='Value',
        help='Used for static type fields',
    )
    field = fields.Char(
        string='Dynamic Field',
        help='Dynamicaly computed in a record fields hierarchy. If starting '
             'by "object." the account.move.line will be used as base. If '
             'starting by "backend." then the infor.backend is used.'
             'If the field can not be resolved the value in "default_value" '
             'wil be used instead.',
    )
    field_default_value = fields.Char(
        string='Default Value',
        help='Used if the dynamic field resolution fails.',
    )
    backend_id = fields.Many2one(
        comodel_name='infor.backend',
        string='Infor Backend',
    )
