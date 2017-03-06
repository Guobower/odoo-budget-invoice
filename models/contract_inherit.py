# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Contract(models.Model):
    _inherit = 'budget.contractor.contract'

    # RELATIONSHIPS
    # ----------------------------------------------------------
    invoice_ids = fields.One2many('budget.invoice.invoice',
                                  'contract_id',
                                  string="Invoices")
    volume_discount_ids = fields.One2many('budget.invoice.volume.discount',
                                          'contract_id',
                                          string="Volume Discounts")
