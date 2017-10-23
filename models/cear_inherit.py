# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_utilities.models.utilities import choices_tuple


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
    # currency_id already exist in the parent model

    allocation_ids = fields.One2many('budget.invoice.cear.allocation',
                                     'cear_id',
                                     string="Allocations")

    actual_ids = fields.One2many('budget.invoice.actual',
                                 'cear_id',
                                 string="Actuals")

    # RELATED FIELDS
    # ----------------------------------------------------------

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    problem = fields.Char(string='Problem',
                          compute='_compute_problem',
                          store=True)

    im_utilized_amount = fields.Monetary(currency_field='currency_id',
                                         string='Utilized Amount (IM)',
                                         compute='_compute_im_utilized_amount',
                                         store=True)

    @api.one
    @api.depends('authorized_amount', 'fn_utilized_amount', 'im_utilized_amount', 'category')
    def _compute_problem(self):

        if self.category == "Y":
            self.problem = False
            return

        if self.authorized_amount < self.im_utilized_amount:
            self.problem = 'IM overrun'
            return

        if self.authorized_amount < self.fn_utilized_amount:
            self.problem = 'FN overrun'
            return

        self.problem = False

    @api.one
    @api.depends('allocation_ids', 'allocation_ids.amount', 'allocation_ids.invoice_id.state')
    def _compute_im_utilized_amount(self):
        self.invoice_ids = self.mapped('allocation_ids.invoice_id')
        cear_allocations = self.env['budget.invoice.cear.allocation'].search([('cear_id', '=', self.id),
                                                                              ('invoice_id.state', 'not in',
                                                                               ['draft', 'on hold', 'rejected'])
                                                                              ])
        self.im_utilized_amount = sum(cear_allocations.mapped('amount'))


        # BUTTONS
        # ----------------------------------------------------------
