# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.tests import common
from odoo.modules.registry import Registry

from odoo.addons.queue_job.exception import RetryableJobError
from odoo.addons.component.core import WorkContext

from .common import InforTestCase


class TestLocker(InforTestCase):

    def setUp(self):
        super().setUp()
        self.registry2 = Registry(common.get_db_name())
        self.cr2 = self.registry2.cursor()
        self.env2 = api.Environment(self.cr2, self.env.uid, {})

        @self.addCleanup
        def reset_cr2():
            # rollback and close the cursor, and reset the environments
            self.env2.reset()
            self.cr2.rollback()
            self.cr2.close()

        self.backend2 = self.env2['infor.backend'].browse(self.backend.id)

    def test_lock(self):
        """Lock a record"""
        main_partner = self.env.ref('base.main_partner')
        work = WorkContext(model_name='res.partner',
                           collection=self.backend)
        locker = work.component_by_name('infor.record.locker')
        locker.lock(main_partner)

        main_partner2 = self.env2.ref('base.main_partner')
        work2 = WorkContext(model_name='res.partner',
                            collection=self.backend2)
        locker2 = work2.component_by_name('infor.record.locker')
        with self.assertRaises(RetryableJobError):
            locker2.lock(main_partner2)
