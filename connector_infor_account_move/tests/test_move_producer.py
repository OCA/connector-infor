# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from string import Template
from freezegun import freeze_time

from odoo.addons.connector_infor.tests.common import InforTestCase

from .common import AccountMoveMixin


@freeze_time("2018-06-18 17:07:00")
class TestMoveProducer(InforTestCase, AccountMoveMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.account = cls.env['account.account'].search([
            ('internal_type', '=', 'receivable')])
        cls.account.code = 'SPR'
        cls.journal = cls.create_journal()
        cls.move1 = cls.create_move_binding_1(cls.journal)
        cls.move2 = cls.create_move_binding_2(cls.journal)
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner'
            })
        cls.invoice = cls.env['account.invoice'].create({
            'journal_id': cls.journal.id,
            'partner_id': cls.partner.id,
            'move_id': cls.move1.odoo_id.id,
            # number is related to move_id.name
            })
        # Prepare custom fields
        cls.custom_field = cls.env['infor.account.journal.custom.field']
        cls.dimension_static = cls.custom_field.create({
            'name': 'Shape_of_the_earth',
            'field_type': 'dimensioncode',
            'data_type': 'static',
            'field_value': 'eliptic',
            'backend_id': cls.backend.id,
            })
        cls.dimension_dynamic = cls.custom_field.create({
            'name': 'Move_Line_Ref',
            'field_type': 'dimensioncode',
            'data_type': 'dynamic',
            'field_value': '',
            'field_default_value': 'never to hear',
            'field': 'object.name',
            'backend_id': cls.backend.id,
            })
        # If dynamic field can not be resolved, default value should be used
        cls.dimension_dynamic_bad_1 = cls.custom_field.create({
            'name': 'Get_default',
            'field_type': 'dimensioncode',
            'data_type': 'dynamic',
            'field_value': '',
            'field_default_value': 'default',
            'field': 'object.move_id.narration.unknown_chain',
            'backend_id': cls.backend.id,
            })
        cls.property_static = cls.custom_field.create({
            'name': 'Prop_une',
            'field_type': 'property',
            'data_type': 'static',
            'field_value': 'One',
            'field_default_value': 'default',
            'field': 'object.move_id.narration',
            'backend_id': cls.backend.id,
            })
        cls.property_dynamic = cls.custom_field.create({
            'name': 'Prop_deux',
            'field_type': 'property',
            'data_type': 'dynamic',
            'field_value': 'not_to_be_seen',
            'field_default_value': 'not_to_be_seen',
            'field': 'object.move_id.journal_id.code',
            'backend_id': cls.backend.id,
            })
        cls.company = cls.env['res.company'].create({
            'name': 'Test company',
            })

    @classmethod
    def compare_xml_line_by_line(self, content, expected):
        """This a quick way to check the diff line by line to ease debugging"""
        generated_line = [l.strip() for l in content.split(b'\n')
                          if len(l.strip())]
        expected_line = [l.strip() for l in expected.split(b'\n')
                         if len(l.strip())]
        l = len(expected_line)
        for i in range(l):
            if generated_line[i].strip() != expected_line[i].strip():
                print('Diff at {}/{}'.format(i, l))
                print('Expected {}'.format(expected_line[i]))
                print('Generated {}'.format(generated_line[i]))
                break

    def test_fiscal_time(self):
        """Check the fiscal year and period computation."""
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            self.company.fiscalyear_last_month = 8
            self.company.fiscalyear_last_day = 31
            end, period = component._compute_fiscal_time(self.company,
                                                         '2018-04-12')
            self.assertEqual(end, 2018)
            self.assertEqual(period, 8)
            self.company.fiscalyear_last_month = 12
            end, period = component._compute_fiscal_time(self.company,
                                                         '2018-11-11')
            self.assertEqual(end, 2018)
            self.assertEqual(period, 11)

    def test_move_not_summarized(self):
        """ """
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            # we need bytes to parse with lxml otherwise it gets confused
            # by the encoding header in the file
            content = component.produce(self.move1).encode('utf8')
            self.assertXmlDocument(content)
            # Load expected result from file setting some values as they can
            # not be predicted
            test_file = Template(self.read_test_file(
                'connector_infor_account_move/tests/'
                'examples/move_not_summarized.xml')
            )
            expected = test_file.substitute(
                INVOICE_ID=str(self.invoice.id),
                MOVE_ID=str(self.move1.id),
                TEST_DATE=self.move1.create_date,
            ).encode('utf8')
            self.compare_xml_line_by_line(content, expected)
            # self.assertXmlEquivalentOutputs(content, expected)

    def test_move_summarized(self):
        moves = self.move1 + self.move2
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            # we need bytes to parse with lxml otherwise it gets confused
            # by the encoding header in the file
            content = component.produce(moves).encode('utf8')
            self.assertXmlDocument(content)
            # Load expected result from file setting some values as they can
            # not be predicted
            test_file = Template(self.read_test_file(
                'connector_infor_account_move/tests/'
                'examples/move_summarized.xml')
            )
            expected = test_file.substitute(
                INVOICE_ID='',
                MOVE_ID='',
                TEST_DATE=self.move1.create_date,
            ).encode('utf8')
            # self.compare_xml_line_by_line(content, expected)
            self.assertXmlEquivalentOutputs(content, expected)

    def test_custom_fields(self):
        """Check that the custom fields are properly generated."""
        expected_properties = [
            {'base_object': '',
             'data_type': 'static',
             'default': 'default',
             'field_type': 'property',
             'name': 'Prop_une',
             'value': 'One'
             },
            {'base_object': 'object',
             'data_type': 'dynamic',
             'default': 'not_to_be_seen',
             'field_type': 'property',
             'name': 'Prop_deux',
             'value': 'move_id.journal_id.code'}
            ]
        expected_dimension = [
            {'base_object': '',
             'data_type': 'static',
             'default': False,
             'field_type': 'dimensioncode',
             'name': 'Shape_of_the_earth',
             'value': 'eliptic'
             },
            {'base_object': 'object',
             'data_type': 'dynamic',
             'default': 'never to hear',
             'field_type': 'dimensioncode',
             'name': 'Move_Line_Ref',
             'value': 'name'
             },
            {'base_object': 'object',
             'data_type': 'dynamic',
             'default': 'default',
             'field_type': 'dimensioncode',
             'name': 'Get_default',
             'value': ''
             }
            ]
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            content = component._render_context(self.move1)
        self.assertEqual(content.get('PROPERTIES'), expected_properties)
        self.assertEqual(content.get('DIMENSION_CODES'), expected_dimension)

    def test_mapping_directly(self):
        with self.backend.work_on('infor.account.move') as work:
            component = work.component(usage='message.producer')
            content = component._render_context(self.move1)
        # Checking the formating of datetime
        self.assertEqual(content.get('TRANSACTION_DATE'),
                         '2018-06-13T00:00:00Z')
