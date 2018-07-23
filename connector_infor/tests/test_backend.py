# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import InforTestCase


class TestBackend(InforTestCase):

    def test_verb(self):
        """Check the proper verb is computed from the exchange type"""
        self.backend.exchange_type = 'file'
        self.assertEqual(self.backend.verb, 'Sync')
        self.backend.exchange_type = 'sql'
        self.assertEqual(self.backend.verb, 'Process')

    def test_work_on(self):
        """"Check that we can get a component from the backend"""
        with self.backend.work_on('infor.backend') as work:
            component = work.component_by_name('infor.base')
            self.assertEqual(component._name, 'infor.base')
