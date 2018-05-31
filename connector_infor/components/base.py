# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.component.core import AbstractComponent


class BaseInforConnectorComponent(AbstractComponent):
    """ Base Infor Connector Component

    All components of this connector should inherit from it.
    """

    _name = 'infor.base'
    _inherit = 'base.connector'
    _collection = 'infor.backend'
