# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division

from odoo import _, models


class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    def _fix_multiple_exchange_rates_diff(
            self, aml_to_fix, amount_diff, diff_in_currency,
            currency, move_date):
        for rec in self:
            move_lines, partial_reconciles = (
                super(AccountPartialReconcileCashBasis,
                      self)._fix_multiple_exchange_rates_diff(
                    aml_to_fix, amount_diff, diff_in_currency,
                    currency, move_date))
            for aml in move_lines:
                diff_move = aml.move_id
                # We get the invoice and the payment move
                invoice_move = (
                    rec.credit_move_id if
                    rec.credit_move_id.journal_id.type == 'purchase' else
                    rec.debit_move_id)
                bank_move = (
                    rec.debit_move_id.move_id if
                    rec.credit_move_id.journal_id.type == 'purchase' else
                    rec.credit_move_id)
                lines = []
                # We loop the tax lines of the invoice move to get the tax rate
                for tax in invoice_move.move_id.line_ids.filtered(
                        lambda r: r.tax_line_id.use_cash_basis).mapped(
                        "tax_line_id"):
                    # We check if the move will be a amount_currency fix
                    # if this is True we compute the currency amount
                    # to the correspinding currency.
                    if diff_in_currency != 0 and amount_diff == 0:
                        amount_diff = (
                            currency.with_context(date=bank_move.date).compute(
                                diff_in_currency, rec.company_currency_id))
                    # We get the tax difference based in the base amount
                    tax_amount_diff = (
                        (amount_diff /
                         (abs(tax.amount) * .01 + 1) * (abs(tax.amount) * .01))
                        )
                    # We create the tax counterpart
                    lines.append((0, 0, {
                        'name': (
                            _('Currency exchange rate difference for: ' +
                              tax.name)),
                        'debit': (
                            tax_amount_diff < 0 and -tax_amount_diff or 0.0),
                        'credit': (
                            tax_amount_diff > 0 and tax_amount_diff or 0.0),
                        'account_id': tax.cash_basis_account.id,
                        'move_id': diff_move.id,
                        'currency_id': currency.id,
                        'partner_id': rec.debit_move_id.partner_id.id,
                    }))
                    # We create the gain / loss counterpart
                    lines.append((0, 0, {
                        'name': (
                            _('Currency exchange rate difference for: ' +
                              tax.name)),
                        'debit': (
                            tax_amount_diff > 0 and tax_amount_diff or 0.0),
                        'credit': (
                            tax_amount_diff < 0 and -tax_amount_diff or 0.0),
                        'account_id': (
                            tax_amount_diff > 0 and
                            rec.company_id.currency_exchange_journal_id.
                            default_debit_account_id.id or
                            rec.company_id.currency_exchange_journal_id.
                            default_credit_account_id.id),
                        'move_id': diff_move.id,
                        'currency_id': currency.id,
                        'partner_id': rec.debit_move_id.partner_id.id,
                    }))
                diff_move.button_cancel()
                diff_move.write({
                    'line_ids': [x for x in lines],
                    'ref': invoice_move.move_id.name,
                    'diff_move_id': invoice_move.move_id.id,
                })
                diff_move.post()
        return move_lines, partial_reconciles
