# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountFiscalYearWizard(models.TransientModel):
    _inherit = 'account.fiscalyear.close.wizard'

    @api.model
    def _get_account_balances_query(self):
        query, params = super(
            AccountFiscalYearWizard, self)._get_account_balances_query()
        query = """
            SELECT aml.account_id, aac.name, ROUND(SUM(balance), 2) AS balance,
                   aac.user_type_id, aml.analytic_account_id
            FROM account_move_line aml
            JOIN account_account aac ON aml.account_id = aac.id
            JOIN account_move am ON am.id = aml.move_id
            WHERE aml.date BETWEEN %s AND %s
            AND aac.user_type_id IN (12, 13, 14, 15, 16, 17)
            AND aml.company_id = %s
            AND am.state = 'posted'
            GROUP BY aml.account_id, aac.name, aac.user_type_id,
                aml.analytic_account_id;
            """
        return query, params

    @api.model
    def prepare_aml(self, item, move_id):
        res = super(AccountFiscalYearWizard, self).prepare_aml(item, move_id)
        res['analytic_account_id'] = item['analytic_account_id']
        return res
