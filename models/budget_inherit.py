# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_utilities.models.utilities import choices_tuple


class BudgetInherit(models.Model):
    _inherit = 'budget.core.budget'

    # CHOICES
    # ----------------------------------------------------------

    # BASIC FIELDS
    # ----------------------------------------------------------

    # RELATIONSHIPS
    # ----------------------------------------------------------
    # cear_ids exist in the Budget Inherit in Capex Module
    # oear_ids exist in the Budget Inherit in Opex Module

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    invoice_ids = fields.One2many('budget.invoice.invoice',
                                  compute='_compute_invoice_ids',
                                  string="Invoices")

    @api.one
    def _compute_invoice_ids(self):
        # TODO ADD INVOICE_IDS TO OEAR THEN ADD TO BELOW
        self.invoice_ids = self.cear_ids.mapped('invoice_ids')