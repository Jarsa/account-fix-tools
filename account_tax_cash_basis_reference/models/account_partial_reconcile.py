# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    def create_tax_cash_basis_entry(self, percentage_before_rec):
        res = super().create_tax_cash_basis_entry(percentage_before_rec)
        move_tax = self.env['account.move'].search(
            [('tax_cash_basis_rec_id', '=', self.id)])

        debit_move = self.debit_move_id
        credit_move = self.credit_move_id

        # Customer Invoices
        if (debit_move.journal_id.type == 'sale' and
                credit_move.journal_id.type in ['bank', 'cash']):
            origin_move = debit_move.move_id
        # Refunds Validation, we takes the latest date
        elif (debit_move.journal_id.type in ['sale', 'purchase'] and
                credit_move.journal_id.type in ['sale', 'purchase']):
            origin_move = (
                debit_move.move_id if
                debit_move.invoice_id.type in ['in_invoice', 'out_invoice']
                else credit_move.move_id)
        # Supplier Invoices
        else:
            if credit_move.invoice_id:
                origin_move = credit_move.move_id
            else:
                origin_move = debit_move.move_id
        move_tax.button_cancel()
        move_tax.write({
            'partner_id': origin_move.partner_id.id,
            'origin_move_id': origin_move.id,
            'ref': origin_move.name,
        })
        move_tax.line_ids.write({
            'partner_id': origin_move.partner_id.id,
        })
        move_tax.post()
        return res
