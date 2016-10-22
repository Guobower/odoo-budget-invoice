# -*- coding: utf-8 -*-

from openerp import models, fields, api
from .utils import choices_tuple

class Invoice(models.Model):
    _name = 'budget.invoice'
    _rec_name = 'invoice_no'
    _description = 'Invoice'
    _order = 'id desc'

    # CHOICES
    # ----------------------------------------------------------
    STATES = choices_tuple(['draft', 'verified', 'summary generated',
               'under certification', 'sent to finance', 'closed', 'rejected'], is_sorted=False)
    INVOICE_TYPES = choices_tuple(['access network', 'cable works', 'damage case', 'development',
                                   'fdh uplifting', 'fttm activities', 'maintainance work',
                                   'man power', 'mega project', 'migration', 'on demand activities',
                                   'provisioning', 'recharge', 'recovery'], is_sorted=False)
    PAYMENT_TYPES = choices_tuple(['ready for service', 'interim'], is_sorted=False)
    PROBLEMS = choices_tuple(['ok', 'duplicate', 'overrun'])
    REGIONS = choices_tuple(['AUH', 'DXB', 'NE', 'HO'])

    # BASIC FIELDS
    # ----------------------------------------------------------
    state = fields.Selection(STATES, default='draft')

    invoice_no = fields.Char(string="Invoice No", required=True)
    region = fields.Selection(REGIONS)
    invoice_type = fields.Selection(INVOICE_TYPES)
    payment_type = fields.Selection(PAYMENT_TYPES)
    revenue_amount = fields.Float(string='Revenue Amount', digits=(32, 4), default=0.00)
    opex_amount = fields.Float(string='OPEX Amount', digits=(32, 4), default=0.00)
    capex_amount = fields.Float(string='CAPEX Amount', digits=(32, 4), default=0.00)
    penalty = fields.Float(string='Penalty Amount', digits=(32, 4), default=0.00)
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

    # RELATIONSHIPS
    # ----------------------------------------------------------
    contract_id = fields.Many2one('budget.contract', string='Contract')
    compute_contractor_id = fields.Many2one('res.partner', string='Contractor')
    task_id = fields.Many2one('budget.task', string='Task')

    # RELATED FIELDS
    # ----------------------------------------------------------
    related_authorized_amount = fields.Float(string='Authorized Amount',
                                             related='task_id.authorized_amount')
    related_utilized_amount = fields.Float(string='Utilized Amount',
                                             related='task_id.utilized_amount')
    # COMPUTE FIELDS
    # ----------------------------------------------------------
    problem = fields.Selection(PROBLEMS, compute='_compute_problem', store=True)
    invoice_summary_id = fields.Many2one('budget.invoice.summary', string="Invoice Summary")
    invoice_amount = fields.Float(string='Invoice Amount', digits=(32, 4), default=0.00,
                                  compute='_compute_invoice_amount',
                                  store=True)

    @api.one
    @api.depends('invoice_no', 'invoice_amount', 'task_id.authorized_amount', 'task_id.utilized_amount')
    def _compute_problem(self):
        # Checks Duplicate
        count = self.env['budget.invoice'].search_count([('invoice_no', '=', self.invoice_no),
                                                         ('state', '!=', 'rejected')])
        if count > 1:
            self.problem = 'duplicate'
        # Checks Overrun
        elif self.state == 'draft' and self.task_id.authorized_amount < self.task_id.utilized_amount + self.invoice_amount:
            self.problem = 'overrun'
        elif self.state != 'draft' and self.task_id.authorized_amount < self.task_id.utilized_amount:
            self.problem = 'overrun'
        else:
            self.problem = 'ok'

    @api.one
    @api.depends('opex_amount', 'capex_amount', 'revenue_amount', 'penalty')
    def _compute_invoice_amount(self):
        self.invoice_amount = self.opex_amount + self.capex_amount + self.revenue_amount - self.penalty

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
    def set2rejected(self):
        self.state = 'rejected'
