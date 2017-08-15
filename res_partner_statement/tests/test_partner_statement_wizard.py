# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.tools.translate import _


class TestPartnerStatementWizard(TransactionCase):

    def setUp(self):
        super(TestPartnerStatementWizard, self).setUp()
        self.wiz_partner_statement = self.env['partner.statement.wizard']
        self.partner_ids = self.env.ref("base.res_partner_12")

    def test_10_res_partner_statement_get_types(self):
        value = self.wiz_partner_statement.with_context(
            active_model='res.partner',
            active_ids=[self.partner_ids.id]).get_types()
        self.assertEqual(
            value, [
                ('out_invoice', 'Cliente'),
                ('in_invoice', 'Proveedor')],
            'incorrect')
