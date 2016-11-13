# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IrAttachment(models.Model):
    # Inherit in Filestore
    _inherit = 'ir.attachment'

    # BASIC FIELDS
    # ----------------------------------------------------------
    is_invoice_summary = fields.Boolean(string="Is Invoice Summary")

    # RELATIONSHIPS
    # ----------------------------------------------------------
    invoice_summary_id = fields.Many2one('budget.invoice.summary', string="Invoice Summary")
