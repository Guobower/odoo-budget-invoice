# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Contractor(models.Model):
    _inherit = 'budget.contractor.contractor'

    # TODO TO BE REMOVE
    is_budget_invoice_contractor = fields.Boolean(string='Is Budget Invoice Contractor')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    volume_discount_ids = fields.One2many('budget.invoice.volume.discount',
                                          'contractor_id',
                                          string="Volume Discounts")

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    total_invoice = fields.Integer(compute='_compute_total_invoice', store=True)
    # TODO RENAME TO INVOICE
    contractor_invoice_ids = fields.One2many('budget.invoice.invoice',
                                             compute='_compute_invoice_ids',
                                             string="Invoices"
                                             )

    @api.one
    @api.depends('contract_ids.invoice_ids')
    def _compute_total_invoice(self):
        self.total_invoice = len(self.mapped('contract_ids.invoice_ids'))

    @api.one
    @api.depends('contract_ids.invoice_ids')
    def _compute_invoice_ids(self):
        self.contractor_invoice_ids = self.mapped('contract_ids.invoice_ids')
