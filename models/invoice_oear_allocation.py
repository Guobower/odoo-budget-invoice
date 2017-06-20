# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_utilities.models.utilities import choices_tuple


class OearAllocation(models.Model):
    _name = 'budget.invoice.oear.allocation'
    _rec_name = 'invoice_id'
    _description = 'Invoice Task Allocation'
    _order = 'sequence'

    # CHOICES
    # ----------------------------------------------------------

    # BASIC FIELDS
    # ----------------------------------------------------------
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id')

    # Used for Invoice Summary sequence
    sequence = fields.Integer('Display order')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    company_currency_id = fields.Many2one('res.currency', readonly=True,
                                          default=lambda self: self.env.user.company_id.currency_id)
    invoice_id = fields.Many2one('budget.invoice.invoice',
                              string='Invoice')
    oear_id = fields.Many2one('budget.opex.oear',
                              string='OEAR',
                              domain="[('state','=','authorized')]")

    cost_center_id = fields.Many2one('budget.core.cost.center', string='Cost Center')
    account_code_id = fields.Many2one('budget.core.account.code', string='Account Code')

    # RELATED FIELDS
    # ----------------------------------------------------------
    related_accrued_amount = fields.Monetary(string='Accrued Amount',
                                             related='oear_id.operation_id.accrued_amount',
                                             currency_field='company_currency_id')
