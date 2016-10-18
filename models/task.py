# -*- coding: utf-8 -*-

from openerp import models, fields, api
from .utils import choices_tuple

class Task(models.Model):
    _name = 'budget.task'
    _rec_name = 'task_no'
    _description = 'Task'

    # BASIC FIELDS
    # ----------------------------------------------------------
    region = fields.Char(string="Region")
    category = fields.Char(string="Category")
    year = fields.Integer(string="Year")

    task_no = fields.Char(string="Task No", required=True)
    task_class = fields.Char(string="Task Class")
    task_description = fields.Text(string="Task Description")
    task_owner = fields.Char(string="Task Owner")
    task_created_by = fields.Char(string="Task Create By")
    task_start_date = fields.Date(string="Task Start Date")
    task_completion_date = fields.Date(string="Task Completion Date")
    task_status = fields.Char(string="Task Status")

    authorized_amount = fields.Float(string='Authorized Amount', digits=(32, 4), default=0.00)
    current_year = fields.Float(string='Current Year Amount', digits=(32, 4), default=0.00)
    total_amount = fields.Float(string='Total Amount', digits=(32, 4), default=0.00)
    transferable_amount = fields.Float(string='Transferable Amount', digits=(32, 4), default=0.00)
    current_month_exp_amount = fields.Float(string='Current Month Expenditure Amount', digits=(32, 4), default=0.00)
    completion = fields.Integer(string="Completion")

    last_pcc_date = fields.Date(string="Last PCC Date")
    expected_completion_date = fields.Date(string="Expected Completion Date")
    last_followed_date = fields.Date(string="Last Followed Date")
    major_type = fields.Char(string="Major Type")
    minor_sub_type = fields.Char(string="Minor Sub Type")
    gl_code = fields.Char(string="GL Code")
    pec_no = fields.Char(string="Pec No")

    engineer_pf = fields.Char(string="Engineer PF")
    engineer_name = fields.Char(string="Engineer Name")
    engineer_contact = fields.Char(string="Engineer Contact")
    engineer_email = fields.Char(string="Engineer Email")
    engineer_department = fields.Char(string="Engineer Department")
    organization = fields.Char(string="Organization")

    proj_no = fields.Char(string="Project No")
    proj_description = fields.Text(string="Project Description")
    proj_owner = fields.Char(string="Project Owner")
    proj_start_date = fields.Date(string="Project Start Date")

    notes = fields.Text(string="Notes")
    # Direct Data from PMP dump
    user_id = fields.Char(string="User ID")
    fwp_user_id = fields.Char(string="FWP User ID")

    # RELATIONSHIPS
    # ----------------------------------------------------------
    invoice_ids = fields.One2many('budget.invoice',
                                  'task_id',
                                  string="Invoices")

    # COMPUTE FIELDS
    # ----------------------------------------------------------
    utilized_amount = fields.Float(string='Utilized Amount', digits=(32, 4), default=0.00,
                                   compute='_compute_utilized_amount',
                                   store=True)

    @api.one
    @api.depends('invoice_ids.invoice_amount', 'invoice_ids.state')
    def _compute_utilized_amount(self):
        invoices = self.env['budget.invoice'].search([('task_id', '=', self.id),
                                           ('state', 'in', ['verified', 'summary printed',
                                                            'under certification', 'sent to finance', 'closed',])
                                           ])
        self.utilized_amount = sum(invoices.mapped('invoice_amount'))
#        self.utilized_amount = sum(self.filtered(lambda r: r.invoice_ids.state=='verified').mapped('invoice_ids.invoice_amount'))
    # BUTTONS
    # ----------------------------------------------------------

