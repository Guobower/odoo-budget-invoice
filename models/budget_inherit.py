# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_core.models.utilities import choices_tuple


class BudgetInherit(models.Model):
    _inherit = 'budget.core.budget'

    # CHOICES
    # ----------------------------------------------------------

    # BASIC FIELDS
    # ----------------------------------------------------------

    # RELATIONSHIPS
    # ----------------------------------------------------------
    # cear_ids exist in the Budget Inherit in Capex Module

    # COMPUTE FIELDS
    # ----------------------------------------------------------
#     invoice_ids = fields.One2many('budget.invoice.invoice',
# #                                  compute='_compute_invoice_ids',
#                                   string="Invoices")

    # @api.one
    # def _compute_invoice_ids(self):
    #     self.invoice_ids = self.cear_ids.mapped('invoice_ids')