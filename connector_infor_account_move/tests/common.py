# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields


class AccountMoveMixin(object):

    @classmethod
    def create_journal(cls):
        return cls.env['account.journal'].create({
            'name': 'Test Journal',
            'code': 'TEST',
            'type': 'purchase',
        })

    def create_move(self, journal):
        return self.env['infor.account.move'].create({
            'backend_id': self.backend.id,
            'name': 'test',
            'date': fields.Date.today(),
            'journal_id': journal.id,
        })
