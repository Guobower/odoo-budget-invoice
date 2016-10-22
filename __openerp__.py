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
    'depends': ['document',
                'budget_contractor'],
    'external_dependencies': {
        'python': ['openpyxl']
    },
    'data': [
        'security/budget_invoice.xml',
        'security/ir.model.access.csv',

       'workflow/invoice.xml',
        'workflow/invoice_summary.xml',

        'views/invoice.xml',
        'views/invoice_summary.xml',
        'views/task.xml',
        'views/contractor_inherit.xml',
        'views/menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
