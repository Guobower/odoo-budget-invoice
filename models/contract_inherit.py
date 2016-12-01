# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Contract(models.Model):
    _inherit = 'budget.contractor.contract'

    # RELATIONSHIPS
    # ----------------------------------------------------------
    invoice_ids = fields.One2many('budget.invoice.invoice',
                                  'contract_id',
                                  string="Invoices")

