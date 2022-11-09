# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_cash_basis_move_ids = fields.One2many(
        'account.move',
        'origin_move_id',
        string='Tax Move(s)',
    )
    origin_move_id = fields.Many2one(
        'account.move',
        string='Origin Move',
        help='Original Journal Entry from which this move was created.',
    )
    tax_cash_basis_moves_count = fields.Integer(
        string='Currency Exchange Move(s)',
        compute='_compute_tax_cash_basis_moves_count',)

    @api.depends('tax_cash_basis_move_ids')
    def _compute_tax_cash_basis_moves_count(self):
        for rec in self:
            rec.tax_cash_basis_moves_count = len(
                rec.tax_cash_basis_move_ids)

    def action_tax_cash_basis_moves(self):
        return {
            'name': _('Tax Move(s)'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [(
                'origin_move_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False
            }
        }
