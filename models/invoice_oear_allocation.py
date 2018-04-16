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
    amount = fields.Monetary(string='Amount', currency_field='currency_id')

    # Used for Invoice Summary sequence
    sequence = fields.Integer('Display order')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    currency_id = fields.Many2one('res.currency', readonly=False, required=False,
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'AED')],
                                                                                       limit=1))
    currency_aed_id = fields.Many2one('res.currency', readonly=True,
                                      default=lambda self: self.env['res.currency'].search([('name', '=', 'AED')],
                                                                                           limit=1))
    invoice_id = fields.Many2one('budget.invoice.invoice',
                                 string='Invoice')
    oear_id = fields.Many2one('budget.opex.oear',
                              string='OEAR',
                              domain="[('state','=','authorized')]")

    cost_center_id = fields.Many2one('budget.core.cost.center', string='Cost Center')
    account_code_id = fields.Many2one('budget.core.account.code', string='Account Code')

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    amount_aed = fields.Monetary(string='Amount (AED)', compute='_compute_amount_aed', store=True,
                                 currency_field='currency_aed_id')

    @api.one
    @api.depends('currency_id', 'amount')
    def _compute_amount_aed(self):
        if self.currency_id.name == 'AED':
            self.amount_aed = self.amount
        else:
            self.amount_aed = self.amount if not self.currency_id.rate else self.amount / self.currency_id.rate

    # RELATED FIELDS
    # ----------------------------------------------------------
    related_accrued_amount = fields.Monetary(string='Accrued Amount',
                                             related='oear_id.operation_id.accrued_amount',
                                             currency_field='currency_id')
