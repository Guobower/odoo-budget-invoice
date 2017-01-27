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
    problem = fields.Char(string='Problem',
                          compute='_compute_problem')

    @api.one
    @api.depends('related_cear_problem', 'invoice_id.certified_invoice_amount')
    def _compute_problem(self):
        if not self.related_cear_problem:
            return
        elif self.related_cear_problem != "ok":
            self.problem = self.related_cear_problem
        elif self.related_cear_im_utilized_amount + self.related_invoice_certified_invoice_amount > self.related_cear_authorized_amount:
            self.problem = "overrun"
        elif self.related_cear_fn_utilized_amount + self.related_invoice_certified_invoice_amount > self.related_cear_authorized_amount:
            self.problem = "overrun"
        else:
            self.problem = "ok"
