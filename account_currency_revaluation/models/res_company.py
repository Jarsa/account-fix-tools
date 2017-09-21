# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    revaluation_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Revaluation Journal',
        help='This journal will be used for save'
        'the revaluation data',)
