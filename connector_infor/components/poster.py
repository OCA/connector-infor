# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent, Component


class InforBasePoster(AbstractComponent):
    """Post a message to Infor

    Base component, the various methods of sending the messages
    must be implemented in sub-components (sync or process).
    """
    _name = 'infor.base.poster'
    _inherit = ['infor.base']
    _usage = 'message.poster'

    def __init__(self, working_context):
        super().__init__(working_context)
        self.message = None

    def post(self, message):
        """Post the message to Infor"""
        self.message = message
        result = self._post()
        return result

    def _post(self):
        """Flow of the poster"""
        if self._has_to_skip():
            return
        # prevent other jobs to post the same message, will be released on
        # commit (or rollback)
        self.component('record.locker').lock(self.message)
        self._write_to_infor()
        self._update_message()

    def _write_to_infor(self):
        self.component(usage='storage').write(
            self.message.verb,
            self.message.message_ident,
            self.message.content
        )

    def _update_message(self):
        self.message.state = 'sent'

    def _has_to_skip(self):
        """Return True if the post of the message can be skipped"""
        return self.message.state != 'new'


class InforProcessPoster(Component):
    """Send file using the "Process" protocol

    This is not supported yet.

    The Process flow is described as:

    1. The message's content is pushed in the "outbox" table of the infor
    database. The message state is set as "sent" in odoo.
    2. Periodically, a cron checks the "inbox" table, in case of failure
    it sets the state of the message corresponding to the id as "failed".
    In case of success, it writes the Infor ID in the bindings related
    to the message and set the message state to 'success'.

    This component would do the step 1, but the InforDBStorage component
    is not yet implemented.

    This component is generic and is used unless overridden for a model.
    """
    _name = 'infor.process.poster'
    _inherit = ['infor.base.poster', 'infor.base']

    @classmethod
    def _component_match(cls, work):
        # collection is the backend here
        return work.collection.verb == 'Process'


class InforSyncPoster(Component):
    """Send file using the "Sync" protocol

    The Sync flow is described as:

    1. The message's content is written to a file system or sftp
    2. Odoo forgets about it, we'll receive no ack nor failure status, so we
    directly update the state of the message to "success", we also set the
    message id in the external_id of the infor.account.move so keep track that
    they have been exported

    This component is generic and is used unless overridden for a model.
    """
    _name = 'infor.sync.poster'
    _inherit = ['infor.base.poster', 'infor.base']

    @classmethod
    def _component_match(cls, work):
        # collection is the backend here
        return work.collection.verb == 'Sync'

    def _update_message(self):
        self.message.state = 'success'
        domain = [('infor_message_id', '=', self.message.id)]
        bindings = self.env['infor.account.move'].search(domain)
        bindings.write({
            'external_id': 'SYNC-%s' % self.message.message_ident,
        })
