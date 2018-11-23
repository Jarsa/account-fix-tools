# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    skip_currency_exchange_difference_reversal = fields.Boolean(
        string='Avoid Reversal of Currency Exchange Difference Journal Entry',
        help='This feature avoids the creation of a reversal Journal Entry'
        ' for Currency Exchange Difference when a Payment is'
        'unreconciled from an invoice. '
        'If Lock Dates are set a Warning will be raised otherwise Currency '
        'Exchange Journal Entry will be deleted.',
        readonly=False)
