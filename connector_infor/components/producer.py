# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from jinja2 import Template

from odoo.tools import file_open
from odoo.addons.component.core import AbstractComponent


class InforBaseProducer(AbstractComponent):
    """Produce a message for the outbox (interface)"""
    _name = 'infor.base.producer'
    _inherit = ['infor.base']
    _usage = 'message.producer'

    def produce(self, record):
        """Produce the content of a message"""
        raise NotImplementedError


class InforJinjaProducer(AbstractComponent):
    """Produce a message for the outbox using Jinja2

    Abstract, must be implemented for models.
    """
    _name = 'infor.jinja.producer'
    _inherit = ['infor.base.producer', 'infor.base']

    # path to a jinja2 template file
    _template_path = None

    @property
    def _template(self):
        assert self._template_path
        return file_open(self._template_path, 'r').read()

    def _render_context(self, record):
        """Return the context for jinja2 rendering

        Can be overridden to add values to render in the template.
        """
        backend = self.backend_record
        return {
            'TENANT_ID': backend.tenant_id,
        }

    def produce(self, record):
        """Produce the content of a message

        This component uses Jinja2 from a template file to produce
        the message. The :meth:`render_context` method must be overridden
        to return the values to fill in the template.
        """
        template = Template(self._template)
        return template.render(**self._render_context(record))
