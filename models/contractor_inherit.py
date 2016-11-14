# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Contractor(models.Model):
    _inherit = 'res.partner'

    is_budget_invoice_contractor = fields.Boolean(string='Is Budget Invoice Contractor')

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    total_invoice = fields.Integer(compute='_compute_total_invoice', store=True)
    contractor_invoice_ids = fields.One2many('budget.invoice',
                                             compute='_compute_invoice_ids',
                                             string="Invoices"
                                             )

    @api.one
    @api.depends('contractor_contract_ids.invoice_ids')
    def _compute_total_invoice(self):
        self.total_invoice = len(self.mapped('contractor_contract_ids.invoice_ids'))

    @api.one
    @api.depends('contractor_contract_ids.invoice_ids')
    def _compute_invoice_ids(self):
        self.contractor_invoice_ids = self.mapped('contractor_contract_ids.invoice_ids')