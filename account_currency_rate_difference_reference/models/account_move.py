# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    exchange_move_id = fields.Many2one(
        'account.move',
        string='Currency Exchange Difference Move',
    )

    def action_currency_rate_diference(self):
        return {
            'name': _('Currency Exchange Difference Move'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.exchange_move_id.id,
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False
            }
        }
