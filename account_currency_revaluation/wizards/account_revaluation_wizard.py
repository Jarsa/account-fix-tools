# -*- coding: utf-8 -*-
# Copyright 2017 Jarsa Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountRevaluationWizard(models.TransientModel):
    _name = 'account.revaluation.wizard'

    cutoff_date = fields.Date(
        default=fields.Date.context_today,
        help='Cutoff Date to revaluation',
        required=True,)

    @api.model
    def get_revaluation_balances(self):
        self.ensure_one()
        amls = self.env['account.move.line'].search(
            [('currency_id', '!=', False),
             ('account_id.apply_for_revaluation', '=', True),
             ('date', '<=', self.cutoff_date)],
            order='partner_id')
        balances = [{}, {}]
        errors = []
        for aml in amls:
            partner = str(aml.partner_id.id)
            account = str(aml.account_id.id)
            an_account = False
            if aml.account_id.user_type_id == self.env.ref(
                    "account.data_account_type_liquidity"):
                if account not in balances[1].keys():
                    balances[1][account] = {
                        'balance': aml.balance,
                        'balance_currency': aml.amount_currency,
                    }
                else:
                    balances[1][account]['balance'] += aml.balance
                    balances[1][account]['balance_currency'] += (
                         aml.amount_currency)
                continue
            # We check if the journal has a analytic account
            if aml.journal_id.account_analytic_id:
                an_account = aml.journal_id.account_analytic_id
            elif (aml.journal_id == aml.company_id.
                  currency_exchange_journal_id):
                an_account = (
                    aml.full_reconcile_id.reconciled_line_ids.filtered(
                        lambda r: r.journal_id.type in ['sale', 'purchase'] and
                        r.invoice_id.type in
                        ['in_invoice', 'out_invoice']).mapped(
                            'journal_id.account_analytic_id'))
            if not an_account:
                an_account = aml.move_id.line_ids.filtered(
                    lambda r: r.analytic_account_id).mapped(
                    'analytic_account_id')

            if len(an_account) != 1:
                errors.append(aml.id)
                continue
            else:
                an_account = str(an_account.id)

            if partner not in balances[0].keys():
                balances[0][partner] = {}

            if account not in balances[0][partner].keys():
                balances[0][partner][account] = {}

            if an_account not in balances[0][partner][account].keys():
                balances[0][partner][account][an_account] = {
                    'balance': aml.balance,
                    'balance_currency': aml.amount_currency,
                }
            else:
                balances[0][partner][account][an_account]['balance'] += (
                    aml.balance)
                balances[0][partner][account][an_account][
                    'balance_currency'] += aml.amount_currency
        return balances

    @api.model
    def prepare_lines(self, kwargs):
        partner = False
        if 'partner' in kwargs.keys():
            if kwargs['partner'] != 'False':
                partner = int(kwargs['partner'])
        return {
            'partner_id': partner,
            'journal_id': kwargs['revaluation_journal_id'].id,
            'name': '/',
            'debit': abs(kwargs['amount']) if kwargs['amount'] > 0 else 0,
            'credit': abs(kwargs['amount']) if kwargs['amount'] < 0 else 0,
            'currency_id': kwargs['currency_id'].id,
        }

    @api.model
    def create_lines(self, **kwargs):
        aml_obj = self.env['account.move.line']
        amount_currency = (
            self.env.user.company_id.currency_id.compute(
                abs(kwargs['amount']), kwargs['currency_id']))
        line = self.prepare_lines(kwargs)
        line.update({
            'account_id': int(kwargs['account']),
            'move_id': kwargs['move'].id,
            'amount_currency': (
                -amount_currency if line['debit'] == 0 else
                amount_currency),
            })
        reconcile_line = aml_obj.with_context(
            check_move_validity=False).create(line)
        aml_obj |= reconcile_line
        line = self.prepare_lines(kwargs)
        line.update({
            'account_id': (
                kwargs['ex_journal_id'].default_debit_account_id.id if
                kwargs['amount'] < 0 else
                kwargs['ex_journal_id'].default_credit_account_id.id),
            'move_id': kwargs['move'].id,
            'debit': abs(kwargs['amount']) if kwargs['amount'] < 0 else 0,
            'credit': abs(kwargs['amount']) if kwargs['amount'] > 0 else 0,
            'amount_currency': (
                -amount_currency if line['credit'] == 0 else
                amount_currency),
            })
        if 'an_account' in kwargs.keys():
            line.update({
                'analytic_account_id': int(kwargs['an_account']),
                })
        aml_obj.create(line)

        line = self.prepare_lines(kwargs)
        line.update({
            'account_id': int(kwargs['account']),
            'move_id': kwargs['reversal_move'].id,
            'debit': line['credit'],
            'credit': line['debit'],
            'amount_currency': (
                -amount_currency if line['credit'] == 0 else
                amount_currency),
        })
        reversal_reconcile_line = aml_obj.with_context(
            check_move_validity=False).create(line)
        aml_obj |= reversal_reconcile_line
        line = self.prepare_lines(kwargs)
        line.update({
            'account_id': (
                kwargs['ex_journal_id'].default_debit_account_id.id if
                kwargs['amount'] < 0 else
                kwargs['ex_journal_id'].default_credit_account_id.id),
            'move_id': kwargs['reversal_move'].id,
            'amount_currency': (
                -amount_currency if line['debit'] == 0 else
                amount_currency),
        })
        if 'an_account' in kwargs.keys():
            line.update({
                'analytic_account_id': int(kwargs['an_account']),
                })
        aml_obj.create(line)
        if (not reconcile_line.reconciled and not
                reversal_reconcile_line.reconciled and
                reconcile_line.account_id.user_type_id != self.env.ref(
                    "account.data_account_type_liquidity") and
                reversal_reconcile_line.account_id.user_type_id !=
                self.env.ref("account.data_account_type_liquidity")):
            aml_obj.reconcile()

    @api.multi
    def run_revaluation(self):
        self.ensure_one()
        balances = False
        revaluation_journal_id = (
            self.env.user.company_id.revaluation_journal_id)
        currency_exchange_journal_id = (
            self.env.user.company_id.currency_exchange_journal_id)
        currency_usd = self.env.ref('base.USD').with_context(
            date=self.cutoff_date)
        company_currency = self.env.user.company_id.currency_id
        am_obj = self.env['account.move']
        if not revaluation_journal_id:
            raise ValidationError(
                _('You must configure a revaluation journal in '
                    'the account settings.'))
        if (not currency_exchange_journal_id.default_debit_account_id or not
                currency_exchange_journal_id.default_credit_account_id):
            raise ValidationError(
                _('Error. You must configure a default profit/loss '
                    'accounts into the currency exchange journal.'))
        balances = self.get_revaluation_balances()
        move = am_obj.create({
            'journal_id': revaluation_journal_id.id,
            'date': self.cutoff_date,
            'ref': _('Revaluation of: ' + self.cutoff_date),
            })
        reversal_move = am_obj.create({
            'journal_id': revaluation_journal_id.id,
            'date': fields.Date.to_string(
                (fields.Date.from_string(
                    self.cutoff_date) + timedelta(days=1))),
            'ref': _('Revaluation of: ' + self.cutoff_date + ' (reversal)'),
            })
        for partner, account_data in balances[0].items():
            for account, an_account_data in account_data.items():
                for an_account, amount in an_account_data.items():
                    cutoff_amount = currency_usd.compute(
                        amount['balance_currency'], company_currency)
                    revaluation_amount = round(
                        amount['balance'] - cutoff_amount, 6)
                    if revaluation_amount != 0.0:
                        self.create_lines(
                            ex_journal_id=currency_exchange_journal_id,
                            revaluation_journal_id=revaluation_journal_id,
                            move=move,
                            reversal_move=reversal_move,
                            partner=partner,
                            account=account,
                            an_account=an_account,
                            amount=revaluation_amount,
                            currency_id=currency_usd)
        for account,  amounts in balances[1].items():
            cutoff_amount = currency_usd.compute(
                amount['balance_currency'], company_currency)
            revaluation_amount = round(
                amount['balance'] - cutoff_amount, 6)
            if revaluation_amount != 0.0:
                self.create_lines(
                    ex_journal_id=currency_exchange_journal_id,
                    revaluation_journal_id=revaluation_journal_id,
                    move=move,
                    reversal_move=reversal_move,
                    account=account,
                    amount=revaluation_amount,
                    currency_id=currency_usd)
        move.post()
        reversal_move.post()
        return {
            'name': _('Account Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [(
                'id', 'in', [move.id, reversal_move.id])],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False
            }
        }
