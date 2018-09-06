# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    nbr_tax_moves = fields.Integer(
        string='Tax Moves', compute="_compute_nbr_tax_moves",
        default=0, oldname='nbr_moves',)
    tax_move_ids = fields.One2many(
        'account.move',
        'invoice_move_id',
        string='Tax Journal Entries',
        oldname='account_move_ids',
        help='Field to link the tax journal entries '
             'with the invoice journal entry.',
    )
    invoice_move_id = fields.Many2one(
        'account.move',
        string='Invoice Journal Entry',
        oldname='move_id',
        help='Field to link the invoice journal entry with the tax journal'
        ' entry.'
    )

    @api.multi
    def _compute_nbr_tax_moves(self):
        for rec in self:
            if rec.tax_move_ids:
                rec.nbr_tax_moves = len(rec.tax_move_ids)

    @api.multi
    def _reverse_move(self, date=None, journal_id=None):
        if self.tax_cash_basis_rec_id:
            date = (
                self.tax_cash_basis_rec_id.debit_move_id.date if
                self.tax_cash_basis_rec_id.debit_move_id
                .journal_id.type in ['bank', 'cash'] else
                self.tax_cash_basis_rec_id.credit_move_id.date)
        return super()._reverse_move(date, journal_id)

    @api.multi
    def get_tax_journal_entries(self):
        return {
            'name': _('Tax Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [(
                'invoice_move_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
            }
        }
