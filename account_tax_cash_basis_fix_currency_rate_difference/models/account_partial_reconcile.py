# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division

from odoo import _, models


class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    def _fix_multiple_exchange_rates_diff(
            self, aml_to_fix, amount_diff, diff_in_currency, currency,
            move_date):
        for rec in self:
            line_to_reconcile, partial_rec = (
                super(AccountPartialReconcileCashBasis,
                      self)._fix_multiple_exchange_rates_diff(
                    aml_to_fix, amount_diff, diff_in_currency,
                    currency, move_date))
            move = self.env['account.move.line'].browse(
                line_to_reconcile.id).move_id
            # We get the invoice and the payment move
            invoice_move = (
                rec.credit_move_id if
                rec.credit_move_id.journal_id.type == 'purchase' else
                rec.debit_move_id)
            bank_move = (
                rec.debit_move_id if
                rec.credit_move_id.journal_id.type == 'purchase' else
                rec.credit_move_id)
            lines = []

            # We check if the move will be a amount_currency fix
            # if this is True we compute the currency amount
            # to the correspinding currency.
            if diff_in_currency != 0 and amount_diff == 0:
                amount_diff = (
                    currency.with_context(date=bank_move.date).compute(
                        diff_in_currency, rec.company_currency_id))
            diff_factor = amount_diff

            root_amount = (
                invoice_move.debit if invoice_move.debit > 0.0
                else invoice_move.credit)
            an_lines = self.env['account.move.line'].read_group(
                [('move_id', '=', invoice_move.move_id.id),
                 ('analytic_account_id', '!=', False)],
                ['debit', 'credit', 'analytic_account_id'],
                'analytic_account_id', lazy=False)
            total_lines = len(an_lines)
            data = []
            if total_lines > 0:
                for aml in move.line_ids:
                    if not aml.account_id.reconcile:
                        lines.append((2, aml.id))

            for an_line in an_lines:
                tax_rate = sum(
                    invoice_move.move_id.line_ids.filtered(
                        lambda r: r.tax_line_id).mapped(
                        'tax_line_id').mapped('amount')) / 100
                an_amount = (
                    an_line['debit']
                    if invoice_move.credit > 0.0
                    else an_line['credit'])
                an_percentage = round(
                    ((an_amount + (an_amount * tax_rate)) * 100) /
                    root_amount)
                diff_factor = (amount_diff * (an_percentage / 100))
                data.append(diff_factor)
                # We create the gain / loss counterpart
                lines.append((0, 0, {
                    'name': _(
                        'Currency exchange rate difference'),
                    'debit': (
                        diff_factor > 0 and diff_factor or 0.0),
                    'credit': (
                        diff_factor < 0 and -diff_factor or 0.0),
                    'account_id': (
                        diff_factor > 0 and
                        rec.company_id.currency_exchange_journal_id.
                        default_debit_account_id.id or
                        rec.company_id.currency_exchange_journal_id.
                        default_credit_account_id.id),
                    'move_id': move.id,
                    'currency_id': currency.id,
                    'partner_id': rec.debit_move_id.partner_id.id,
                    'analytic_account_id': an_line['analytic_account_id'][0],
                }))

            if total_lines == 0:
                total_lines = 1
                data.append(diff_factor)
            # We loop the tax lines of the invoice move to get the tax rate
            # We get the tax difference based in the base amount
            refund = self.env['account.invoice'].search([
                ('move_id', '=', bank_move.move_id.id)])
            if refund.type in ['out_refund', 'in_refund']:
                for tax in invoice_move.move_id.line_ids.filtered(
                        lambda r: r.tax_line_id.use_cash_basis).mapped(
                        "tax_line_id"):
                    for index in range(total_lines):
                        tax_amount_diff = (
                            (data[index] /
                             (abs(tax.amount) * .01 + 1) * (
                                abs(tax.amount) * .01)))
                        # We create the tax counterpart
                        lines.append((0, 0, {
                            'name': _(
                                'Currency exchange rate difference for: ' +
                                tax.name),
                            'debit': (
                                tax_amount_diff > 0 and tax_amount_diff or
                                0.0),
                            'credit': (
                                tax_amount_diff < 0 and -tax_amount_diff or
                                0.0),
                            'account_id': tax.cash_basis_account.id,
                            'move_id': move.id,
                            'currency_id': currency.id,
                            'partner_id': rec.debit_move_id.partner_id.id,
                        }))
                        # We create the gain / loss counterpart
                        lines.append((0, 0, {
                            'name': _(
                                'Currency exchange rate difference for: ' +
                                tax.name),
                            'debit': (
                                tax_amount_diff < 0 and -tax_amount_diff or
                                0.0),
                            'credit': (
                                tax_amount_diff > 0 and tax_amount_diff or
                                0.0),
                            'account_id': (
                                tax_amount_diff > 0 and
                                rec.company_id.currency_exchange_journal_id.
                                default_debit_account_id.id or
                                rec.company_id.currency_exchange_journal_id.
                                default_credit_account_id.id),
                            'move_id': move.id,
                            'currency_id': currency.id,
                            'partner_id': rec.debit_move_id.partner_id.id,
                            'analytic_account_id': (
                                an_lines[index]['analytic_account_id'][0]),
                        }))
            move.button_cancel()
            move.write({
                'line_ids': [x for x in lines],
                'ref': invoice_move.move_id.name,
                'diff_move_id': invoice_move.move_id.id,
            })
            move.post()
        return line_to_reconcile, partial_rec
