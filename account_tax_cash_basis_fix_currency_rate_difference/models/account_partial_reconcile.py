# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division

from odoo import _, api, models


class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    @api.model
    def create_exchange_rate_entry(
            self, aml_to_fix, amount_diff, diff_in_currency, currency, move):
        """
        Method inherited to fix the tax currency exchange difference.
        Originally Odoo only transfer the invoice taxes with the currency rate
        at invoice date, so, we must fix the currency exchange difference
        of the translated taxes

        :param aml_to_fix: recordset of account.move.line (possible several
            but sharing the same currency)
        :param amount_diff: float. Amount in company currency to fix
        :param diff_in_currency: float. Amount in foreign currency `currency`
            to fix
        :param currency: res.currency
        :param move: account.move
        :return: tuple.
            [0]: account.move.line created to balance the `aml_to_fix`
            [1]: recordset of account.partial.reconcile created between the
                tuple first element and the `aml_to_fix`
        """
        created_lines, partial_rec = super().create_exchange_rate_entry(
            aml_to_fix, amount_diff, diff_in_currency, currency, move)
        exchange_journal = move.company_id.currency_exchange_journal_id
        company_currency = move.company_id.currency_id
        amount_diff = company_currency.round(amount_diff)
        diff_in_currency = currency and currency.round(diff_in_currency) or 0

        for aml in created_lines:
            diff_move = aml.move_id
            # We get the invoice and the payment move
            invoice_move = (
                self.credit_move_id.move_id if
                self.credit_move_id.journal_id.type == 'purchase' else
                self.debit_move_id.move_id)
            payment_move = (
                self.debit_move_id.move_id if
                self.credit_move_id.journal_id.type == 'purchase' else
                self.credit_move_id.move_id)
            lines = []
            invoice_taxes = invoice_move.line_ids.filtered(
                'tax_ids').mapped('tax_ids').filtered(
                lambda t: t.tax_exigibility == 'on_payment')

            # We loop the tax lines of the invoice move to get the tax rate
            for tax in invoice_taxes.filtered(lambda t: t.amount != 0.0):
                # We check if the move will be a amount_currency fix
                # if this is True we compute the currency amount
                # to the correspinding currency.
                if diff_in_currency != 0 and amount_diff == 0:
                    amount_diff = (
                        currency.with_context(date=payment_move.date).compute(
                            diff_in_currency, company_currency))
                # We get the tax difference based in the base amount
                tax_amount_diff = company_currency.round(
                    (amount_diff /
                     (abs(tax.amount) * .01 + 1) * (abs(tax.amount) * .01))
                    )
                # We create the tax counterpart
                lines.append((0, 0, {
                    'name': (
                        _('Currency exchange rate difference for: %s') % (
                            tax.name)),
                    'debit': (
                        tax_amount_diff < 0 and -tax_amount_diff or 0.0),
                    'credit': (
                        tax_amount_diff > 0 and tax_amount_diff or 0.0),
                    'account_id': tax.cash_basis_account.id,
                    'move_id': diff_move.id,
                    'currency_id': currency.id,
                    'partner_id': self.debit_move_id.partner_id.id,
                }))
                # We create the gain / loss counterpart
                lines.append((0, 0, {
                    'name': (
                        _('Currency exchange rate difference for: %s') % (
                            tax.name)),
                    'debit': (
                        tax_amount_diff > 0 and tax_amount_diff or 0.0),
                    'credit': (
                        tax_amount_diff < 0 and -tax_amount_diff or 0.0),
                    'account_id': (
                        tax_amount_diff > 0 and
                        exchange_journal.default_debit_account_id.id or
                        exchange_journal.default_credit_account_id.id),
                    'move_id': diff_move.id,
                    'currency_id': currency.id,
                    'partner_id': self.debit_move_id.partner_id.id,
                }))
            gain_loss_line = aml.move_id.line_ids.filtered(
                lambda l: not l.account_id.reconcile)
            lines.append((1, gain_loss_line.id, {
                'tax_ids': [(6, 0, invoice_taxes.ids)],
            }))
            diff_move.button_cancel()
            diff_move.write({
                'line_ids': [x for x in lines],
                'ref': invoice_move.name,
                'diff_move_id': invoice_move.id,
            })
            diff_move.post()
        return created_lines, partial_rec
