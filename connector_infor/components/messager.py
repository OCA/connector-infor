# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class InforMessager(Component):
    """Create a message for a record in the local message box

    This component is generic and used by default for any model
    (unless there is a specialized component for a model).
    """
    _name = 'infor.messager'
    _inherit = ['infor.base']
    _usage = 'messager'

    def __init__(self, working_context):
        super().__init__(working_context)
        self.record = None

    def run(self, records, *args, **kwargs):
        """Create a message for ``records`` to be sent to Infor

        :param record: record to push as message
        """
        self.records = self._filter_records(records)
        result = self._run()
        return result

    def _filter_records(self, records):
        """Filter records to include in the Infor message

        By default, any record already in a message or having an infor id
        is removed.
        """
        return records.filtered(
            lambda rec: not (rec.infor_message_id or rec.external_id)
        )

    def _run(self):
        """Flow of the messager"""
        if self._has_to_skip():
            return

        assert self.records
        # prevent other jobs to create a message for the same records, will be
        # released on commit (or rollback)
        self.component('record.locker').lock(self.records)

        content = self._produce_message()
        message = self._create_message(content)
        self._update_records(message)

        return _('Message created')

    def _produce_message(self):
        producer = self.work.component(usage='message.producer')
        return producer.produce(self.records)

    def _create_message(self, content):
        return self.env['infor.message'].sudo().create({
            'backend_id': self.backend_record.id,
            'verb': self.backend_record.verb,
            'content': content,
        })

    def _update_records(self, message):
        self.records.sudo().write({
            'infor_message_id': message.id,
        })

    def _has_to_skip(self):
        """Return True if the creation of the message can be skipped"""
        # if all the records have been filtered, we have nothing to do
        return not self.records
