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
    # task_ids exist in the Budget Inherit in Capex Module

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    total_certified_invoice_amount = fields.Monetary(compute='_compute_total_certified_invoice_amount',
                                                   currency_field='company_currency_id',
                                                   string='Total Certified Amount',
                                                   store=True)

    @api.one
    @api.depends('task_ids.invoice_ids.certified_invoice_amount')
    def _compute_total_certified_invoice_amount(self):
        self.total_certified_invoice_amount = sum(self.task_ids.invoice_ids.mapped('certified_invoice_amount'))
