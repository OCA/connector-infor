# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class InforBackend(models.Model):
    _name = 'infor.backend'
    _inherit = ['mail.thread', 'connector.backend']
    _description = 'Infor Backend'

    name = fields.Char(string='Name', required=True)
    tenant_id = fields.Char(string='Tenant ID')
    logical_id = fields.Char(string='Logical ID')
    component_id = fields.Char(string='Component ID')
    confirmation_code = fields.Char(string='Confirmation Code')
    accounting_entity_id = fields.Char(string='Accounting Entity ID')
    dbsource_id = fields.Many2one(
        comodel_name='base.external.dbsource',
        string='DB Source',
        required=True,
    )

    @api.multi
    def test_infor_connnection(self):
        self.ensure_one()
        self.dbsource_id.connection_test()
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
            _logger.info("Exception details\n\n%s", err)
        finally:
            connection.close()
        return True
