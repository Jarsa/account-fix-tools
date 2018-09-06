# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Tax Cash Basis - Fix Currency Rate Difference',
    'version': '11.0.1.0.0',
    'category': 'Accounting',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'depends': ['account_cancel'],
    'summary': (
        'This module add the name of the invoice name'
        ' to the exchange reference journal entry and fix '
        'the currency rate difference with tax cash basis behavior.'),
    'license': 'AGPL-3',
    'data': [
        "views/account_move_view.xml",
    ],
    'installable': True,
}
