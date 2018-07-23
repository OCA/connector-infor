# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo.fields import Datetime as DatetimeField
from odoo.tools import file_open, ustr
from odoo.addons.component.core import AbstractComponent

from odoo.addons.mail.models.mail_template import mako_template_env


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

    @staticmethod
    def _format_datetime(d):
        """Format a datetime in the format expected by Infor."""
        if not isinstance(d, datetime):
            try:
                d = DatetimeField.from_string(d)
            except ValueError:
                d = None
        if d:
            return d.isoformat() + 'Z'
        return ''

    @property
    def _template(self):
        assert self._template_path
        return file_open(self._template_path, 'r').read()

    def _render_context(self, records):
        """Return the context for jinja2 rendering

        Can be overridden to add values to render in the template.
        """
        backend = self.backend_record
        return {
            'VERB': backend.verb,
            'TENANT_ID': backend.tenant_id,
        }

    def produce(self, records):
        """Produce the content of a message

        This component uses Jinja2 from a template file to produce
        the message. The :meth:`render_context` method must be overridden
        to return the values to fill in the template.
        For safetc the odoo sandboxed Jinja environment is used.
        """
        template_txt = self._template
        mako_template_env.variable_start_string = "{{"
        mako_template_env.variable_end_string = "}}"
        mako_template_env.block_start_string = "{%"
        mako_template_env.block_end_string = "%}"
        mako_template_env.comment_start_string = "{#"
        mako_template_env.comment_end_string = "#}"
        template = mako_template_env.from_string(ustr(template_txt))
        template.globals['format_datetime'] = self._format_datetime
        return template.render(**self._render_context(records))
