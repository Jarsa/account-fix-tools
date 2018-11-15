# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    currency_rate_difference_move_ids = fields.One2many(
        'account.move',
        'origin_doc_id',
        string=' Currency Exchange Move(s)',
    )
    currency_rate_moves_count = fields.Integer(
        string='Currency Exchange Move(s)',
        compute='_compute_currency_rate_moves_count',)
    origin_doc_id = fields.Many2one(
        'account.move',
        string='Origin Document Move',
        help='Original Journal Entry from which this move was created.',
    )

    @api.depends('currency_rate_difference_move_ids')
    def _compute_currency_rate_moves_count(self):
        for rec in self:
            rec.currency_rate_moves_count = len(
                rec.currency_rate_difference_move_ids)

    @api.multi
    def action_currency_rate_diference(self):
        return {
            'name': _('Currency Exchange Difference Move(s)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [(
                'origin_doc_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False
            }
        }
