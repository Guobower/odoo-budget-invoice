# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_core.models.utilities import choices_tuple


class TaskInherit(models.Model):
    _inherit = 'budget.capex.cear'

    # CHOICES
    # ----------------------------------------------------------


    # BASIC FIELDS
    # ----------------------------------------------------------
    # state already exist in the parent model
    # category already exist in the parent model
    # authorized_amount already exist in the parent model

    # RELATIONSHIPS
    # ----------------------------------------------------------
    # company_currency_id already exist in the parent model

    # invoice_ids = fields.One2many('budget.invoice.invoice',
    #                               'cear_id',
    #                               string="Invoices")

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    problem = fields.Char(string='Problem')
    # utilized_amount = fields.Monetary(currency_field='company_currency_id',
    #                                   string='Utilized Amount (IM)',
    #                                   compute='_compute_utilized_amount',
    #                                   store=True)

    # @api.one
    # @api.depends('invoice_ids')
    # def _compute_total_invoice(self):
#        self.total_invoice = len(self.invoice_ids)
#     @api.one
#     @api.depends('authorized_amount', 'utilized_amount', 'category', 'state', 'total_amount')
#     def _compute_problem(self):
#
#         if self.category == "Y":
#             self.problem = 'ok'
#
#         elif self.authorized_amount < self.utilized_amount:
#             self.problem = 'overrun'
#
#         # TODO THIS GOES TO ACTUAL
#         elif self.authorized_amount < self.total_amount:
#             self.problem = 'overrun'
#
#         else:
#             self.problem = 'ok'

    # @api.one
    # @api.depends('invoice_ids.certified_invoice_amount', 'invoice_ids.state')
    # def _compute_utilized_amount(self):
    #     pass
        # invoices = self.env['budget.invoice.invoice'].search([('cear_id', '=', self.id),
        #                                    ('state', 'in', ['verified', 'summary generated', 'amount hold',
        #                                                     'under certification', 'sent to finance', 'closed'])
        #                                    ])
        # self.utilized_amount = sum(invoices.mapped('certified_invoice_amount'))

    # BUTTONS
    # ----------------------------------------------------------
