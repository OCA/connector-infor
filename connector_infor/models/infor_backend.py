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

    name = fields.Char(string='Name', required=True)
    tenant_id = fields.Char(string='Tenant ID', default='Infor')
    logical_id = fields.Char(string='Logical ID')
    component_id = fields.Char(string='Component ID')
    confirmation_code = fields.Char(string='Confirmation Code')
    accounting_entity_id = fields.Char(string='Accounting Entity ID')
    type = fields.Selection(
        [('sql', 'SQL'), ('file', 'File')],
        string='Type',
        default='sql',
        required=True,
    )
    dbsource_id = fields.Many2one(
        comodel_name='base.external.dbsource',
        string='DB Source',
    )
    file_backend_id = fields.Many2one(
        comodel_name='file.backend',
        string='File Backend',
    )
    infor_message_ids = fields.One2many(
        comodel_name='infor.message',
        inverse_name='backend_id',
        string='Messages',
        readonly=True,
    )

    @api.multi
    def test_infor_connnection(self):
        self.ensure_one()
        if self.type == 'sql':
            self.dbsource_id.connection_test()
        else:
            self.file_backend_id.sftp_connnection_test()
        return True

    @api.multi
    def test_insert_record(self):
        self.ensure_one()
        sql = "INSERT INTO cor_property (C_PROPERTY_NAME,C_PROPERTY_VALUE) " \
              "VALUES (%(property_name)s, %(property_value)s)"
        execute_params = {
            'property_name': 'new_odoo_record',
            'property_value': '3.0.0',
        }
        try:
            connection = self.dbsource_id.connection_open_mysql()
            self.dbsource_id.execute(sql, execute_params, False)
        except Exception as err:
            self.cr.rollback()
            _logger.info("Exception details\n\n%s", err)
        finally:
            connection.close()
        return True

    @api.multi
    def action_view_infor_messages(self):
        self.ensure_one()
        action = self.env.ref('connector_infor.action_infor_message').read()[0]

        domain = action['domain']
        action['domain'] = literal_eval(domain) if domain else []
        action['domain'].append(('backend_id', '=', self.id))
        return action
