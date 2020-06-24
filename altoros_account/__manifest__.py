# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Altoros: Accounting',
    'summary': 'Altoros: Accounting',
    'category': 'Accounting',
    "author": "Novobi",
    "website": "https://www.novobi.com/",
    'depends': [
        'account_accountant',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    "application": False,
    "installable": True,
}
