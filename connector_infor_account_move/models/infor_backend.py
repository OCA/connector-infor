# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class InforBackend(models.Model):
    _inherit = 'infor.backend'

    backend_infor_journal_line = fields.One2many(
        'backend.infor.journal.line',
        'infor_backend_id',
        string='Journals'
    )
    backend_infor_journal_custom_field = fields.One2many(
        'backend.infor.journal.custom.field',
        'infor_backend_id',
        string='Custom Field'
    )
