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

        # Prepare custom fields
        cls.dimension_static = cls.env['infor.account.journal.custom.field'].create({
            'name': 'Shape_of_the_earth',
            'field_type': 'dimensioncode',
            'data_type': 'static',
            'field_value': 'eliptic',
            'backend_id': cls.backend.id,
            })
        cls.dimension_dynamic = cls.env['infor.account.journal.custom.field'].create({
            'name': 'Move_Narration',
            'field_type': 'dimensioncode',
            'data_type': 'dynamic',
            'field_value': '',
            'field_default_value': 'never to hear',
            'field': 'object.narration',
            'backend_id': cls.backend.id,
            })
        # If dynamic field can not be resolved, default value should be used
        cls.dimension_dynamic_bad_1 = cls.env['infor.account.journal.custom.field'].create({
            'name': 'Get_default',
            'field_type': 'dimensioncode',
            'data_type': 'dynamic',
            'field_value': '',
            'field_default_value': 'default',
            'field': 'object.narration.lajsdflaksjfd',
            'backend_id': cls.backend.id,
            })
        cls.property_static = cls.env['infor.account.journal.custom.field'].create({
            'name': 'Prop_une',
            'field_type': 'property',
            'data_type': 'static',
            'field_value': 'One',
            'field_default_value': 'default',
            'field': 'object.narration',
            'backend_id': cls.backend.id,
            })
        cls.property_dynamic = cls.env['infor.account.journal.custom.field'].create({
            'name': 'Prop_deux',
            'field_type': 'property',
            'data_type': 'dynamic',
            'field_value': 'not_to_be_seen',
            'field_default_value': 'not_to_be_seen',
            'field': 'object.journal_id.code',
            'backend_id': cls.backend.id,
            })

    # TODO remove decorator once fixed
    # @unittest.expectedFailure
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

    def test_custom_fields(self):
        """Check that the custom fields are properly generated."""
        expected_dimension = [('Shape_of_the_earth', 'eliptic'),
                              ('Move_Narration', 'little story'),
                              ('Get_default', 'default')
                              ]
        expected_properties = [('Prop_une', 'One'),
                               ('Prop_deux', 'TEST')
                               ]
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            content = component._render_context(self.move1)
        self.assertEqual(content.get('DIMENSION_CODES'), expected_dimension)
        self.assertEqual(content.get('PROPERTIES'), expected_properties)

    def test_mapping_directly(self):
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            content = component._render_context(self.move1)
        # Checking the formating of datetime
        self.assertEqual(content.get('TRANSACTION_DATE'),
                         '2018-06-13T00:00:00Z')
