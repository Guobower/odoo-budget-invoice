# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.budget_core.models.utilities import choices_tuple

from odoo.exceptions import ValidationError, UserError


def amount_setter(invoice=None, budget_type=None):
    if budget_type is None:
        raise ValidationError('Budget Type In Amount Setter must not be None')

    amount_id = invoice.amount_ids.search([('budget_type', '=', budget_type), ('invoice_id', '=', invoice.id)], limit=1)
    if not amount_id:
        amount_id = invoice.amount_ids.create({
            'budget_type': budget_type,
            'invoice_type': 'others',
            'payment_type': 'others',
        })

    amount_id.write({
        'amount': getattr(invoice, '%s_amount' % budget_type),
        'invoice_id': invoice.id
    })


class Invoice(models.Model):
    _name = 'budget.invoice.invoice'
    _rec_name = 'invoice_no'
    _description = 'Invoice'
    _order = 'sequence desc'
    _inherit = ['mail.thread']

    # CHOICES
    # ----------------------------------------------------------
    STATES = choices_tuple(['draft', 'verified', 'summary generated',
                            'under certification', 'sent to finance', 'closed',
                            'on hold', 'rejected', 'amount hold'], is_sorted=False)
    TEAMS = choices_tuple(['head office', 'regional'], is_sorted=False)
    INVOICE_TYPES = choices_tuple(['access network', 'supply of materials', 'civil works', 'cable works',
                                   'damage case', 'development', 'fdh uplifting', 'fttm activities',
                                   'maintenance work', 'man power', 'mega project', 'migration',
                                   'on demand activities', 'provisioning', 'recharge', 'recovery'], is_sorted=False)

    # BASIC FIELDS
    # ----------------------------------------------------------
    state = fields.Selection(STATES, default='draft')
    team = fields.Selection(TEAMS, string='Team')

    invoice_no = fields.Char(string="Invoice No")
    approval_ref = fields.Char(string="Approval Ref")

    on_hold_percentage = fields.Float(string='On Hold Percent (%)', digits=(5, 2))
    penalty_percentage = fields.Float(string='Penalty Percent (%)', digits=(5, 2))

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

    remark = fields.Text(string='Remarks')
    description = fields.Text(string='Description')
    proj_no = fields.Char(string="PEC No")

    # Used for Invoice Summary sequence
    sequence = fields.Integer('Display order')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    company_currency_id = fields.Many2one('res.currency', readonly=True,
                                          default=lambda self: self.env.user.company_id.currency_id)
    contract_id = fields.Many2one('budget.contractor.contract', string='Contract')
    po_id = fields.Many2one('budget.invoice.purchase.order',
                            string='Purchase Order')

    # TODO TO BE REMOVED ONCE FINALIZE
    account_code_id = fields.Many2one('budget.core.account.code', string='Account Code')
    cost_center_id = fields.Many2one('budget.core.cost.center', string='Cost Center')

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

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    contractor_id = fields.Many2one('res.partner',
                                    domain="[('is_budget_contractor','=',True)]",
                                    string='Contractor',
                                    compute='_compute_contractor_id',
                                    inverse='_set_contractor_id',
                                    store=True)
    problem = fields.Char(string='Problem',
                          compute='_compute_problem',
                          store=True)
    discount_percentage = fields.Float(string='Discount Percent (%)',
                                       digits=(5, 2),
                                       compute='_compute_discount_percentage',
                                       inverse='_set_discount_percentage',
                                       store=True)
    opex_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                  compute='_compute_opex_amount',
                                  inverse='_set_opex_amount',
                                  string='OPEX Amount')
    capex_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                   compute="_compute_capex_amount",
                                   inverse='_set_capex_amount',
                                   string='CAPEX Amount')
    revenue_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                     compute='_compute_revenue_amount',
                                     inverse='_set_revenue_amount',
                                     string='Revenue Amount')
    invoice_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                     compute='_compute_invoice_amount',
                                     string='Invoice Amount')
    penalty_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                     compute='_compute_penalty_amount',
                                     string='Penalty Amount')
    discount_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                      compute='_compute_discount_amount',
                                      string='Discount Amount')
    on_hold_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                     compute='_compute_on_hold_amount',
                                     inverse='_set_on_hold_amount',
                                     string='On Hold Amount')
    certified_invoice_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                               compute='_compute_certified_invoice_amount',
                                               string='Certified Amount')
    balance_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                     compute='_compute_balance_amount',
                                     string='Balance Amount')

    cear_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                  compute='_compute_cear_amount',
                                  string='Cear Amount')

    oear_amount = fields.Monetary(currency_field='company_currency_id', store=True,
                                  compute='_compute_oear_amount',
                                  string='Oear Amount')

    @api.one
    @api.depends('contract_id')
    def _compute_contractor_id(self):
        self.contractor_id = self.contract_id.contractor_id

    @api.one
    @api.depends('cear_allocation_ids.problem', 'invoice_no', 'contract_id')
    def _compute_problem(self):
        # Checks Duplicate
        count = self.search_count([('invoice_no', '=', self.invoice_no),
                                   ('contract_id.contractor_id', '=', self.contractor_id.id),
                                   ('state', '!=', 'rejected')])
        if count > 1:
            self.problem = 'duplicate'

        else:
            problems = self.cear_allocation_ids.mapped('problem')
            uniq_problems = set(problems) - set([False])
            self.problem = '; '.join(uniq_problems)

    @api.one
    @api.depends('invoice_date', 'contractor_id')
    def _compute_discount_percentage(self):
        if self.invoice_date:
            reference_date = self.invoice_date
        elif self.contractor_id:
            reference_date = fields.Date.today()
        else:
            self.discount_percentage = 0.00
            return

        volume_discount_id = self.contractor_id.volume_discount_ids. \
            search([('start_date', '<=', reference_date),
                    ('end_date', '>=', reference_date)], limit=1)

        if len(volume_discount_id) == 0:
            self.discount_percentage = 0.00
        else:
            self.discount_percentage = volume_discount_id.discount_percentage

    @api.one
    @api.depends('amount_ids', 'amount_ids.amount', 'amount_ids.budget_type')
    def _compute_opex_amount(self):
        self.opex_amount = sum(self.amount_ids.filtered(lambda r: r.budget_type == 'opex'). \
                               mapped('amount'))

    @api.one
    @api.depends('amount_ids', 'amount_ids.amount', 'amount_ids.budget_type')
    def _compute_capex_amount(self):
        self.capex_amount = sum(self.amount_ids.filtered(lambda r: r.budget_type in ['capex']). \
                                mapped('amount'))

    @api.one
    @api.depends('amount_ids', 'amount_ids.amount', 'amount_ids.budget_type')
    def _compute_revenue_amount(self):
        self.revenue_amount = sum(self.amount_ids.filtered(lambda r: r.budget_type in ['revenue']). \
                                  mapped('amount'))

    @api.one
    @api.depends('revenue_amount', 'opex_amount', 'capex_amount')
    def _compute_invoice_amount(self):
        self.invoice_amount = self.opex_amount + \
                              self.capex_amount + \
                              self.revenue_amount

    @api.one
    @api.depends('penalty_percentage', 'invoice_amount')
    def _compute_penalty_amount(self):
        self.penalty_amount = self.invoice_amount * self.penalty_percentage / 100

    @api.one
    @api.depends('discount_percentage', 'invoice_amount')
    def _compute_discount_amount(self):
        self.discount_amount = self.invoice_amount * self.discount_percentage / 100

    @api.one
    @api.depends('on_hold_percentage', 'certified_invoice_amount')
    def _compute_on_hold_amount(self):
        self.on_hold_amount = self.certified_invoice_amount * self.on_hold_percentage / 100

    @api.one
    @api.depends('invoice_amount', 'penalty_amount', 'discount_amount')
    def _compute_certified_invoice_amount(self):
        self.certified_invoice_amount = self.invoice_amount - self.penalty_amount - self.discount_amount

    @api.one
    @api.depends('cear_allocation_ids', 'capex_amount', 'revenue_amount')
    def _compute_cear_amount(self):
        self.cear_amount = self.capex_amount + self.revenue_amount

    @api.one
    @api.depends('amount_ids', 'opex_amount')
    def _compute_oear_amount(self):
        self.oear_amount = self.opex_amount

    # INVERSE FIELDS
    # ----------------------------------------------------------
    @api.one
    def _set_penalty_amount(self):
        self.penalty_percentage = self.penalty_amount / self.certified_invoice_amount * 100

    @api.one
    def _set_discount_amount(self):
        self.discount_percentage = self.discount_amount / self.certified_invoice_amount * 100

    @api.one
    def _set_on_hold_amount(self):
        self.on_hold_percentage = self.on_hold_amount / self.certified_invoice_amount * 100

    @api.one
    def _set_capex_amount(self):
        amount_setter(invoice=self, budget_type='capex')

    @api.one
    def _set_revenue_amount(self):
        amount_setter(invoice=self, budget_type='revenue')

    @api.one
    def _set_opex_amount(self):
        amount_setter(invoice=self, budget_type='opex')

    @api.one
    def _set_contractor_id(self):
        return

    @api.one
    def _set_discount_percentage(self):
        return

    _set_discount_percentage
    # CONSTRAINS
    # ----------------------------------------------------------
    _sql_constraints = [
        ('on_hold_percentage_min_max', 'CHECK (on_hold_percentage BETWEEN 0 AND 100)',
         'On Hold Percentage must be with in 0-100'),
        ('penalty_percentage_min_max', 'CHECK (penalty_percentage BETWEEN 0 AND 100)',
         'Penalty Percentage must be with in 0-100'),
    ]

    @api.one
    @api.constrains('cear_amount', 'cear_allocation_ids')
    def _check_total_capex(self):
        allocation_cear_amount = sum(self.cear_allocation_ids.mapped('amount'))
        # if the difference of cear_amount and allocation is less than 1 (threshold),
        # it means that it is miss allocated
        if abs(self.cear_amount - allocation_cear_amount) > 1:
            msg = 'TOTAL INVOICE (CEAR) AMOUNT IS {} BUT CEAR AMOUNT ALLOCATED IS {}'.format(self.cear_amount,
                                                                                             allocation_cear_amount
                                                                                             )
            raise ValidationError(msg)

    # @api.one
    # @api.constrains('opex_amount', 'oear_allocation_ids')
    # def _check_total_opex(self):
    #     oear_amount = self.opex_amount
    #     allocation_oear_amount = sum(self.oear_allocation_ids.mapped('amount'))
    #     if oear_amount != allocation_oear_amount:
    #         msg = 'TOTAL OEAR AMOUNT IS {} BUT OEAR AMOUNT ALLOCATED IS {}'.format(allocation_oear_amount,
    #                                                                                oear_amount)
    #         raise ValidationError(msg)

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

    # ADDITIONAL FUNCTIONS
    # ----------------------------------------------------------

    # POLYMORPH FUNCTIONS
    # ----------------------------------------------------------
    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})

        dup_amounts = []
        for amount in self.amount_ids:
            dup_amounts.append(amount.copy({'invoice_id': False}))

        dup_cear_allocations = []
        for cear_allocation in self.cear_allocation_ids:
            dup_cear_allocations.append(cear_allocation.copy({'invoice_id': False}))

        default.update(
            amount_ids=[(6, 0, [i.id for i in dup_amounts])],
            cear_allocation_ids=[(6, 0, [i.id for i in dup_cear_allocations])]
        )

        return super(Invoice, self).copy(default)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        # CHECK USER GROUP AND ASSIGN IF TEAM IS REGIONAL OR HEAD OFFICE
        current_user = self.env.user
        options = {
            'head office': ['group_invoice_head_office_user', 'group_invoice_head_office_manager'],
            'regional': ['group_invoice_regional_user', 'group_invoice_regional_manager']
        }
        for team, groups in options.items():
            for group in groups:
                if self.env.ref('budget_invoice.{}'.format(group)) in current_user.groups_id:
                    values.update(team=team)
                    break

        return super(Invoice, self).create(values)
