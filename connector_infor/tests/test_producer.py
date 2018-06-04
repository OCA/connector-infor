# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component

from .common import InforComponentRegistryCase


class TestProducer(InforComponentRegistryCase):

    def setUp(self):
        super().setUp()
        self.comp_registry.load_components('connector_infor')

    def test_jinja_producer(self):
        """"Generate a message from a jinja message producer"""
        class MyJinjaProducer(Component):
            _name = 'my.jinja.producer'
            _inherit = 'infor.jinja.producer'

            _template_path = 'connector_infor/tests/examples/in-1.xml'

            def _render_context(self, records):
                """Return the context for jinja2 rendering

                Must be overridden to return a dict of values.
                """
                context = super()._render_context(records)
                context['NAME'] = records.name
                return context

        self._build_components(MyJinjaProducer)

        # use a dummy model which we are sure we have
        with self.backend.work_on(
                'res.partner', components_registry=self.comp_registry
                ) as work:

            component = work.component(usage='message.producer')
            main_partner = self.env.ref('base.main_partner')
            # we need bytes to parse with lxml otherwise it gets confused
            # by the encoding header in the file
            content = component.produce(main_partner).encode('utf8')
            self.assertXmlDocument(content)

            expected = self.read_test_file(
                'connector_infor/tests/examples/out-1.xml'
            ).encode('utf8')
            self.assertXmlEquivalentOutputs(content, expected)
