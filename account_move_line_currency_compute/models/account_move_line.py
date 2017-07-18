# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('currency_id', 'amount_currency')
    def _onchange_currency_id_amount_currency(self):
        if self.currency_id:
            amount = (
                self.currency_id.with_context(date=self.move_id.date).compute(
                    self.amount_currency, self.move_id.company_id.currency_id))
            self.update({
                'debit': abs(amount) if amount > 0.0 else 0.0,
                'credit': abs(amount) if amount < 0.0 else 0.0,
            })
