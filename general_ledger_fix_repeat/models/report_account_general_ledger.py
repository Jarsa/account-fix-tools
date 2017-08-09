# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class report_account_general_ledger(models.AbstractModel):
    _inherit = "account.general.ledger"
    _description = "General Ledger Report"

    @api.multi
    def group_by_account_id(self, line_id):
        accounts = super(
            report_account_general_ledger, self).group_by_account_id(line_id)
        for account, value in accounts.items():
            accounts[account]['lines'] = set(value['lines'])
        return accounts
