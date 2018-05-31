# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class InforBinding(models.Model):
    _name = 'infor.binding'
    _inherit = 'external.binding'
    _description = 'Infor Binding (abstract)'

    # odoo_id = odoo-side id must be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='infor.backend',
        string='Infor Backend',
        required=True,
        ondelete='restrict',
    )
    external_id = fields.Char(string='ID on Infor')

    _sql_constraints = [
        ('infor_uniq', 'unique(backend_id, external_id)',
         'A binding already exists with the same Infor ID.'),
    ]

    @api.multi
    @job(default_channel='root.infor')
    def generate_message(self):
        bindings = self.exists()
        if not bindings:
            return
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            messager = work.component('messager')
            return messager.run(bindings)