# Copyright 2017, Jarsa Sistemas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_currency_rate_date(self):
        return self.date_invoice
