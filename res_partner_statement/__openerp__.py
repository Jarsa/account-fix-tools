# -*- coding: utf-8 -*-
# © 2016 Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Partner Statement",
    "summary": "Description",
    "version": "9.0.1.0.0",
    "category": "Hidden",
    "website": "https://www.jarsa.com.mx/",
    "author": "JARSA Sistemas, S.A. de C.V.",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        'report',
        'account_accountant',
        'sale',
        'stock',
    ],
    "data": [
        'wizard/partner_statement_wizard_view.xml',
        'views/config_report.xml',
        'report/partner_statement_report_template.xml',
    ],
    "demo": [
    ]
}
