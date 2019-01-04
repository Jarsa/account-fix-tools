# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _


class AccountFiscalYearWizard(models.TransientModel):
    _name = 'account.fiscalyear.close.wizard'

    date_start = fields.Date(
        default=lambda self: self.get_date_start(),
        required=True,)
    date_end = fields.Date(
        default=lambda self: self.get_date_end(),
        required=True,)
    account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account",
        required=True,
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Journal",
        domain=[('type', '=', 'general')],
        required=True,
    )

    @api.model
    def get_date_start(self):
        return str(fields.date.today().year - 1) + "-01-01"

    @api.model
    def get_date_end(self):
        return str(fields.date.today().year - 1) + "-12-31"

    @api.model
    def _get_account_balances_query(self):
        return """
            SELECT aml.account_id, aac.name, ROUND(SUM(balance), 2) AS balance,
                   aac.user_type_id
            FROM account_move_line aml
            JOIN account_account aac ON aml.account_id = aac.id
            JOIN account_move am ON am.id = aml.move_id
            WHERE aml.date BETWEEN %s AND %s
            AND aac.user_type_id IN (12, 13, 14, 15, 16, 17)
            AND aml.company_id = %s
            AND am.state = 'posted'
            GROUP BY aml.account_id, aac.name, aac.user_type_id;
            """, (self.date_start, self.date_end, self.env.user.company_id.id)

    @api.model
    def get_account_balances(self):
        query, params = self._get_account_balances_query()
        self._cr.execute(query, params)
        return self._cr.dictfetchall()

    @api.model
    def prepare_am(self):
        return {
            'journal_id': self.journal_id.id,
            'date': self.date_end,
            'ref': _("%s Year-ending's Journal Entry") % (
                fields.date.today().year - 1)
        }

    @api.model
    def prepare_aml(self, item, move_id):
        return {
            'name': item['name'] + ': ' + str(
                fields.Date.from_string(self.date_end).year),
            'debit': abs(item['balance']) if item['balance'] < 0.0 else 0.0,
            'credit': abs(item['balance']) if item['balance'] > 0.0 else 0.0,
            'move_id': move_id.id,
            'account_id': item['account_id'],
        }

    @api.multi
    def get_years_ending_entry(self):
        self.ensure_one()
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        move = am_obj.create(self.prepare_am())
        data = self.get_account_balances()
        for item in data:
            root_aml = aml_obj.with_context(check_move_validity=False).create(
                self.prepare_aml(item, move))
            root_aml.copy({
                'account_id': self.account_id.id,
                'debit': root_aml.credit,
                'credit': root_aml.debit,
            })
        move.post()
        return {
            'name': _('Year Endings Account Move(s)'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': move.id,
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
            }
        }
