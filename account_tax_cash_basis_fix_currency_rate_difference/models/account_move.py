# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    nbr_diff_moves = fields.Float(
        string='Exchange Diferential', compute="_compute_nbr_diff_moves",
        default=0,)
    account_diff_move_ids = fields.One2many(
        'account.move',
        'diff_move_id',
        string='Account Move',
    )
    diff_move_id = fields.Many2one(
        'account.move',
    )

    @api.multi
    def _compute_nbr_diff_moves(self):
        for rec in self:
            if rec.account_diff_move_ids:
                rec.nbr_diff_moves = len(rec.account_diff_move_ids)

    @api.multi
    def get_difference_entries(self):
        return {
            'name': _('Currency Exchange Difference Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [(
                'diff_move_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False
            }
        }
