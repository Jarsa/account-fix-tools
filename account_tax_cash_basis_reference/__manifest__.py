# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Accounting - Tax Cash Basis Move Assignation',
    'version': '11.0.1.0.0',
    'category': 'Accounting',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'depends': ['account_cancel'],
    'summary': '''This modules add the partner to the tax
                cash basis journal entries and link it to the invoice
                journal entries.''',
    'license': 'AGPL-3',
    'data': [
        'views/account_move_view.xml',
    ],
}
