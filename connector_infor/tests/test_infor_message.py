# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import InforTestCase


class TestInforMessage(InforTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def create_message(self, vals=None):
        default = {
            'backend_id': self.backend.id,
            'verb': 'Sync',
            'content': 'foo',
        }
        if vals:
            default.update(vals)
        return self.env['infor.message'].create(default)

    def test_default_values(self):
        message1 = self.create_message()
        message2 = self.create_message()
        self.assertEqual(message1.state, 'new')
        self.assertEqual(message2.state, 'new')
        # check that sequence is incremented
        self.assertEqual(message1.message_ident + 1, message2.message_ident)

    def test_new_message_post_delayed(self):
        """When a new message is created, a job to post it is delayed"""
        with self.mock_with_delay() as (delayable_cls, delayable):
            message = self.create_message()
            self.assertEqual(1, delayable_cls.call_count)
            delay_args, delay_kwargs = delayable_cls.call_args
            self.assertEqual((message,), delay_args)

            delayable.post.assert_called_once()
