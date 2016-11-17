# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Contract(models.Model):
    _inherit = 'budget.contract'

    # RELATIONSHIPS
    # ----------------------------------------------------------
    invoice_ids = fields.One2many('budget.invoice',
                                  'contract_id',
                                  string="Invoices")

