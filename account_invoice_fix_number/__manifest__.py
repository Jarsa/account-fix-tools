# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Accounting - Invoice Fix Number",
    "version": "13.0.0.1.0",
    "category": "Accounting",
    "author": "Jarsa Sistemas,MtNet",
    "website": "https://www.jarsa.com.mx",
    "depends": ["account"],
    "summary": "This module assign a fix number based in the invoice number",
    "license": "AGPL-3",
    "data": [
        'views/account_invoice_view.xml',
    ],
    "installable": True,
}
