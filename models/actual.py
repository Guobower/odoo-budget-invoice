# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.budget_core.models.utilities import choices_tuple


class Actual(models.Model):
    _name = 'budget.invoice.actual'
    _rec_name = 'no'
    _description = 'Actual'
    _order = 'no'

    # CHOICES
    # ----------------------------------------------------------
    # BASIC FIELDS
    # ----------------------------------------------------------
    no = fields.Char(string='Reference')
    date = fields.Date(string='Date')
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    company_currency_id = fields.Many2one('res.currency', readonly=True,
                                          default=lambda self: self.env.user.company_id.currency_id)
    contractor_id = fields.Many2one('res.partner',
                                    domain=[('is_budget_contractor', '=', True)],
                                    string='Invoice')

    cear_id = fields.Many2one('budget.capex.cear', string='CEAR')

    oear_id = fields.Many2one('budget.opex.oear', string="OEAR")
