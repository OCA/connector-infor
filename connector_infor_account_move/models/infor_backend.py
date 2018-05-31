# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class InforBackend(models.Model):
    _inherit = 'infor.backend'

    infor_journal_ids = fields.One2many(
        comodel_name='infor.backend.journal',
        inverse_name='infor_backend_id',
        string='Journals'
    )
    infor_journal_custom_field_ids = fields.One2many(
        comodel_name='infor.backend.journal.custom.field',
        inverse_name='infor_backend_id',
        string='Custom Field'
    )
