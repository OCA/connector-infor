# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component

from odoo.addons.connector_infor.tests.common import InforComponentRegistryCase

from .common import AccountMoveMixin


class TestMoveMessager(InforComponentRegistryCase, AccountMoveMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.create_journal()
        cls.move = cls.create_move_binding_1(cls.journal)

    def setUp(self):
        super().setUp()
        self.comp_registry.load_components('connector_infor_account_move')

    def test_messager(self):
        """"Generate a message record"""

        # Disable the original producer for account move and replace it by a
        # fake component that return hardcoded content for the message
        class DisableInforMoveProducer(Component):
            _inherit = 'infor.account.move.producer'
            _usage = None

        class TestInforMoveProducer(Component):
            _name = 'test.infor.account.move.producer'
            _inherit = 'infor.jinja.producer'
            _apply_on = 'infor.account.move'

            def produce(self, records):
                return '<data>my content</data>'

        self._build_components(DisableInforMoveProducer, TestInforMoveProducer)

        self.assertEqual(len(self.env['infor.message'].search([])), 0)

        with self.backend.work_on(
                'infor.account.move', components_registry=self.comp_registry
                ) as work:

            component = work.component(usage='messager')
            component.run(self.move)
            message = self.env['infor.message'].search([])

        self.assertEqual(len(message), 1)
        self.assertEqual(message.backend_id, self.backend)
        self.assertEqual(message.content, '<data>my content</data>')
        self.assertEqual(message.state, 'new')
        self.assertEqual(message.verb, 'Sync')

        self.assertEqual(self.move.infor_message_id, message)
