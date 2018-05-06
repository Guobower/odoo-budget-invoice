# -*- coding: utf-8 -*-
from odoo import fields, models, tools

from .invoice import Invoice


class InvoiceCearAllocationBI(models.Model):
    _name = "budget.invoice.cear.allocation.bi"
    _description = "CEAR Allocation BI"
    _auto = False

    # CHOICES
    # ----------------------------------------------------------
    STATES = Invoice.STATES
    TEAMS = Invoice.TEAMS
    YEARS = [(year, year) for year in range(1950, 2050)]

    # BASIC FIELDS
    # ----------------------------------------------------------
    invoice_received_date = fields.Date(string='Invoice Received Date',
                                        readonly=True)
    amount = fields.Monetary(currency_field='currency_id',
                             string='Allocated Against Invoice Amount',
                             readonly=True)
    authorized_amount = fields.Monetary(currency_field='currency_id',
                                        string='Authorized Amount',
                                        readonly=True)
    expenditure_amount = fields.Monetary(currency_field='currency_id',
                                         string='Expenditure Amount',
                                         readonly=True)
    commitment_amount = fields.Monetary(currency_field='currency_id',
                                        string='Commitment Amount',
                                        readonly=True)
    state = fields.Selection(selection=STATES,
                             string='State',
                             readonly=True)
    is_regional = fields.Boolean(string='Is Regional',
                                 readonly=True)
    is_head_office = fields.Boolean(string='Is Head Office',
                                    readonly=True)
    cear_year = fields.Selection(selection=YEARS,
                                 string='Year',
                                 readonly=True)

    # RELATIONSHIPS
    # ----------------------------------------------------------
    currency_id = fields.Many2one('res.currency',
                                  string='Currency',
                                  readonly=True)
    cear_id = fields.Many2one('budget.capex.cear',
                              string='CEAR',
                              readonly=True)
    po_id = fields.Many2one('budget.purchase.order',
                            string='Purchase Order',
                            readonly=True)
    invoice_id = fields.Many2one('budget.invoice.invoice',
                                 string='Invoice',
                                 readonly=True)
    contract_id = fields.Many2one('budget.contractor.contract',
                                  string='Contract',
                                  readonly=True)
    contractor_id = fields.Many2one('budget.contractor.contractor',
                                    string='Contractor',
                                    readonly=True)
    responsible_id = fields.Many2one('res.users',
                                     string='Responsible',
                                     readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'budget_invoice_cear_allocation_bi')
        self._cr.execute("""
            CREATE OR REPLACE VIEW budget_invoice_cear_allocation_bi AS (
                SELECT
                  al.id                          AS id,
                  cear.id                        AS cear_id,
                  AVG(cear.authorized_amount)    AS authorized_amount,
                  AVG(cear.commitment_amount)    AS commitment_amount,
                  AVG(cear.expenditure_amount)   AS expenditure_amount,
                  SUM(al.amount)                 AS amount,
                  cear.year                      AS cear_year,
                  po.id                          AS po_id,
                  inv.id                         AS invoice_id,
                  inv.invoice_no                 AS invoice_no,
                  inv.received_date              AS invoice_received_date,
                  al.currency_id                 AS currency_id,
                  inv.state                      AS state,
                  inv.contract_id                AS contract_id,
                  inv.contractor_id              AS contractor_id,
                  inv.responsible_id             AS responsible_id,
                  inv.is_regional                AS is_regional,
                  inv.is_head_office             AS is_head_office
                FROM
                  budget_invoice_cear_allocation AS al
                  LEFT JOIN budget_invoice_invoice AS inv ON inv.id = al.invoice_id
                  LEFT JOIN budget_purchase_order AS po ON po.id = inv.po_id
                  LEFT JOIN budget_capex_cear AS cear ON cear.id = al.cear_id
                  GROUP BY al.id, cear.id, cear_year, po.id, inv.id, invoice_no, invoice_received_date, inv.currency_id,
                    inv.state, contract_id, inv.contractor_id, responsible_id
              )
        """)
