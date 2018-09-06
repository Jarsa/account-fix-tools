# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class PartialReconcile(TransactionCase):

    def setUp(self):
        super(PartialReconcile, self).setUp()
        self.tax = self.env.ref('l10n_mx.tax12')
        self.tax_account = self.env.ref('l10n_mx.cuenta208_01')
        self.partner = self.env.ref('base.res_partner_2')
        self.journal = self.env['account.journal'].search([
            ('type', '=', 'sale')], limit=1)
        self.journal.update_posted = True
        self.bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)
        self.bank_journal.update_posted = True
        self.product = self.env.ref(
            'product.product_product_7_product_template')
        self.tax.write({
            'tax_exigibility': 'on_payment',
            'cash_basis_account': self.tax_account.id,
            })
        self.cash_journal = self.env['account.journal'].search(
            [('type', '=', 'general')], limit=1)
        self.cash_journal.update_posted = True
        self.env.user.company_id.tax_cash_basis_journal_id = self.cash_journal

    def create_invoice(self):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'journal_id': self.journal.id,
            'name': 'Invoice to customer',
            'account_id': self.partner.property_account_receivable_id.id,
            'type': 'out_invoice',
        })
        self.env['account.invoice.line'].create({
            'product_id': self.product.id,
            'account_id': (self.product.get_product_accounts().
                           get('income').id),
            'quantity': 1,
            'price_unit': 1000,
            'invoice_id': invoice.id,
            'uom_id': self.product.uom_id.id,
            'discount': 10.0,
            'name': 'Product that cost 1000',
            'invoice_line_tax_ids': [(4, self.tax.id)],
        })
        invoice.action_invoice_open()
        return invoice

    def create_payment_entry(self):
        account_move_lines = [
            (0, 0, {
                'journal_id': self.bank_journal.id,
                'name': '/',
                'partner_id': self.partner.id,
                'date': fields.Date.today(),
                'account_id': self.partner.property_account_receivable_id.id,
                'debit': 0,
                'credit': 1150,
            }),
            (0, 0, {
                'journal_id': self.bank_journal.id,
                'name': '/',
                'partner_id': self.partner.id,
                'date': fields.Date.today(),
                'account_id': self.bank_journal.default_debit_account_id.id,
                'debit': 1150,
                'credit': 0,
            })
        ]
        move = self.env['account.move'].create({
            'journal_id': self.bank_journal.id,
            'name': '/',
            'partner_id': self.partner.id,
            'date': fields.Date.today(),
            'line_ids': account_move_lines,
            })
        move.post()
        return move

    def reconcile_moves(self, invoice, payment):
        move_lines = self.env['account.move.line']
        move_lines += invoice.line_ids.filtered(
            lambda r: r.account_id.reconcile)
        move_lines += payment.line_ids.filtered(
            lambda r: r.account_id.reconcile)
        move_lines.reconcile()

    def test_10_referece_cash_basis_journal_entry(self):
        invoice = self.create_invoice()
        payment_move = self.create_payment_entry()
        invoice_move = invoice.move_id
        self.reconcile_moves(invoice_move, payment_move)
        cash_move = self.env['account.move'].search([
            ('ref', '=', invoice.number),
            ('journal_id', '=', self.cash_journal.id)])
        self.assertEqual(cash_move.ref, invoice.number)
        self.assertEqual(cash_move.partner_id.id, self.partner.id)
