# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountFullReconcile(models.Model):
    _inherit = 'account.full.reconcile'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not res.exchange_move_id:
            return res
        origin_move = res.reconciled_line_ids.filtered(
            lambda l: l.account_id.reconcile and l.journal_id.type in
            ['sale', 'purchase'] and l.invoice_id.type in
            ['in_invoice', 'out_invoice']).move_id
        res.exchange_move_id.origin_doc_id = origin_move.id
        return res
