# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons.budget_utilities.models.utilities import choices_tuple
from odoo.exceptions import ValidationError, UserError

from datetime import datetime
from dateutil.relativedelta import relativedelta

# DUE TO REFLECT ALL CHANGES IN ALL SIDES

DIFFERENCE_THRESHOLD = 1


def convert_amount(currency_id, amount):
    if currency_id:
        return amount / currency_id.rate
    return amount


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


def _set_team(self=None):
    # TODO REMOVE
    # CHECK USER GROUP AND ASSIGN IF TEAM IS REGIONAL OR HEAD OFFICE
    current_user = self.env.user
    # user = self.env['res.users'].browse(self.env.uid)
    #
    # if user.has_group('base.group_sale_salesman'):
    #     print 'This user is a salesman'
    # else:
    #     print 'This user is not a salesman'
    options = {
        'regional': ['group_invoice_regional_user', 'group_invoice_regional_manager'],
        'head office': ['group_invoice_head_office_user', 'group_invoice_head_office_manager'],
    }
    for team, groups in options.items():
        for group in groups:
            if self.env.ref('budget_invoice.{}'.format(group)) in current_user.groups_id:
                return team
    return False


class Invoice(models.Model):
    _name = 'budget.invoice.invoice'
    _rec_name = 'invoice_no'
    _description = 'Invoice'
    _order = 'sequence desc'
    _inherit = ['mail.thread', 'budget.enduser.mixin']

    # CHOICES
    # ----------------------------------------------------------
    STATES = choices_tuple(['draft', 'verified', 'summary generated', 'sd signed', 'svp signed',
                            'cto signed', 'sent to finance', 'closed',
                            'on hold', 'rejected', 'amount hold'], is_sorted=False)
    TEAMS = choices_tuple(['head office', 'regional', 'resource'], is_sorted=False)
    KPI_STATES = choices_tuple(['pending', 'in', 'out'], is_sorted=False)
    INVOICE_TYPES = choices_tuple(['access network', 'supply of materials', 'civil works', 'cable works',
                                   'damage case', 'development', 'fdh uplifting', 'fttm activities',
                                   'maintenance work', 'man power', 'mega project', 'migration',
                                   'on demand activities', 'provisioning', 'recharge', 'recovery'], is_sorted=False)
    MMS_MONTH = choices_tuple(['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                               'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], is_sorted=False)
    MMS_YEAR = choices_tuple([str(i) for i in range(2005, 2025)], is_sorted=False)

    # BASIC FIELDS
    # ----------------------------------------------------------
    # division_id, section_id, sub_section_id exist in enduser.mixin
    is_head_office = fields.Boolean(default=False)
    is_regional = fields.Boolean(default=False)

    # TODO REMOVE AFTER MIGRATION
    # ----------------------------------------------------------
    odoo10_id = fields.Integer()
    # ----------------------------------------------------------
    state = fields.Selection(STATES, default='draft', track_visibility='onchange')
    # TODO REMOVE
    team = fields.Selection(TEAMS, string='Team', default=lambda self: _set_team(self))

    invoice_no = fields.Char(string="Invoice No")
    # TODO MOVE TO OUTSOURING
    approval_ref = fields.Char(string="Approval Ref")
    mms_no = fields.Char(string="MMS No")
    mms_month = fields.Selection(MMS_MONTH, string="MMS Month")
    mms_year = fields.Selection(MMS_YEAR, string="MMS Year")
    # TODO DEPRECATED
    charge_account = fields.Char(string="Charge Account")

    on_hold_percentage = fields.Float(string='On Hold Percent (%)', digits=(5, 2))
    penalty_percentage = fields.Float(string='Penalty Percent (%)', digits=(5, 2))
    discount_percentage = fields.Float(string='Discount Percent (%)', digits=(5, 2))
    other_deduction_percentage = fields.Float(string='Other Deduction Amount(%)', digits=(5, 2))
    due_percentage = fields.Float(string='Due Amount (%)', digits=(5, 2), default=100)

    is_on_hold_percentage = fields.Boolean(string='Is On Hold (%)', default=True)
    is_penalty_percentage = fields.Boolean(string='Is Penalty (%)', default=True)
    is_discount_percentage = fields.Boolean(string='Is Discount (%)', default=True)
    is_other_deduction_percentage = fields.Boolean(string='Is Other Deduction (%)', default=True)
    is_discount_apply_after_other_deduction_percentage = fields.Boolean(string='Apply Discount After Other Deduction',
                                                                        default=False)
    is_due_percentage = fields.Boolean(string='Is Due Amount (%)', default=True)

    initial_invoice_amount = fields.Monetary(currency_field='currency_id', string='Initial Invoice Amount',
                                             help="Invoice Amount used for Initial Input Only,"
                                                  " not used for any calculation")
    input_on_hold_amount = fields.Monetary(currency_field='currency_id', string='On Hold Amount')
    input_penalty_amount = fields.Monetary(currency_field='currency_id', string='Penalty Amount')
    input_discount_amount = fields.Monetary(currency_field='currency_id', string='Discount Amount')
    input_other_deduction_amount = fields.Monetary(currency_field='currency_id',
                                                   string='Other Deduction Amount')
    input_due_amount = fields.Monetary(currency_field='currency_id',
                                       string='Due Amount')

    # TODO DEPRECATE
    period_start_date = fields.Date(string='Period Start Date')
    period_end_date = fields.Date(string='Period End Date')
    # ---------------

    invoice_date = fields.Date(string='Invoice Date')
    invoice_cert_date = fields.Date(string='Inv Certification Date')
    claim_start_date = fields.Date(string='Claim Start Date')
    claim_end_date = fields.Date(string='Claim End Date')

    received_date = fields.Date(string='Received Date', default=lambda self: fields.Date.today())
    # TODO DEPRECATE
    signed_date = fields.Date(string='Signed Date')
    # ---------------
    sd_signed_date = fields.Date(string='SD Signed Date', track_visibility='onchange')
    svp_signed_date = fields.Date(string='SVP Signed Date', track_visibility='onchange')
    cto_signed_date = fields.Date(string='CTO Signed Date', track_visibility='onchange')
    sent_finance_date = fields.Date(string='Sent to Finance Date', track_visibility='onchange')
    closed_date = fields.Date(string='Closed Date', track_visibility='onchange')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    rfs_date = fields.Date(string='RFS Date')  # TODO MAKE THIS CONTRACTUAL RFS
    actual_rfs_date = fields.Date(string='Actual RFS Date')

    on_hold_date = fields.Date(string='On Hold Date')
    reject_date = fields.Date(string='Reject Date')

    remark = fields.Text(string='Remarks')
    system_remark = fields.Text(string='System Remarks')
    description = fields.Text(string='Description')
    # TODO DEPRECATE
    proj_no = fields.Char(string="PEC No")
    # ---------------

    # Used for Invoice Summary sequence
    sequence = fields.Integer('Display order')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    aed_currency_id = fields.Many2one('res.currency', readonly=True,
                                      default=lambda self: self.env['res.currency'].search([('name', '=', 'AED')],
                                                                                           limit=1))

    currency_id = fields.Many2one('res.currency', readonly=True,
                                  store=True,
                                  compute='_compute_currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id)

    is_different_currency = fields.Boolean(string="Is Diff. Currency", readonly=True,
                                           compute='_compute_is_different_currency', store=True)

    responsible_id = fields.Many2one('res.users', string='Responsible',
                                     default=lambda self: self.env.user.id)
    pec_id = fields.Many2one('budget.invoice.pec', string='PEC No')
    contract_id = fields.Many2one('budget.contractor.contract', string='Contract')
    contractor_id = fields.Many2one('budget.contractor.contractor', string='Contractor')
    # TODO DEPRECATED
    old_contractor_id = fields.Many2one('res.partner', string='Old Contractor')
    # ---------------
    po_id = fields.Many2one('budget.purchase.order',
                            string='Purchase Order')

    # TODO DEPRECATED ONCE ALDREADY TRANSFERED TO OEARS
    account_code_id = fields.Many2one('budget.core.account.code', string='Account Code')
    cost_center_id = fields.Many2one('budget.core.cost.center', string='Cost Center')
    # ---------------
    amount_ids = fields.One2many('budget.invoice.amount',
                                 'invoice_id',
                                 copy=True,
                                 string="Amounts")
    cear_allocation_ids = fields.One2many('budget.invoice.cear.allocation',
                                          'invoice_id',
                                          copy=True,
                                          string="CEARs")
    oear_allocation_ids = fields.One2many('budget.invoice.oear.allocation',
                                          'invoice_id',
                                          copy=True,
                                          string="OEARs")
    summary_ids = fields.Many2many('budget.invoice.invoice.summary',
                                   'budget_invoice_summary_invoice',
                                   'invoice_id',
                                   'summary_id',
                                   string='Summaries')
    region_id = fields.Many2one('budget.enduser.region', string="Region")

    # TODO DEPRECATE
    old_sub_section_id = fields.Many2one('res.partner', string="Old Sub Section")
    old_section_id = fields.Many2one('res.partner', string="Old Section")

    # RELATED FIELDS
    # ----------------------------------------------------------
    related_po_amount = fields.Monetary(currency_field='currency_id',
                                        related='po_id.amount',
                                        string='PO Amount')
    related_po_paid_amount = fields.Monetary(currency_field='currency_id',
                                             related='po_id.total_invoice_amount',
                                             string='PO Paid Amount')

    # ONCHANGE FIELDS
    # ----------------------------------------------------------
    @api.onchange('contractor_id', 'invoice_no')
    def _onchange_domain_contract_id(self):
        if self.contractor_id:
            return {'domain': {'contract_id': [('contractor_id', '=', self.contractor_id.id)]}}
        else:
            return {'domain': {'contract_id': []}}

    @api.onchange('contract_id')
    def _onchange_contractor_id(self):
        self.contractor_id = self.contract_id.contractor_id

    @api.onchange('contract_id', 'invoice_date')
    def _onchange_input_discount_percentage(self):
        if self.contract_id.discount_rule_id and self.contract_id.is_discount_applicable:
            self.is_discount_percentage = True
            self.input_discount_amount = 0
            eval_context = {'datetime': datetime,
                            'relativedelta': relativedelta,
                            'cr': self.env.cr,
                            'invoice_id': self,
                            'contract_id': self.contract_id}
            # CODE START
            # invoice_id = self
            # contract_id = self.contract_id
            # cr = self.env.cr
            # discount_percentage = 0.00
            # if invoice_id.invoice_date and invoice_id.contract_id:
            #
            #     year_invoice = invoice_id.year_invoice
            #     year_invoice = 'Year ' + str(int(year_invoice[-1]) - 1)
            #     sql = """
            #     SELECT SUM(certified_invoice_amount)
            #     FROM budget_invoice_invoice
            #     WHERE state NOT IN ('draft', 'on hold', 'rejected', 'amount hold')
            #       AND contract_id = %(contract_id)s
            #       AND year_invoice = '%(year_invoice)s'
            #     GROUP BY contract_id, year_invoice
            #     """ % {
            #         'contract_id': contract_id.id,
            #         'year_invoice': year_invoice,
            #     }
            #
            #     cr.execute(sql)
            #     res = cr.dictfetchone()
            #     total_certified_amount_previous_month = 0.0 if res is None else res['sum']
            #     for discount in contract_id.discount_ids.search([('contract_id', '=', contract_id.id)],
            #                                                     order='min_threshold desc'):
            #         min_threshold = discount.min_threshold
            #         max_threshold = discount.max_threshold
            #         if min_threshold <= total_certified_amount_previous_month and max_threshold == -1:
            #             discount_percentage = discount.discount_percentage
            #             break
            #
            #         elif min_threshold <= total_certified_amount_previous_month <= max_threshold:
            #             discount_percentage = discount.discount_percentage
            #             break

            # self.discount_percentage = discount_percentage

            # CODE END
            eval_context = self.contract_id.discount_rule_id.run_rule_code(eval_context)
            self.discount_percentage = eval_context['discount_percentage']

    @api.onchange('rfs_date')
    def _onchange_actual_rfs_date(self):
        if not self.actual_rfs_date:
            self.actual_rfs_date = self.rfs_date

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    problem = fields.Char(string='Problem',
                          compute='_compute_problem',
                          store=True)
    has_hold_amount = fields.Boolean(string='Has Amount Hold',
                                     compute='_compute_has_hold_amount',
                                     store=True)
    discount_applicable = fields.Char(string='Discount Applicable',
                                      compute='_compute_discount_applicable',
                                      store=True)
    year_rfs = fields.Char(string='Year RFS',
                           compute='_compute_year_rfs',
                           inverse='_set_year_rfs',
                           index=True,
                           store=True,
                           help='Year is the rfs year against contract period '
                                '(eg. contract start is 08/08/2017, '
                                'year_rfs 1 will be between 08/08/2017 - 08/08/2018)')
    year_invoice = fields.Char(string='Year Invoice',
                               compute='_compute_year_invoice',
                               inverse='_set_year_invoice',
                               index=True,
                               store=True,
                               help='Year is the invoice year against contract period '
                                    '(eg. contract start is 08/08/2017, '
                                    'year_invoice 1 will be between 08/08/2017 - 08/08/2018)')
    kpi_lapse_days = fields.Integer(string="KPI Lapse Days",
                                    compute='_compute_kpi_lapse_days',
                                    store=True)
    kpi_state = fields.Selection(KPI_STATES, string="KPI Status",
                                 compute='_compute_kpi_state',
                                 default='pending',
                                 store=True)
    claim_lapse_days = fields.Integer(string='Claim KPI Days',
                                      compute='_compute_claim_lapse_days',
                                      store=True)
    opex_amount = fields.Monetary(currency_field='currency_id', store=True,
                                  compute='_compute_opex_amount',
                                  inverse='_set_opex_amount',
                                  string='OPEX Amount')
    capex_amount = fields.Monetary(currency_field='currency_id', store=True,
                                   compute="_compute_capex_amount",
                                   inverse='_set_capex_amount',
                                   string='CAPEX Amount')
    revenue_amount = fields.Monetary(currency_field='currency_id', store=True,
                                     compute="_compute_revenue_amount",
                                     inverse='_set_revenue_amount',
                                     string='Revenue Amount')
    invoice_amount = fields.Monetary(currency_field='currency_id', store=True,
                                     compute='_compute_invoice_amount',
                                     inverse='_set_invoice_amount',
                                     string='Invoice Amount')
    penalty_amount = fields.Monetary(currency_field='currency_id', store=True,
                                     compute='_compute_penalty_amount',
                                     string='Penalty Amount')
    discount_amount = fields.Monetary(currency_field='currency_id', store=True,
                                      compute='_compute_discount_amount',
                                      string='Discount Amount')
    on_hold_amount = fields.Monetary(currency_field='currency_id', store=True,
                                     compute='_compute_on_hold_amount',
                                     string='On Hold Amount')
    other_deduction_amount = fields.Monetary(currency_field='currency_id', store=True,
                                             compute='_compute_other_deduction_amount',
                                             string='Tools/Other Deduction Amount')
    due_amount = fields.Monetary(currency_field='currency_id', store=True,
                                 compute='_compute_due_amount',
                                 string='Due Amount')
    certified_invoice_amount = fields.Monetary(currency_field='currency_id', store=True,
                                               compute='_compute_certified_invoice_amount',
                                               string='Certified Amount')
    certified_capex_amount = fields.Monetary(currency_field='currency_id', store=True,
                                             compute='_compute_certified_capex_amount',
                                             string='Certified Capex Amount')
    certified_opex_amount = fields.Monetary(currency_field='currency_id', store=True,
                                            compute='_compute_certified_opex_amount',
                                            string='Certified Opex Amount')
    certified_revenue_amount = fields.Monetary(currency_field='currency_id', store=True,
                                               compute='_compute_certified_revenue_amount',
                                               string='Certified Revenue Amount')

    balance_amount = fields.Monetary(currency_field='currency_id', store=True,
                                     compute='_compute_balance_amount',
                                     string='Balance Amount')

    cear_amount = fields.Monetary(currency_field='currency_id', store=True,
                                  compute='_compute_cear_amount',
                                  string='Cear Amount')

    oear_amount = fields.Monetary(currency_field='currency_id', store=True,
                                  compute='_compute_oear_amount',
                                  string='Oear Amount')

    # SAME AS CEAR AND OEAR, IT WILL BE USE TO CHECK WHETHER TO HIDE CEAR AND OEAR TABS
    total_revenue_amount = fields.Monetary(currency_field='currency_id', store=True,
                                           compute='_compute_total_revenue_amount',
                                           string='Total Revenue Amount')

    summary_id = fields.Many2one('budget.invoice.invoice.summary',
                                 compute="_compute_summary_id",
                                 inverse='_set_summary_id',
                                 string="Summary Reference",
                                 track_visibility='onchange',
                                 store=True)

    capex_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                       store=True,
                                       compute='_compute_capex_aed_amount',
                                       string='Capex Amount AED'
                                       )

    opex_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                      store=True,
                                      compute='_compute_opex_aed_amount',
                                      string='Opex Amount AED'
                                      )

    invoice_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                         store=True,
                                         compute='_compute_invoice_aed_amount',
                                         string='Invoice Amount AED'
                                         )

    revenue_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                         store=True,
                                         compute="_compute_revenue_aed_amount",
                                         string='Revenue Amount AED')

    certified_invoice_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                                   store=True,
                                                   compute="_compute_certified_invoice_aed_amount",
                                                   string='Certified Amount AED')

    certified_capex_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                                 store=True,
                                                 compute="_compute_certified_capex_aed_amount",
                                                 string='Certified Capex AED')

    certified_opex_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                                store=True,
                                                compute="_compute_certified_opex_aed_amount",
                                                string='Certified Opex AED')

    certified_revenue_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                                   store=True,
                                                   compute="_compute_certified_revenue_aed_amount",
                                                   string='Certified Revenue AED')

    penalty_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                         store=True,
                                         compute="_compute_penalty_aed_amount",
                                         string='Penalty Amount AED')

    discount_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                          store=True,
                                          compute="_compute_discount_aed_amount",
                                          string='Discount Amount AED')

    on_hold_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                         store=True,
                                         compute="_compute_on_hold_aed_amount",
                                         string='On Hold Amount AED')

    other_deduction_aed_amount = fields.Monetary(currency_field='aed_currency_id',
                                                 store=True,
                                                 compute="_compute_other_deduction_aed_amount",
                                                 string='Other Deduction Amount AED')

    @api.one
    @api.depends('contract_id', 'contract_id.commencement_date', 'rfs_date')
    def _compute_discount_applicable(self):
        pass

    @api.one
    @api.depends('received_date', 'sent_finance_date')
    def _compute_kpi_lapse_days(self):
        if self.received_date and self.sent_finance_date:
            sent_finance_date = fields.Date.from_string(self.sent_finance_date)
            received_date = fields.Date.from_string(self.received_date)

            self.kpi_lapse_days = relativedelta(sent_finance_date, received_date).days
        else:
            self.kpi_lapse_days = 0

    @api.one
    @api.depends('kpi_lapse_days')
    def _compute_kpi_state(self):
        # TODO FIX THIS
        return
        # threshold = self.env['budget.invoice.invoice.kpi.checker'].search([('team', '=', self.team)], limit=1)
        #
        # if not threshold:
        #     self.kpi_state = 'pending'
        #     return
        #
        # self.kpi_state = 'in' if self.kpi_lapse_days <= threshold.threshold else 'out'

    @api.one
    @api.depends('claim_start_date', 'claim_end_date')
    def _compute_claim_lapse_days(self):
        if self.claim_start_date and self.claim_end_date:
            diff = relativedelta(fields.Date.from_string(self.claim_end_date),
                                 fields.Date.from_string(self.claim_start_date)).days
            self.claim_lapse_days = diff
        else:
            self.claim_lapse_days = 0

    @api.one
    @api.depends('contract_id', 'contract_id.commencement_date', 'rfs_date')
    def _compute_year_rfs(self):
        # TODO MAKE TEST
        contract_start = fields.Date.from_string(self.contract_id.commencement_date)
        contract_end = fields.Date.from_string(self.contract_id.end_date)
        rfs_date = fields.Date.from_string(self.rfs_date)

        if not contract_start or not rfs_date or not contract_end:
            return

        # the total number of years inclusive in the contract
        number_of_years = contract_end.year - contract_start.year

        # year starts at 1 and ends at number_of_years + 1
        for year in range(1, number_of_years + 1):
            start = contract_start + relativedelta(years=year - 1)
            end = contract_start + relativedelta(years=year)

            if start <= rfs_date < end:
                self.year_rfs = 'Year %s' % year
                continue

    @api.one
    @api.depends('contract_id', 'contract_id.commencement_date', 'invoice_date')
    def _compute_year_invoice(self):
        # TODO MAKE TEST
        contract_start = fields.Date.from_string(self.contract_id.commencement_date)
        contract_end = fields.Date.from_string(self.contract_id.end_date)
        invoice_date = fields.Date.from_string(self.invoice_date)

        if not contract_start or not invoice_date or not contract_end:
            return

        # the total possible number of years enclosing the invoice date
        # + 1 to make sure invoice_date will be inclusive
        number_of_years = invoice_date.year - contract_start.year + 1

        # year starts at 1 and ends at number_of_years + 1
        for year in range(1, number_of_years + 1):
            start = contract_start + relativedelta(years=year - 1)
            end = contract_start + relativedelta(years=year)

            if start <= invoice_date < end:
                self.year_invoice = 'Year %s' % year
                break

    @api.one
    @api.depends('on_hold_amount')
    def _compute_has_hold_amount(self):
        self.has_hold_amount = True if self.on_hold_amount != 0.0 else False

    @api.one
    @api.depends('state', 'cear_allocation_ids.problem', 'invoice_no', 'contractor_id')
    def _compute_problem(self):
        if self.state == 'rejected':
            self.problem = False
            return

        # Checks Duplicate
        domain = [('invoice_no', '=', self.invoice_no),
                  ('contractor_id', '=', self.contractor_id.id),
                  ('state', '!=', 'rejected')]
        if not isinstance(self.id, models.NewId):
            domain.append(('id', '!=', self.id))

        invoice_ids = self.search(domain)
        if len(invoice_ids) > 0:
            self.problem = 'duplicate'
            return

        problems = self.cear_allocation_ids.mapped('problem')
        uniq_problems = set(problems) - {False}
        if len(uniq_problems) > 0:
            self.problem = '; '.join(uniq_problems)
            return

        self.problem = False
        return

    @api.one
    @api.depends('amount_ids', 'amount_ids.amount', 'amount_ids.budget_type', 'amount_ids.currency_id')
    def _compute_opex_amount(self):
        for amount_id in self.amount_ids.filtered(lambda r: r.budget_type == 'opex'):
            self.opex_amount += amount_id.amount

    @api.one
    @api.depends('currency_id', 'opex_amount')
    def _compute_opex_aed_amount(self):
        self.opex_aed_amount = convert_amount(self.currency_id, self.opex_amount)

    @api.one
    @api.depends('amount_ids', 'amount_ids.amount', 'amount_ids.budget_type', 'amount_ids.currency_id')
    def _compute_capex_amount(self):
        for amount_id in self.amount_ids.filtered(lambda r: r.budget_type in ['capex']):
            self.capex_amount += amount_id.amount

    @api.one
    @api.depends('capex_amount', 'currency_id')
    def _compute_capex_aed_amount(self):
        self.capex_aed_amount = convert_amount(self.currency_id, self.capex_amount)

    @api.one
    @api.depends('amount_ids', 'amount_ids.amount', 'amount_ids.budget_type', 'amount_ids.currency_id')
    def _compute_revenue_amount(self):
        for amount_id in self.amount_ids.filtered(lambda r: r.budget_type in ['revenue']):
            self.revenue_amount += amount_id.amount

    @api.one
    @api.depends('currency_id', 'revenue_amount')
    def _compute_revenue_aed_amount(self):
        self.revenue_aed_amount = convert_amount(self.currency_id, self.revenue_amount)

    @api.one
    @api.depends('revenue_amount', 'opex_amount', 'capex_amount')
    def _compute_invoice_amount(self):
        self.invoice_amount = self.opex_amount + \
                              self.capex_amount + \
                              self.revenue_amount

    @api.one
    @api.depends('revenue_aed_amount', 'opex_aed_amount', 'capex_aed_amount')
    def _compute_invoice_aed_amount(self):
        self.invoice_aed_amount = self.opex_aed_amount + \
                                  self.capex_aed_amount + \
                                  self.revenue_aed_amount

    @api.one
    @api.depends('is_penalty_percentage', 'penalty_percentage',
                 'input_penalty_amount', 'invoice_amount')
    def _compute_penalty_amount(self):
        if self.is_penalty_percentage:
            self.penalty_amount = self.invoice_amount * self.penalty_percentage / 100
            self.input_penalty_amount = 0
            return
        self.penalty_amount = self.input_penalty_amount
        self.penalty_percentage = 0

    @api.one
    @api.depends('is_discount_percentage', 'discount_percentage',
                 'is_discount_apply_after_other_deduction_percentage',
                 'input_discount_amount', 'invoice_amount')
    def _compute_discount_amount(self):
        if self.is_discount_percentage:

            if self.is_discount_apply_after_other_deduction_percentage:
                to_be_discounted_amount = self.invoice_amount - self.other_deduction_amount
            else:
                to_be_discounted_amount = self.invoice_amount

            self.discount_amount = to_be_discounted_amount * self.discount_percentage / 100
            self.input_discount_amount = 0
            return

        self.discount_amount = self.input_discount_amount
        self.discount_percentage = 0

    @api.one
    @api.depends('is_on_hold_percentage', 'on_hold_percentage',
                 'input_on_hold_amount', 'invoice_amount')
    def _compute_on_hold_amount(self):
        if self.is_on_hold_percentage:
            self.on_hold_amount = self.invoice_amount * self.on_hold_percentage / 100
            self.input_on_hold_amount = 0
            return
        self.on_hold_amount = self.input_on_hold_amount
        self.on_hold_percentage = 0

    @api.one
    @api.depends('is_other_deduction_percentage', 'other_deduction_percentage',
                 'input_other_deduction_amount', 'invoice_amount')
    def _compute_other_deduction_amount(self):
        if self.is_other_deduction_percentage:
            self.other_deduction_amount = self.invoice_amount * self.other_deduction_percentage / 100
            self.input_other_deduction_amount = 0
            return
        self.other_deduction_amount = self.input_other_deduction_amount
        self.other_deduction_percentage = 0

    @api.one
    @api.depends('is_due_percentage', 'due_percentage',
                 'input_due_amount')
    def _compute_due_amount(self):
        if self.is_due_percentage:
            self.due_amount = self.invoice_amount
            self.input_due_amount = 0
            return
        self.due_amount = self.input_due_amount
        self.due_percentage = 0

    @api.one
    @api.depends('invoice_amount', 'penalty_amount', 'discount_amount',
                 'on_hold_amount', 'other_deduction_amount')
    def _compute_certified_invoice_amount(self):
        self.certified_invoice_amount = self.invoice_amount - self.penalty_amount - self.discount_amount - \
                                        self.on_hold_amount - self.other_deduction_amount

    @api.one
    @api.depends('invoice_amount', 'certified_invoice_amount', 'capex_amount')
    def _compute_certified_capex_amount(self):
        if self.invoice_amount == 0.0:
            return
        percentage = self.capex_amount / self.invoice_amount
        self.certified_capex_amount = self.certified_invoice_amount * percentage

    @api.one
    @api.depends('invoice_amount', 'certified_invoice_amount', 'opex_amount')
    def _compute_certified_opex_amount(self):
        if self.invoice_amount == 0.0:
            return
        percentage = self.opex_amount / self.invoice_amount
        self.certified_opex_amount = self.certified_invoice_amount * percentage

    @api.one
    @api.depends('invoice_amount', 'certified_invoice_amount', 'revenue_amount')
    def _compute_certified_revenue_amount(self):
        if self.invoice_amount == 0.0:
            return
        percentage = self.revenue_amount / self.invoice_amount
        self.certified_revenue_amount = self.certified_invoice_amount * percentage

    @api.one
    @api.depends('cear_allocation_ids', 'capex_amount')
    def _compute_cear_amount(self):
        self.cear_amount = self.capex_amount

    @api.one
    @api.depends('oear_allocation_ids', 'opex_amount')
    def _compute_oear_amount(self):
        self.oear_amount = self.opex_amount

    @api.one
    @api.depends('cear_allocation_ids', 'oear_allocation_ids', 'revenue_amount')
    def _compute_total_revenue_amount(self):
        self.total_revenue_amount = self.revenue_amount

    @api.one
    @api.depends('summary_ids')
    def _compute_summary_id(self):
        if self.summary_ids:
            self.summary_id = self.summary_ids.sorted(key='id', reverse=True)[0]

    @api.one
    @api.depends('amount_ids', 'amount_ids.currency_id')
    def _compute_currency_id(self):
        self.currency_id = False if not self.mapped('amount_ids.currency_id') \
            else self.mapped('amount_ids.currency_id')[0]

    @api.one
    @api.depends('currency_id', 'aed_currency_id')
    def _compute_is_different_currency(self):
        if self.currency_id == self.aed_currency_id:
            self.is_different_currency = False
        else:
            self.is_different_currency = True

    @api.depends('currency_id', 'currency_id.name')
    def _compute_currency_name(self):
        self.currency_name = self.currency_id.name

    @api.one
    @api.depends('certified_invoice_amount')
    def _compute_certified_invoice_aed_amount(self):
        self.certified_invoice_aed_amount = convert_amount(self.currency_id, self.certified_invoice_amount)

    @api.one
    @api.depends('certified_capex_amount')
    def _compute_certified_capex_aed_amount(self):
        self.certified_capex_aed_amount = convert_amount(self.currency_id, self.certified_capex_amount)

    @api.one
    @api.depends('certified_opex_amount')
    def _compute_certified_opex_aed_amount(self):
        self.certified_opex_aed_amount = convert_amount(self.currency_id, self.certified_opex_amount)

    @api.one
    @api.depends('certified_revenue_amount')
    def _compute_certified_revenue_aed_amount(self):
        self.certified_revenue_aed_amount = convert_amount(self.currency_id, self.certified_revenue_amount)

    @api.one
    @api.depends('penalty_amount')
    def _compute_penalty_aed_amount(self):
        self.penalty_aed_amount = convert_amount(self.currency_id, self.penalty_amount)

    @api.one
    @api.depends('discount_amount')
    def _compute_discount_aed_amount(self):
        self.discount_aed_amount = convert_amount(self.currency_id, self.discount_amount)

    @api.one
    @api.depends('on_hold_amount')
    def _compute_on_hold_aed_amount(self):
        self.on_hold_aed_amount = convert_amount(self.currency_id, self.on_hold_amount)

    @api.one
    @api.depends('other_deduction_amount')
    def _compute_other_deduction_aed_amount(self):
        self.other_deduction_aed_amount = convert_amount(self.currency_id, self.other_deduction_amount)

    # INVERSE FIELDS
    # ----------------------------------------------------------
    @api.one
    def _set_invoice_amount(self):
        return

    @api.one
    def _set_penalty_amount(self):
        return

    @api.one
    def _set_discount_amount(self):
        return

    @api.one
    def _set_on_hold_amount(self):
        return

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
    def _set_year_rfs(self):
        return

    @api.one
    def _set_year_invoice(self):
        return

    @api.one
    def _set_summary_id(self):
        return

    # CONSTRAINS
    # ----------------------------------------------------------
    _sql_constraints = [
        ('on_hold_percentage_min_max', 'CHECK (on_hold_percentage BETWEEN 0 AND 100)',
         'On Hold Percentage must be with in 0-100'),
        ('penalty_percentage_min_max', 'CHECK (penalty_percentage BETWEEN 0 AND 100)',
         'Penalty Percentage must be with in 0-100'),
    ]

    @api.one
    @api.constrains('cear_amount', 'oear_amount', 'total_revenue_amount',
                    'oear_allocation_ids', 'cear_allocation_ids')
    def _check_total_distributed_amount(self):
        current_user = self.env.user

        if current_user.has_group('base.group_system'):
            return

        amount = sum([amount_id.amount / amount_id.currency_id.rate for amount_id in self.mapped('amount_ids')])

        allocation_cear_amount = sum(self.mapped('cear_allocation_ids.amount'))
        allocation_oear_amount = sum(self.mapped('oear_allocation_ids.amount'))
        allocated_amount = allocation_cear_amount + allocation_oear_amount
        # if the difference of cear_amount and allocation is less than (threshold),
        # it means that it is miss allocated
        if abs(amount - allocated_amount) > DIFFERENCE_THRESHOLD:
            msg = 'TOTAL INVOICE AMOUNT IS {} BUT TOTAL AMOUNT ALLOCATED IS {}'.format(amount,
                                                                                       allocated_amount
                                                                                       )
            raise ValidationError(msg)

    @api.one
    @api.constrains('amount_ids', 'cear_allocation_ids', 'oear_allocation_ids')
    def _check_amount_ids_count_currency(self):
        currency_names = self.mapped('amount_ids.currency_id.name') + \
                         self.mapped('cear_allocation_ids.currency_id.name') + \
                         self.mapped('oear_allocation_ids.currency_id.name') + \
                         [self.currency_id.name]

        currency_names = [i for i in currency_names if i]
        if len(set(currency_names)) > 1:
            msg = 'Amount currency in an invoice should only be one and same for all elements'
            raise ValidationError(msg)

    @api.constrains('currency_id')
    def _check_purchase_order_invoice_currency(self):
        currency_names = self.mapped('po_id.currency_id.name') + \
            [self.currency_id.name]

        currency_names = [i for i in currency_names if i]
        if len(set(currency_names)) > 1:
            raise ValidationError("Purchase order and invoice currencies are different.")

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
    def set2sd_signed(self):
        self.state = 'sd signed'

    @api.one
    def set2svp_signed(self):
        self.state = 'svp signed'

    @api.one
    def set2cto_signed(self):
        self.state = 'cto signed'

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

    @api.one
    def reset(self):
        if self.summary_ids:
            raise ValidationError("Must not be part of a Summary, Please Remove")
        self.state = 'draft'

    # REDIRECT/OPEN OTHER VIEWS BUTTONS
    # ----------------------------------------------------------
    def summary_wizard(self):
        form_id = self.env.ref('budget_invoice.view_form_invoice_summary').id
        context = {
            'default_invoice_ids': [(6, 0, self.ids)],
            'is_head_office': True,
            'is_regional': True,
            'auto_generate': True
        }
        res = {
            'name': 'Create Summary',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'budget.invoice.invoice.summary',
            'views': [(form_id, 'form')],
            'context': context
        }
        return res

    # ADDITIONAL FUNCTIONS
    # ----------------------------------------------------------
    @api.model
    def recompute_problem(self, list_invoice_no):
        # APPLY DUPLICATE CHECK FOR ALL RELATED INVOICES USING WRITE
        # BECAUSE THE COMPUTED FIELD WON'T ALLOW UPDATE OF OTHER INVOICES
        # list_invoice_no = [self.invoice_no, vals.get('invoice_no')]
        invoice_ids = self.search([('invoice_no', 'in', list_invoice_no)])
        self.env.add_todo(self._fields['problem'], invoice_ids)
        self.recompute()
        self.env.cr.commit()

    @api.one
    def release_hold_amount(self):
        self.on_hold_percentage = 0.0
        self.on_hold_amount = 0.0

    # POLYMORPH FUNCTIONS
    # ----------------------------------------------------------
    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        new_values = {
            'summary_ids': False,
            'received_date': fields.Date.today(),
            'invoice_date': False,
            'invoice_cert_date': False,
            'start_date': False,
            'end_date': False,
            'rfs_date': False,
            'claim_start_date': False,
            'claim_end_date': False,
            'sd_signed_date': False,
            'svp_signed_date': False,
            'cto_signed_date': False,
            'sent_finance_date': False,
            'closed_date': False,
            'reject_date': False,
        }
        default.update(new_values)

        return super(Invoice, self).copy(default)

    @api.model
    def create(self, vals):
        list_invoice_no = self.mapped('invoice_no')
        if vals.get('invoice_no', False):
            list_invoice_no.append(vals.get('invoice_no'))
        res = super(Invoice, self).create(vals)

        self.recompute_problem(list_invoice_no)
        return res

    @api.multi
    def write(self, vals):
        list_invoice_no = self.mapped('invoice_no')
        if vals.get('invoice_no', False):
            list_invoice_no.append(vals.get('invoice_no'))
        res = super(Invoice, self).write(vals)

        self.recompute_problem(list_invoice_no)
        return res

    @api.multi
    def unlink(self):
        list_invoice_no = self.mapped('invoice_no')
        res = super(Invoice, self).unlink()

        self.recompute_problem(list_invoice_no)
        return res
