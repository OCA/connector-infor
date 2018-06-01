# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent, Component


class InforBaseStorage(AbstractComponent):
    """Manipulate files in the Infor storage

    Base component, the various methods of writing the files
    must be implemented in sub-components (sql or file).
    """
    _name = 'infor.base.storage'
    _inherit = ['infor.base']
    _usage = 'storage'

    def write(self, verb, message_id, content):
        """Write the message's content to the Infor storage"""
        raise NotImplementedError

    def set_processed(self, message_id):
        raise NotImplementedError


class InforDBStorage(Component):
    """Use a database for the messages

    Using the 'base_external_dbsource' addon
    """
    _name = 'infor.db.storage'
    _inherit = ['infor.base.storage', 'infor.base']

    @classmethod
    def _component_match(cls, work):
        # collection is the backend here
        return work.collection.exchange_type == 'sql'


class InforFileStorage(Component):
    """Use a file backend (filesystem or sftp) for the messages

    File backend is provided by the 'file.backend' model in the
    'storage_backend' addon.
    """
    _name = 'infor.file.storage'
    _inherit = ['infor.base.storage', 'infor.base']

    @classmethod
    def _component_match(cls, work):
        # collection is the backend here
        return work.collection.exchange_type == 'file'

    def write(self, verb, message_id, content):
        """Write the message's content to the Infor storage"""
        filename = '%s-%d.xml' % (verb, message_id)
        self.backend_record.storage_backend_id._add_bin_data(
            filename,
            content.encode(),
        )

    def set_processed(self, message_id):
        # does not exists with the files
        return
