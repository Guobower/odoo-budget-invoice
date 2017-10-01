# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_utilities.models.utilities import choices_tuple


class ProjectEstimatedCost(models.Model):
    _name = 'budget.invoice.pec'
    _rec_name = 'no'
    _description = 'Project Estimated Cost'
    _order = 'date desc'

    # CHOICES
    # ----------------------------------------------------------
    # BASIC FIELDS
    # ----------------------------------------------------------
    no = fields.Char(string='PEC No')
    date = fields.Date(string='Date')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    currency_id = fields.Many2one('res.currency', readonly=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    contract_id = fields.Many2one('budget.contractor.contract', string='Contract')
    cear_id = fields.Many2one('budget.capex.cear', string='CEAR')
    invoice_ids = fields.One2many('budget.invoice.invoice',
                                  'pec_id',
                                  string="Invoices")
