# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    @api.model
    def create_exchange_rate_entry(self, aml_to_fix, move):
        created_lines, partial_rec = super().create_exchange_rate_entry(
            aml_to_fix, move)
        partial = self.env['account.partial.reconcile'].search(
            ['|',
                '&', ('debit_move_id', '=', aml_to_fix.id),
                     ('credit_move_id.invoice_id', '!=', False),
                '&', ('credit_move_id', '=', aml_to_fix.id),
                     ('debit_move_id.invoice_id', '!=', False)], limit=1)
        for aml in created_lines:
            origin_move = (
                partial.credit_move_id.invoice_id and
                partial.credit_move_id.move_id or
                partial.debit_move_id.move_id)
            move.button_cancel()
            move.write({
                'ref': origin_move.name,
                'origin_doc_id': origin_move.id,
            })
            move.post()
        return created_lines, partial_rec
