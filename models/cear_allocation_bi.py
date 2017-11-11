# -*- coding: utf-8 -*-
from odoo import fields, models, tools


class InvoiceCearAllocationBI(models.Model):
    _name = "budget.invoice.cear.allocation.bi"
    _description = "CEAR Allocation BI"
    _auto = False

    cear_id = fields.Many2one('budget.capex.cear',
                              string='CEAR',
                              readonly=True)
    po_id = fields.Many2one('budget.purchase.order',
                            string='Purchase Order',
                            readonly=True)
    invoice_id = fields.Many2one('budget.invoice.invoice',
                                 string='Invoice',
                                 readonly=True)
    invoice_receive_date = fields.Date(string='Invoice Receive',
                                       readonly=True)
    amount = fields.Monetary(currency_field='currency_id',
                             string='Allocated Amount',
                             readonly=True)
    state = fields.Char(string='State',
                        readonly=True)
    team = fields.Char(string='Team',
                       readonly=True)
    currency_id = fields.Many2one('res.currency',
                                  string='Currency',
                                  readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'budget_invoice_cear_allocation_bi')
        self._cr.execute("""
            CREATE OR REPLACE VIEW budget_invoice_cear_allocation_bi AS (
                SELECT
                  al.id             AS id,
                  cear.id           AS cear_id,
                  po.id             AS po_id,
                  inv.id            AS invoice_id,
                  inv.received_date AS invoice_receive_date,
                  al.currency_id    AS currency_id,
                  al.amount         AS amount,
                  inv.state         AS state,
                  inv.team          AS team
                FROM
                  budget_invoice_cear_allocation AS al
                  LEFT JOIN
                  budget_invoice_invoice AS inv ON inv.id = al.invoice_id
                  LEFT JOIN
                  budget_purchase_order AS po ON po.id = inv.po_id
                  LEFT JOIN
                  budget_capex_cear AS cear ON cear.id = al.cear_id
              )
        """)
