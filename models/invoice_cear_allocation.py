# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_core.models.utilities import choices_tuple


class CearAllocation(models.Model):
    _name = 'budget.invoice.cear.allocation'
    _rec_name = 'invoice_id'
    _description = 'Invoice Task Allocation'
    _order = 'sequence'

    # CHOICES
    # ----------------------------------------------------------

    # BASIC FIELDS
    # ----------------------------------------------------------
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id')

    # Used for Invoice Summary sequence
    sequence = fields.Integer('Display order')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    company_currency_id = fields.Many2one('res.currency', readonly=True,
                                          default=lambda self: self.env.user.company_id.currency_id)
    invoice_id = fields.Many2one('budget.invoice.invoice',
                                 string='Invoice')
    cear_id = fields.Many2one('budget.capex.cear',
                              string='CEAR',
                              domain="[('state','=','authorized')]")

    # RELATED FIELD
    # ----------------------------------------------------------
    related_invoice_state = fields.Selection(related='invoice_id.state')
    related_invoice_certified_invoice_amount = fields.Monetary(currency_field='company_currency_id',
                                                               related='invoice_id.certified_invoice_amount')
    related_cear_im_utilized_amount = fields.Monetary(currency_field='company_currency_id',
                                                      related='cear_id.im_utilized_amount')
    related_cear_fn_utilized_amount = fields.Monetary(currency_field='company_currency_id',
                                                      related='cear_id.fn_utilized_amount')
    related_cear_authorized_amount = fields.Monetary(currency_field='company_currency_id',
                                                     related='cear_id.authorized_amount')
    related_cear_problem = fields.Char(related='cear_id.problem')

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    problem = fields.Char(string='Problem',
                          compute='_compute_problem',
                          store=True)

    @api.one
    @api.depends('invoice_id.state', 'invoice_id.certified_invoice_amount',
                 'cear_id.problem')
    def _compute_problem(self):
        if self.invoice_id.state not in ['draft', False]:
            self.problem = self.cear_id.problem
            return

        if self.cear_id.problem != "ok":
            self.problem = self.cear_id.problem
            return
        cear_im_utilized = self.cear_id.im_utilized_amount
        cear_fn_utilized = self.cear_id.fn_utilized_amount
        cear_authorized =  self.cear_id.authorized_amount
        invoice_certified_invoice = self.invoice_id.certified_invoice_amount

        if cear_im_utilized + invoice_certified_invoice > cear_authorized:
            self.problem = "overrun"

        elif cear_fn_utilized + invoice_certified_invoice > cear_authorized:
            self.problem = "overrun"

        else:
            self.problem = "ok"