# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unittest

from odoo.addons.connector_infor.tests.common import InforTestCase

from .common import AccountMoveMixin


class TestMoveProducer(InforTestCase, AccountMoveMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.create_journal()
        # TODO more elaborate move, add lines so we have totals
        cls.move1 = cls.create_move_binding(cls.journal)
        cls.move2 = cls.create_move_binding(cls.journal)

    # TODO remove decorator once fixed
    @unittest.expectedFailure
    def test_move_not_summarized(self):
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            # we need bytes to parse with lxml otherwise it gets confused
            # by the encoding header in the file
            content = component.produce(self.move1).encode('utf8')

            self.assertXmlDocument(content)

            # TODO: complete the expected xml
            expected = self.read_test_file(
                'connector_infor_account_move/tests/'
                'examples/move_not_summarized.xml'
            ).encode('utf8')
            self.assertXmlEquivalentOutputs(content, expected)

    # TODO test summarized move
    # TODO remove decorator once fixed
    @unittest.expectedFailure
    def test_move_summarized(self):
        moves = self.move1 + self.move2
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            # we need bytes to parse with lxml otherwise it gets confused
            # by the encoding header in the file
            content = component.produce(moves).encode('utf8')

            self.assertXmlDocument(content)

            # TODO: complete the expected xml
            expected = self.read_test_file(
                'connector_infor_account_move/tests/'
                'examples/move_summarized.xml'
            ).encode('utf8')
            self.assertXmlEquivalentOutputs(content, expected)

    # TODO add test for custom fields
