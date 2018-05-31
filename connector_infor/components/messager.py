# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import psycopg2

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.exception import RetryableJobError

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
        super(InforMessager, self).__init__(working_context)
        self.record = None

    def run(self, record, *args, **kwargs):
        """Create a message for ``record`` to be sent to Infor

        :param record: record to push as message
        """
        self.record = record
        result = self._run()
        return result

    def _run(self):
        """Flow of the messager"""
        assert self.record

        if self._has_to_skip():
            return

        # prevent other jobs to create a message for the same record will be
        # released on commit (or rollback)
        self._lock()

        content = self._produce_message()
        message = self._create_message(content)
        self._update_record(message)

        return _('Message created')

    def _produce_message(self):
        producer = self.work.component(usage='message.producer')
        return producer.produce(self.record)

    def _create_message(self, content):
        return self.env['infor.message'].sudo().create({
            'backend_id': self.backend_record.id,
            'content': content,
        })

    def _update_record(self, message):
        self.record.sudo().infor_message_id = message.id

    def _lock(self):
        """Lock the record.

        Lock the record so we are sure that only one job is running for this
        record if concurrent jobs have to create a message for the same record.
        When concurrent jobs try to work on the same record, the first one will
        lock and proceed, the others will fail to lock and will be retried
        later.
        """
        sql = ("SELECT id FROM %s WHERE ID = %%s FOR UPDATE NOWAIT" %
               self.model._table)
        try:
            self.env.cr.execute(sql, (self.record.id, ),
                                log_exceptions=False)
        except psycopg2.OperationalError:
            _logger.info('A concurrent job is already working on the same '
                         'record (%s with id %s). Job delayed later.',
                         self.model._name, self.record.id)
            raise RetryableJobError(
                'A concurrent job is already working on the same record '
                '(%s with id %s). The job will be retried later.' %
                (self.model._name, self.record.id))

    def _has_to_skip(self):
        """Return True if the creation of the message can be skipped"""
        return self.record.infor_message_id or self.record.external_id
