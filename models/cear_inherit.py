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

    allocation_ids = fields.One2many('budget.invoice.cear.allocation',
                                     'cear_id',
                                     string="Allocations")
    po_id = fields.Many2one('budget.invoice.purchase.order',
                            string='Purchase Order')
    # COMPUTE FIELDS
    # ----------------------------------------------------------
    problem = fields.Char(string='Problem',
                          compute='_compute_problem')
    im_utilized_amount = fields.Monetary(currency_field='company_currency_id',
                                         string='Utilized Amount (IM)',
                                         compute='_compute_im_utilized_amount',
                                         store=True)

    @api.one
    @api.depends('allocation_ids', 'allocation_ids.amount', 'allocation_ids.invoice_id.state')
    def _compute_im_utilized_amount(self):
        cear_allocations = self.env['budget.invoice.cear.allocation'].search([('cear_id', '=', self.id),
                                                                              ('related_invoice_state', 'not in',
                                                                               ['draft', 'on hold', 'rejected'])
                                                                              ])
        self.im_utilized_amount = sum(cear_allocations.mapped('amount'))

    @api.one
    @api.depends('authorized_amount', 'fn_utilized_amount', 'im_utilized_amount', 'category', 'state')
    def _compute_problem(self):

        if self.category == "Y":
            # False to represent that problem check is not to be perform
            self.problem = False

        elif self.authorized_amount < self.im_utilized_amount:
            self.problem = 'overrun'

        # TODO THIS GOES TO ACTUAL
        elif self.authorized_amount < self.fn_utilized_amount:
            self.problem = 'overrun'

        else:
            self.problem = 'ok'

    # BUTTONS
    # ----------------------------------------------------------
