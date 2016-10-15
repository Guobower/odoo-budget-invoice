# -*- coding: utf-8 -*-
{
    'name': "Invoice",
    'version': '0.1',
    'summary': 'Invoice Management',
    'sequence': 3,
    'description': """
Odoo Module
===========
Specifically Designed for Etisalat-TBPC

Invoice Management
---------------------
- Invoice
- Contract Inherit
- Contractor Inherit
    """,
    'author': "Marc Philippe de Villeres",
    'website': "https://github.com/mpdevilleres",
    'category': 'TBPC Budget',
    'depends': ['budget_contractor'],
    'data': [
        'views/invoice.xml',
        'views/contractor_inherit.xml',
        'views/menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
