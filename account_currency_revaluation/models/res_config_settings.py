# -*- coding: utf-8 -*-
# Copyright 2016 Jarsa Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        required=True,)
    revaluation_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Revaluation Journal',
        help='This journal will be used for save'
        'the revaluation data',
        compute="_get_revaluation_journal_id",
        inverse="_set_revaluation_journal_id",)

    @api.multi
    @api.depends('company_id')
    def _get_revaluation_journal_id(self):
        for rec in self:
            rec.revaluation_journal_id = (
                rec.company_id.revaluation_journal_id.id)

    @api.multi
    def _set_revaluation_journal_id(self):
        for rec in self:
            if(rec.revaluation_journal_id !=
               rec.company_id.revaluation_journal_id):
                rec.company_id.revaluation_journal_id = (
                    rec.revaluation_journal_id.id)
