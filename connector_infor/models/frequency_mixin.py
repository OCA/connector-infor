# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class FrequencyMixin(models.AbstractModel):
    """Add frequency/cron-related features to your models.

    On inheriting models you can:

    * check if you are in manual / realtime or cron mode
    * enable cron mode
    * configure a cron
    * save and get a specific cron to run something on your model

    You have to implement the method `run_cron`.
    """
    _name = 'infor.frequency.mixin'
    _description = 'Infor Frequency Mixin'

    frequency = fields.Selection(
        selection='_select_frequency',
        string='Interval type',
    )
    cron_id = fields.Many2one(
        'ir.cron',
        string='Related cron',
        domain=lambda self: [
            ('model_id', '=', self.env['ir.model']._get_id(self._name))
        ],
        readonly=True,
    )
    is_manual = fields.Boolean(
        compute='_compute_frequency',
        store=True,
    )
    is_realtime = fields.Boolean(
        compute='_compute_frequency',
        store=True,
    )
    is_cron = fields.Boolean(
        compute='_compute_frequency',
        store=True,
    )

    @api.multi
    @api.depends('frequency')
    def _compute_frequency(self):
        for record in self:
            if record.frequency == 'manual':
                record.is_manual = True
            elif record.frequency == 'realtime':
                record.is_realtime = True
            else:
                record.is_cron = True

    @api.model
    def _select_frequency(self):
        return [
            ('manual', 'Manual'),
            ('realtime', 'Realtime'),
            ('hours', 'Hourly'),
            ('days', 'Daily'),
            ('weeks', 'Weekly'),
            ('months', 'Monthly')
        ]

    @api.model
    def get_cron_vals(self):
        model_id = self.env['ir.model']._get_id(self._name)
        return {
            'name': 'Cron for Infor Journal (%s)' % self.display_name,
            'model_id': model_id,
            'state': 'code',
            'code': 'model.run_cron(%d)' % self.id,
            'interval_type': self.frequency,
            'interval_number': 1,
            'nextcall': fields.Datetime.now(),
            'active': True,
        }

    def _update_or_create_cron(self):
        """Update or create cron record if needed."""
        if self.is_cron:
            cron_model = self.env['ir.cron']
            cron_vals = self.get_cron_vals()
            if not self.cron_id:
                self.cron_id = cron_model.create(cron_vals)
            else:
                self.cron_id.write(cron_vals)
        else:
            if self.cron_id:
                self.cron_id.active = False

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._update_or_create_cron()
        return rec

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'frequency' in vals:
            for backend in self:
                backend._update_or_create_cron()
        return res

    @api.model
    def run_cron(self, res_id):
        raise NotImplementedError()
