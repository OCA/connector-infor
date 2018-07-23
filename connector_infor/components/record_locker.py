# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import psycopg2

from odoo.addons.component.core import Component
from odoo.addons.connector.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class InforRecordLocker(Component):
    _name = 'infor.record.locker'
    _inherit = ['infor.base']
    _usage = 'record.locker'

    def lock(self, records):
        """Lock the records.

        Lock the record so we are sure that only one job is running for this
        record(s) if concurrent jobs have to create a message for the same
        record(s).
        When concurrent jobs try to work on the same record(s), the first one
        will lock and proceed, the others will fail to lock and will be retried
        later.
        """
        sql = ("SELECT id FROM %s WHERE ID IN %%s FOR UPDATE NOWAIT" %
               self.model._table)
        try:
            self.env.cr.execute(sql, (tuple(records.ids), ),
                                log_exceptions=False)
        except psycopg2.OperationalError:
            _logger.info('A concurrent job is already working on the same '
                         'record (%s with one id in %s). Job delayed later.',
                         self.model._name, tuple(records.ids))
            raise RetryableJobError(
                'A concurrent job is already working on the same record '
                '(%s with one id in %s). The job will be retried later.' %
                (self.model._name,  tuple(records.ids))
            )
