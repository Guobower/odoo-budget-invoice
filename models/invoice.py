# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_core.models.utilities import choices_tuple


class Invoice(models.Model):
    _name = 'budget.invoice.invoice'
    _rec_name = 'invoice_no'
    _description = 'Invoice'
    _order = 'id desc'
    _inherit = ['mail.thread']

    # CHOICES
    # ----------------------------------------------------------
    STATES = choices_tuple(['draft', 'verified', 'summary generated',
                            'under certification', 'sent to finance', 'closed',
                            'on hold', 'rejected', 'amount hold'], is_sorted=False)
    INVOICE_TYPES = choices_tuple(['access network', 'supply of materials', 'civil works', 'cable works',
                                   'damage case', 'development', 'fdh uplifting', 'fttm activities',
                                   'maintenance work', 'man power', 'mega project', 'migration',
                                   'on demand activities', 'provisioning', 'recharge', 'recovery'], is_sorted=False)

    # BASIC FIELDS
    # ----------------------------------------------------------
    state = fields.Selection(STATES, default='draft')

    invoice_no = fields.Char(string="Invoice No")
    invoice_type = fields.Selection(INVOICE_TYPES)

    revenue_amount = fields.Monetary(string='Revenue Amount', currency_field='company_currency_id')
    opex_amount = fields.Monetary(string='OPEX Amount', currency_field='company_currency_id')
    capex_amount = fields.Monetary(string='CAPEX Amount', currency_field='company_currency_id')
    penalty_amount = fields.Monetary(string='Penalty Amount', currency_field='company_currency_id')

    on_hold_amount = fields.Monetary(string='On Hold Amount', currency_field='company_currency_id')
    # TODO Make Validation for max 100%
    on_hold_percentage = fields.Float(string='On Hold Percent (%)', digits=(5, 2))

    invoice_date = fields.Date(string='Invoice Date')
    invoice_cert_date = fields.Date(string='Inv Certification Date')
    received_date = fields.Date(string='Received Date')
    signed_date = fields.Date(string='Signed Date')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    rfs_date = fields.Date(string='RFS Date')
    reject_date = fields.Date(string='Reject Date')
    sent_finance_date = fields.Date(string='Sent to Finance Date')
    closed_date = fields.Date(string='Closed Date')
    cost_center = fields.Char(string="Cost Center")
    expense_code = fields.Char(string="Expense Code")
    remarks = fields.Text(string='Remarks')
    description = fields.Text(string='Description')
    proj_no = fields.Char(string="Project No")

    # Used for Invoice Summary sequence
    sequence = fields.Integer('Display order')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    company_currency_id = fields.Many2one('res.currency', readonly=True,
                                          default=lambda self: self.env.user.company_id.currency_id)
    contract_id = fields.Many2one('budget.contractor.contract', string='Contract')
    amount_ids = fields.One2many('budget.invoice.amount',
                                 'invoice_id',
                                 string="Amounts")
    cear_allocation_ids = fields.One2many('budget.invoice.cear.allocation',
                                          'invoice_id',
                                          string="CEARs")
    oear_allocation_ids = fields.One2many('budget.invoice.oear.allocation',
                                          'invoice_id',
                                          string="OEARs")
    summary_ids = fields.Many2many('budget.invoice.invoice.summary',
                                   'budget_invoice_summary_invoice',
                                   'invoice_id',
                                   'summary_id',
                                   string='Summaries')
    region_id = fields.Many2one('budget.enduser.region', string="Region")
    section_id = fields.Many2one('res.partner', string="Section", domain=[('is_budget_section', '=', True)])
    sub_section_id = fields.Many2one('res.partner', string="Sub Section", domain=[('is_budget_sub_section', '=', True)])

    # RELATED FIELDS
    # ----------------------------------------------------------
    related_contractor_id = fields.Many2one(string='Contractor',
                                            related='contract_id.contractor_id',
                                            store=True)
    # COMPUTE FIELDS
    # ----------------------------------------------------------
    problem = fields.Char(string='Problem',
                          compute='_compute_problem',
                          store=True)
    invoice_amount = fields.Monetary(string='Invoice Amount', currency_field='company_currency_id',
                                     compute='_compute_invoice_amount',
                                     store=True)
    certified_invoice_amount = fields.Monetary(string='Certified Amount', currency_field='company_currency_id',
                                               compute='_compute_certified_invoice_amount',
                                               inverse='_set_certified_invoice_amount',
                                               store=True)
    total_capex_amount = fields.Monetary(string='CAPEX Amount to be Allocated', currency_field='company_currency_id',
                                         compute='_compute_total_capex_amount',
                                         store=True)
    total_opex_amount = fields.Monetary(string='OPEX Amount to be Allocated', currency_field='company_currency_id',
                                         compute='_compute_total_opex_amount',
                                         store=True)

    @api.one
    @api.depends('certified_invoice_amount', 'invoice_no')
    def _compute_problem(self):
        # Checks Duplicate
        count = self.env['budget.invoice.invoice'].search_count([('invoice_no', '=', self.invoice_no),
                                                                 ('state', '!=', 'rejected')])
        if count > 1:
            self.problem = 'duplicate'

        # elif self.cear_id.problem != 'ok':
        #     self.problem = self.cear_id.problem
        #
        # # TODO USE CATEGORY ALSO TO IGNORE Y
        # elif self.state == 'draft':
        #     if self.cear_id.authorized_amount < self.certified_invoice_amount + self.cear_id.utilized_amount:
        #         self.problem = 'overrun'
        #
        #         # TODO MUST BE PLACED IN ACTUALS
        #     if self.state == 'draft' and self.cear_id.authorized_amount < self.certified_invoice_amount + self.cear_id.total_amount:
        #         self.problem = 'overrun'

        else:
            self.problem = 'ok'

    @api.one
    @api.depends('revenue_amount', 'opex_amount', 'capex_amount')
    def _compute_invoice_amount(self):
        self.invoice_amount = self.opex_amount + \
                              self.capex_amount + \
                              self.revenue_amount

    @api.one
    def _set_certified_invoice_amount(self):
        if self.certified_invoice_amount != self.opex_amount + self.capex_amount + self.revenue_amount:
            self._compute_certified_invoice_amount()

    @api.one
    @api.depends('revenue_amount', 'opex_amount',
                 'capex_amount', 'penalty_amount', 'on_hold_amount')
    def _compute_certified_invoice_amount(self):
        self.certified_invoice_amount = self.opex_amount + \
                                        self.capex_amount + \
                                        self.revenue_amount - \
                                        self.penalty_amount - \
                                        self.on_hold_amount

    @api.one
    @api.depends('amount_ids', 'amount_ids.amount', 'amount_ids.budget_type')
    def _compute_total_opex_amount(self):
        self.total_opex_amount = sum(self.amount_ids.filtered(lambda r: r.budget_type == 'opex').mapped('amount'))

    @api.one
    @api.depends('amount_ids', 'amount_ids.amount', 'amount_ids.budget_type')
    def _compute_total_capex_amount(self):
        self.total_capex_amount = sum(self.amount_ids.filtered(lambda r: r.budget_type in ['capex', 'revenue']). \
                                      mapped('amount'))

    # ONCHANGE
    # ----------------------------------------------------------
    # certified_invoice_amount
    # on_hold_amount = certified_invoice_amount * on_hold_percentage / 100.00
    # on_hold_percentage = on_hold_amount / certified_invoice_amount * 100.00

    @api.onchange('on_hold_amount')
    def onchange_on_hold_percentage(self):
        total_amount = self.opex_amount + self.capex_amount + self.revenue_amount - self.penalty_amount
        # if self.on_hold_amount != total_amount * self.on_hold_percentage / 100.00:
        if total_amount > 0.00:
            self.on_hold_percentage = self.on_hold_amount / total_amount * 100.00

    @api.onchange('on_hold_percentage')
    def onchange_on_hold_amount(self):
        total_amount = self.opex_amount + self.capex_amount + self.revenue_amount - self.penalty_amount
        # if self.on_hold_percentage != self.on_hold_amount / total_amount * 100.00:
        self.on_hold_amount = total_amount * self.on_hold_percentage / 100.00

    # BUTTONS/TRANSITIONS
    # ----------------------------------------------------------
    @api.one
    def set2draft(self):
        self.state = 'draft'

    @api.one
    def set2verified(self):
        self.state = 'verified'

    @api.one
    def set2summary_generated(self):
        self.state = 'summary generated'

    @api.one
    def set2under_certification(self):
        self.state = 'under certification'

    @api.one
    def set2sent_to_finance(self):
        self.state = 'sent to finance'

    @api.one
    def set2closed(self):
        self.state = 'closed'

    @api.one
    def set2on_hold(self):
        self.state = 'on hold'

    @api.one
    def set2rejected(self):
        self.state = 'rejected'

    @api.one
    def set2amount_hold(self):
        self.state = 'amount hold'
