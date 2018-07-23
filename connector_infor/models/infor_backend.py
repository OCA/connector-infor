# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from ast import literal_eval

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class InforBackend(models.Model):
    _name = 'infor.backend'
    _inherit = ['mail.thread', 'connector.backend']
    _description = 'Infor Backend'

    # the verb is the kind of synchronization used with infor
    # 'process' is when using a database, we receive a return from infor, it
    # allows to handle failures and get back IDs.
    # 'sync' is used with the files exchanges, we put the file somewhere and
    # don't have any error handling or return from infor
    _verbs = {
        'sql': 'Process',
        'file': 'Sync'
    }

    name = fields.Char(required=True)
    tenant_id = fields.Char(string='Tenant ID', default='Infor')
    logical_id = fields.Char(string='Logical ID')
    component_id = fields.Char(string='Component ID')
    confirmation_code = fields.Char()
    accounting_entity_id = fields.Char(string='Accounting Entity ID')
    exchange_type = fields.Selection(
        [('sql', 'SQL'), ('file', 'File')],
        string='Type',
        default='sql',
        required=True,
    )
    dbsource_id = fields.Many2one(
        comodel_name='base.external.dbsource',
        string='DB Source',
    )
    storage_backend_id = fields.Many2one(
        comodel_name='storage.backend',
        string='File Backend',
    )
    infor_message_ids = fields.One2many(
        comodel_name='infor.message',
        inverse_name='backend_id',
        string='Messages',
        readonly=True,
    )
    verb = fields.Char(
        compute='_compute_verb'
    )

    @api.depends('exchange_type')
    def _compute_verb(self):
        for backend in self:
            backend.verb = self._verbs[backend.exchange_type]

    @api.multi
    def test_infor_connnection(self):
        self.ensure_one()
        if self.exchange_type == 'sql':
            self.dbsource_id.connection_test()
        else:
            self.storage_backend_id.connnection_test()
        return True

    @api.multi
    def action_view_infor_messages(self):
        self.ensure_one()
        action = self.env.ref('connector_infor.action_infor_message').read()[0]

        domain = action['domain']
        action['domain'] = literal_eval(domain) if domain else []
        action['domain'].append(('backend_id', '=', self.id))
        return action

    @api.onchange('exchange_type')
    def validation_exchange_type(self):
        """Disable the SQL exchange type selection"""
        if self.exchange_type == 'sql':
            self.exchange_type = ''
            return {'warning': {'title': 'Not implemented',
                                'message': 'The synchronization through a '
                                           'database is not yet implemented.'}
                    }
        return {}
