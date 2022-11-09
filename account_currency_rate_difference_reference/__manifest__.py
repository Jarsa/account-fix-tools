# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Currency Rate Difference Reference",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "author": "Jarsa Sistemas, Vauxoo",
    "website": "https://www.jarsa.com.mx",
    "depends": ['account_accountant'],
    "summary": """Link currency rate difference moves to the
                  invoice journal entries.""",
    "license": "AGPL-3",
    "data": [
        "views/account_move_view.xml",
    ],
    "installable": True,
}
