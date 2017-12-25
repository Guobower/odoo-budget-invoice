# -*- coding: utf-8 -*-
from odoo import fields, models, api
from .invoice import Invoice


class InvoiceKpiChecker(models.Model):
    _name = "budget.invoice.invoice.kpi.checker"
    _description = "Invoice KPI Checker"

    # CHOICES
    # ----------------------------------------------------------
    TEAMS = Invoice.TEAMS

    # BASIC FIELDS
    # ----------------------------------------------------------
    team = fields.Selection(TEAMS)
    threshold = fields.Integer()
