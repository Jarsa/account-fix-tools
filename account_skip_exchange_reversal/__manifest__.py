# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Skip Exchange Reversal",
    "version": "13.0.1.0.0",
    "category": "Accounting",
    "author": "Jarsa Sistemas,Vauxoo,MtNet",
    "website": "https://www.jarsa.com.mx",
    "depends": ["account_cancel"],
    "summary": "This module avoid the reversal journal entries creation.",
    "license": "AGPL-3",
    "data": [
        "views/res_config_settings_views.xml",
    ]
}
