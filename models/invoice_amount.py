# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_utilities.models.utilities import choices_tuple


class InvoiceAmount(models.Model):
    _name = 'budget.invoice.amount'
    _rec_name = 'invoice_id'
    _description = 'Invoice Amount'
    _order = 'sequence'

    # CHOICES
    # ----------------------------------------------------------
    BUDGET_TYPES = choices_tuple(['capex', 'opex', 'revenue'])
    INVOICE_TYPES = choices_tuple(['sicet 2a', 'sicet 2b', 'sicet 3', 'monthly rfq', 'support', 'team based hiring',
                                   'others'])
    PAYMENT_TYPES = choices_tuple(['equipment delivery', 'equipment rfs', 'equipment pac', 'equipment support',
                                   'service', 'progressive', 'completion', 'retention at completion',
                                   'retention at end of maintenance', 'completion at acceptance', 'support harges',
                                   'consultancy', 'training', 'utility charges', 'advance', 'renewal fee',
                                   'access network', 'supply of materials', 'civil works', 'cable works',
                                   'damage case', 'development', 'fdh uplifting', 'fttm activities',
                                   'maintenance work', 'man power', 'mega project', 'migration',
                                   'on demand activities', 'provisioning', 'recharge', 'recovery', 'others'])

    # BASIC FIELDS
    # ----------------------------------------------------------
    budget_type = fields.Selection(BUDGET_TYPES)
    invoice_type = fields.Selection(INVOICE_TYPES)
    payment_type = fields.Selection(PAYMENT_TYPES)

    amount = fields.Monetary(string='Amount', currency_field='company_currency_id')

    # Used for Invoice Summary sequence
    sequence = fields.Integer('Display order')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    company_currency_id = fields.Many2one('res.currency', readonly=True,
                                          default=lambda self: self.env.user.company_id.currency_id)
    invoice_id = fields.Many2one('budget.invoice.invoice',
                              string='Invoice')
