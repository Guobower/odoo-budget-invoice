# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .utils import choices_tuple

class TaskInherit(models.Model):
    _inherit = 'budget.task'

    # BASIC FIELDS
    # ----------------------------------------------------------

    # RELATIONSHIPS
    # ----------------------------------------------------------
    # company_currency_id already exist in the parent model
    invoice_ids = fields.One2many('budget.invoice',
                                  'task_id',
                                  string="Invoices")

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    utilized_amount = fields.Monetary(currency_field='company_currency_id',
                                      string='Utilized Amount (IM)',
                                      compute='_compute_utilized_amount',
                                      store=True)

    @api.one
    @api.depends('invoice_ids.invoice_amount', 'invoice_ids.state')
    def _compute_utilized_amount(self):
        invoices = self.env['budget.invoice'].search([('task_id', '=', self.id),
                                           ('state', 'in', ['verified', 'summary generated',
                                                            'under certification', 'sent to finance', 'closed',])
                                           ])
        self.utilized_amount = sum(invoices.mapped('invoice_amount'))

    # BUTTONS
    # ----------------------------------------------------------

