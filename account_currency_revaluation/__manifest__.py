# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Currency Revaluation',
    'summary': '''
        Revaluates the foreign currency balance
        ''',
    'version': '10.0.1.0.0',
    'category': 'Account',
    'website': 'https://www.jarsa.com.mx/',
    'author': 'Jarsa Sistemas',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'account',
    ],
    'data': [
        'wizards/account_revaluation_wizard_view.xml',
        'views/account_account_revaluation_view.xml',
        'views/res_config_settings_view.xml',
    ],
}
