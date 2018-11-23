# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"

    @api.multi
    def unlink(self):
        """ When removing a payment reconciliation, also unlink its full
        reconciliation if it exists.
        This Method will un-post and delete the journal entry from the currency
        exchange journal entry
        """
        for rec in self:
            skip_reversal = (
                self.env.user.company_id.
                skip_currency_exchange_difference_reversal)
            if rec.exchange_move_id and skip_reversal:
                rec.exchange_move_id.button_cancel()
                rec.exchange_move_id.unlink()
        return super().unlink()
