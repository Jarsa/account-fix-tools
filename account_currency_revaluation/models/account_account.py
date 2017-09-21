# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    apply_for_revaluation = fields.Boolean(
        help='If true this account will be used to foreign currency '
        'revaluation',)
