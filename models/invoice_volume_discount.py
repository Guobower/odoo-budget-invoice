# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.addons.budget_core.models.utilities import choices_tuple


class InvoiceVolumeDiscount(models.Model):
    _name = 'budget.invoice.volume.discount'
    _rec_name = 'period'
    _description = 'Volume Discount'
    _order = 'start_date'

    # CHOICES
    # ----------------------------------------------------------

    # BASIC FIELDS
    # ----------------------------------------------------------
    discount_percentage = fields.Float(string='Discount Percent (%)', digits=(5, 2))
    start_date = fields.Date(string='Start Date')

    # Used for Invoice Summary sequence
    sequence = fields.Integer('Display order')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    contractor_id = fields.Many2one('res.partner',
                                    domain="[('is_budget_contractor','=',True)]",
                                    string='Contractor'
                                    )
    # COMPUTE FIELDS
    # ----------------------------------------------------------
    end_date = fields.Date(string='End Date',
                           compute='_compute_end_date',
                           inverse='_set_end_date',
                           store=True)
    period = fields.Char(string='Period',
                         compute='_compute_period',
                         store=True)

    @api.one
    @api.depends('start_date')
    def _compute_end_date(self):
        if self.start_date:
            start_date = fields.Date.from_string(self.start_date)
            end_date = start_date + relativedelta(years=1) - relativedelta(days=1)
            self.end_date = end_date

    @api.one
    @api.depends('start_date', 'end_date')
    def _compute_period(self):
        if self.start_date and self.end_date:
            start_date = fields.Date.from_string(self.start_date)
            end_date = fields.Date.from_string(self.end_date)
            self.period = '{0:%b%y}-{1:%b%y}'.format(start_date, end_date)

    @api.one
    def _set_end_date(self):
        return