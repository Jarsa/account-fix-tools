# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        """This method allow to  compute exchange rate based in invoice_date field
        not from date field."""
        for rec in self:
            date = rec.date
            self.date = self.date_invoice
            total, total_currency, invoice_move_lines = super(
                AccountInvoice, self).compute_invoice_totals(
                    company_currency, invoice_move_lines)
            rec.date = date
        return total, total_currency, invoice_move_lines
