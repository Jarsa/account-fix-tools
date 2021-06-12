# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"

    @api.model
    def _get_options(self, previous_options=None):
        options = super()._get_options(previous_options=previous_options)
        options['currencies'] = self.env['res.currency'].search([]).read(['name'])
        return options
