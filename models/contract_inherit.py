# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_utilities.models.utilities import num_to_shorthand

class Contract(models.Model):
    _inherit = 'budget.contractor.contract'

    # RELATIONSHIPS
    # ----------------------------------------------------------
    invoice_ids = fields.One2many('budget.invoice.invoice',
                                  'contract_id',
                                  string="Invoices")

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    # company_currency_id exist in the main contract model
    invoice_count = fields.Integer(string="Invoice Count",
                                   compute='_compute_invoice_count',
                                   store=True
                                   )
    total_invoice_amount = fields.Monetary(currency_field='company_currency_id',
                                           compute='_compute_total_invoice_amount',
                                           string='Total Certified Amount',
                                           store=True)

    total_invoice_amount_shorthand = fields.Char(compute='_compute_total_invoice_amount_shorthand',
                                                 string='Total Certified Amount',
                                                 store=True)

    @api.one
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        self.invoice_count = len(self.invoice_ids)

    @api.one
    @api.depends('invoice_ids', 'invoice_ids.certified_invoice_amount', 'invoice_ids.state')
    def _compute_total_invoice_amount(self):
        states = ['verified', 'summary generated',
                  'under certification', 'sent to finance', 'closed']
        invoice_ids = self.invoice_ids.filtered(lambda r: r.state in states)
        self.total_invoice_amount = sum(invoice_ids.mapped('certified_invoice_amount'))

    @api.one
    @api.depends('total_invoice_amount')
    def _compute_total_invoice_amount_shorthand(self):
        if not self.total_invoice_amount:
            return
        self.total_invoice_amount_shorthand = num_to_shorthand(self.total_invoice_amount)
