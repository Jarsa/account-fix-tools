# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    @api.model
    def create(self, vals):
        res = super(AccountPartialReconcileCashBasis, self).create(vals)
        move_tax = self.env['account.move'].search(
            [('tax_cash_basis_rec_id', '=', res.id)])

        debit_move = res.debit_move_id
        credit_move = res.credit_move_id
        if (debit_move.journal_id.type == 'sale' and
                credit_move.journal_id.type in ['bank', 'cash']):
            origin_move = debit_move.move_id
            move_date = credit_move.date
        # Refunds Validation, we takes the latest date
        elif (debit_move.journal_id.type in ['sale', 'purchase'] and
                credit_move.journal_id.type in ['sale', 'purchase']):
            origin_move = (
                debit_move.move_id if
                debit_move.invoice_id.type in ['in_invoice', 'out_invoice']
                else credit_move.move_id)
            debit_date = fields.Date.from_string(debit_move.date)
            credit_date = fields.Date.from_string(credit_move.date)
            move_date = (
                fields.Date.to_string(debit_date) if
                debit_date > credit_date else
                fields.Date.to_string(credit_date))
        else:
            if credit_move.invoice_id:
                origin_move = credit_move.move_id
                move_date = debit_move.date
            else:
                origin_move = debit_move.move_id
                move_date = credit_move.date

        move_tax.button_cancel()
        move_tax.write({
            'partner_id': origin_move.partner_id.id,
            'date': move_date,
            'move_id': origin_move.id,
            'ref': origin_move.name,
        })
        move_tax.line_ids.write({
            'partner_id': origin_move.partner_id.id,
            'date': move_date,
        })
        move_tax.post()
        return res
