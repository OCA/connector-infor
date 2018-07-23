# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_infor.tests.common import InforTestCase

from .common import AccountMoveMixin


class TestAccountMove(InforTestCase, AccountMoveMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.create_journal()
        cls.move = cls.create_move(cls.journal)

    def test_binding_created_on_post_no_journal(self):
        """Binding is not created when a move is posted and no journal is
        setup"""
        with self.mock_with_delay() as (delayable_cls, delayable):
            self.move.post()
            self.assertEquals(self.move.state, 'posted')

            move_binding = self.env['infor.account.move'].search(
                [('odoo_id', '=', self.move.id),
                 ('backend_id', '=', self.backend.id)],
            )
            self.assertEquals(0, len(move_binding))

    def create_journal_binding(self, vals=None):
        default = {
            'backend_id': self.backend.id,
            'odoo_id': self.journal.id,
            'external_id': 'TEST',
            'use_summarize_entry': False,
            'frequency': 'manual',
        }
        if vals:
            default.update(vals)
        return self.env['infor.account.journal'].create(default)

    def test_binding_created_on_post(self):
        """Binding is created when a move is posted and journal is setup"""
        journal_binding = self.create_journal_binding()
        with self.mock_with_delay() as (delayable_cls, delayable):
            self.move.post()
            self.assertEquals(self.move.state, 'posted')

            move_binding = self.env['infor.account.move'].search(
                [('odoo_id', '=', self.move.id),
                 ('backend_id', '=', self.backend.id)],
            )
            self.assertEquals(1, len(move_binding))
            self.assertEquals(move_binding.infor_journal_id, journal_binding)
            self.assertFalse(move_binding.infor_message_id)
            self.assertFalse(move_binding.external_id)

            # the infor journal is configured as manual, no automatic job
            self.assertEqual(0, delayable_cls.call_count)
            delayable.generate_message().assert_not_called()

    def test_binding_manual_no_job(self):
        """Do not create a job for generating message when manual"""
        self.create_journal_binding()
        with self.mock_with_delay() as (delayable_cls, delayable):
            self.move.post()

            # the infor journal is configured as manual, no automatic job
            self.assertEqual(0, delayable_cls.call_count)
            delayable.generate_message().assert_not_called()

    def test_binding_cron_no_job(self):
        """Do not create a job for generating message when cron"""
        self.create_journal_binding({
            'frequency': 'days'
        })
        with self.mock_with_delay() as (delayable_cls, delayable):
            self.move.post()

            # the infor journal is configured as manual, no automatic job
            self.assertEqual(0, delayable_cls.call_count)
            delayable.generate_message().assert_not_called()

    def test_binding_job_delayed_on_realtime(self):
        """Create a job for generating message when realtime"""
        self.create_journal_binding({
            'frequency': 'realtime'
        })
        with self.mock_with_delay() as (delayable_cls, delayable):
            self.move.post()
            move_binding = self.move.infor_bind_ids

            self.assertEqual(1, delayable_cls.call_count)
            delay_args, delay_kwargs = delayable_cls.call_args
            self.assertEqual((move_binding,), delay_args)

            delayable.generate_message.assert_called_once()
