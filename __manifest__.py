# -*- coding: utf-8 -*-
{
    'name': "Invoice",
    'version': '0.1',
    'summary': 'Invoice Management',
    'sequence': 6,
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
                'budget_contractor',
                'budget_purchase_order',
                'budget_capex',
                'budget_opex',
                'budget_signature',
                ],
    'external_dependencies': {
        'python': ['openpyxl']
    },
    'data': [
        'security/budget_invoice.xml',
        'security/ir.model.access.csv',

        'workflow/invoice.xml',
        'workflow/invoice_summary.xml',

        'views/res_currency_rate.xml',

        'views/invoice.xml',
        'views/invoice_summary.xml',
        'views/project_estimated_cost.xml',
        'views/contract_inherit.xml',
        'views/purchase_order_inherit.xml',
        'views/discount_rule_inherit.xml',
        'views/cear_inherit.xml',
        'views/oear_inherit.xml',
        'views/budget_inherit.xml',

        'views/cear_allocation_bi.xml',

        'views/menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
