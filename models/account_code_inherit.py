# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_core.models.utilities import choices_tuple


class TaskInherit(models.Model):
    _inherit = 'budget.opex.account.code'

    # CHOICES
    # ----------------------------------------------------------


    # BASIC FIELDS
    # ----------------------------------------------------------


    # RELATIONSHIPS
    # ----------------------------------------------------------
    # company_currency_id already exist in the parent model

    invoice_ids = fields.One2many('budget.invoice.invoice',
                                  'account_code_id',
                                  string="Invoices")

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    utilized_amount = fields.Monetary(currency_field='company_currency_id',
                                      string='Utilized Amount (IM)',
                                      compute='_compute_utilized_amount',
                                      store=True)
    total_invoice =fields.Integer(string='# Invoices', compute='_compute_total_invoice', store=True)

    @api.one
    @api.depends('invoice_ids')
    def _compute_total_invoice(self):
        self.total_invoice = len(self.invoice_ids)

    @api.one
    @api.depends('invoice_ids.certified_invoice_amount', 'invoice_ids.state')
    def _compute_utilized_amount(self):
        invoices = self.env['budget.invoice.invoice'].search([('account_code_id', '=', self.id),
                                           ('state', 'in', ['verified', 'summary generated', 'amount hold',
                                                            'under certification', 'sent to finance', 'closed'])
                                           ])
        self.utilized_amount = sum(invoices.mapped('certified_invoice_amount'))
