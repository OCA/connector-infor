# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Infor Connector",
    "summary": "Integration between Odoo and Infor",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Connector",
    "website": "https://github.com/OCA/connector_infor",
    "depends": [
        "connector",
        "base_external_dbsource_mysql",
        "storage_backend_sftp",
    ],
    "external_dependencies": {
        "python": [
            "xmlunittest",
        ],
    },
    "data": [
        "security/connector_security.xml",
        "security/ir.model.access.csv",
        "views/infor_backend_views.xml",
        "views/infor_message_views.xml",
        "views/connector_infor_menu.xml",
        "data/ir_sequence.xml",
    ],
    "installable": True,
}
