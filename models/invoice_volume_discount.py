# -*- coding: utf-8 -*-
# TODO DEPRECATE VOLUME DISCOUNT THESE
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.addons.budget_utilities.models.utilities import choices_tuple

from datetime import datetime
from collections import namedtuple


def check_overlapping_dates(start_1, end_1, start_2, end_2, frmt='%Y-%m-%d'):
    start_1 = datetime.strptime(start_1, frmt)
    end_1 = datetime.strptime(end_1, frmt)
    start_2 = datetime.strptime(start_2, frmt)
    end_2 = datetime.strptime(end_2, frmt)
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=start_1, end=end_1)
    r2 = Range(start=start_2, end=end_2)
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    return (earliest_end - latest_start).days + 1


# TODO MAKE VALIDATION FOR OVERLAPPING DATES
# TODO MAKE VALIDATION START DATE CANNOT BE GREATER THAN END DATE
class InvoiceVolumeDiscount(models.Model):
    _name = 'budget.invoice.volume.discount'
    _rec_name = 'period'
    _description = 'Volume Discount'
    _order = 'start_date desc'

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
    contractor_id = fields.Many2one('budget.contractor.contractor',
                                    string='Contractor'
                                    )

    contract_id = fields.Many2one('budget.contractor.contract',
                                  domain="[('contractor_id','=',contractor_id)]",
                                  string='Contract'
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
