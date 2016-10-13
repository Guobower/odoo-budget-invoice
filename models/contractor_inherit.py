# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Contractor(models.Model):
    _inherit = 'res.partner'

    # RELATED FIELDS
    # ----------------------------------------------------------
    # invoice_ids = fields.One2many('budget.invoice',
    #                               related='contract_ids.invoice_ids',
    #                               string="Invoices")

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    total_invoice = fields.Integer(compute='_compute_total_invoice', store=True)
    invoice_ids = fields.One2many('budget.invoice',
                                  'compute_contractor_id',
                                  compute='_compute_invoice_ids',
                                  string="Invoices",
                                  store=True)

    @api.one
    @api.depends('contract_ids.invoice_ids')
    def _compute_total_invoice(self):
        self.total_invoice = len(self.mapped('contract_ids.invoice_ids'))

    @api.one
    @api.depends('contract_ids.invoice_ids')
    def _compute_invoice_ids(self):
        self.invoice_ids = self.mapped('contract_ids.invoice_ids')