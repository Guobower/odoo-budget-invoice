# -*- coding: utf-8 -*-

from openerp import models, fields, api
from .utils import choices_tuple

class Invoice(models.Model):
    _name = 'budget.invoice'
    _rec_name = 'invoice_no'
    _description = 'Invoice'

    # CHOICES
    # ----------------------------------------------------------
    STATES = choices_tuple(['new', 'verify invoices', 'overrun check', 'print summary',
               'under certification', 'sent to finance', 'completed'], is_sorted=False)
    INVOICE_TYPES = choices_tuple(['to be filled up'], is_sorted=False)
    PAYMENT_TYPES = choices_tuple(['to be filled up'], is_sorted=False)

    # BASIC FIELDS
    # ----------------------------------------------------------
    state = fields.Selection(STATES, default='new')

    #Regional for Sir Max Team, HO of mehmood team
#    region = fields.Char(string="Contract No")

    invoice_no = fields.Char(string="Invoice No")
    invoice_type = fields.Selection(INVOICE_TYPES)
    payment_type = fields.Selection(PAYMENT_TYPES)
    revenue_amount = fields.Float(string='Revenue Amount', digits=(32, 4), default=0.00)
    opex_amount = fields.Float(string='OPEX Amount', digits=(32, 4), default=0.00)
    capex_amount = fields.Float(string='CAPEX Amount', digits=(32, 4), default=0.00)
    invoice_amount = fields.Float(string='Invoice Amount', digits=(32, 4), default=0.00)
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
    cost_center = fields.Char(string="Cost Center")
    expense_code = fields.Char(string="Expense Code")
    remarks = fields.Text(string='Remarks')
    description = fields.Text(string='Description')
    proj_no = fields.Char(string="Project No")

    # RELATIONSHIPS
    # ----------------------------------------------------------
    contract_id = fields.Many2one('budget.contract', string='Contract')
    compute_contractor_id = fields.Many2one('res.partner', string='Contractor')
    #  task = models.ForeignKey(Task, null=True, on_delete=models.CASCADE)

    # BUTTONS
    # ----------------------------------------------------------
    @api.one
    def set2verify_invoice(self):
        pass