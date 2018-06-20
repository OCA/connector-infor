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

    @classmethod
    def create_move_binding_1(cls, journal):
        account = cls.env['account.account'].search([
            ('internal_type', '=', 'receivable')])
        move = cls.env['account.move'].create({
            'name': 'Test move',
            'date': '2018-06-15',
            'journal_id': journal.id,
            'state': 'draft',
            'narration': 'little story',
            'line_ids': [
                (0, 0, {
                    'name': 'ying',
                    'debit': 150,
                    'account_id': account.id,
                    'ref': 'debit_line',
                    }),
                (0, 0, {
                    'name': 'yang',
                    'credit': 150,
                    'account_id': account.id,
                    'ref': 'credit_line',
                    })
            ],
        })

        return cls.env['infor.account.move'].create({
            'backend_id': cls.backend.id,
            'name': 'test',
            'date': '2018-06-13 14:16:18',
            'journal_id': journal.id,
            'odoo_id': move.id,
        })

    @classmethod
    def create_move_binding_2(cls, journal):
        account = cls.env['account.account'].search([
            ('internal_type', '=', 'receivable')])
        move = cls.env['account.move'].create({
            'name': 'Test move 2',
            'date': '2018-06-15',
            'journal_id': journal.id,
            'state': 'draft',
            'narration': 'nothing to say',
            'line_ids': [
                (0, 0, {
                    'name': 'ying',
                    'debit': 50,
                    'account_id': account.id,
                    'ref': 'debit_line',
                    }),
                (0, 0, {
                    'name': 'ying',
                    'debit': 200,
                    'account_id': account.id,
                    'ref': 'debit_line',
                    }),
                (0, 0, {
                    'name': 'yang',
                    'credit': 250,
                    'account_id': account.id,
                    'ref': 'credit_line',
                    })
            ],
        })
        return cls.env['infor.account.move'].create({
            'backend_id': cls.backend.id,
            'name': 'test',
            'date': '2018-06-13 14:16:18',
            # 'journal_id': journal.id,
            'odoo_id': move.id,
        })

    @classmethod
    def create_move(cls, journal):
        return cls.env['account.move'].create({
            'name': 'test',
            'date': fields.Date.today(),
            'journal_id': journal.id,
        })
