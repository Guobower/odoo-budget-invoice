# -*- coding: utf-8 -*-


import string

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

import random

class TestInvoiceConstraints(TransactionCase):
    #

    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoiceConstraints, self).setUp()

        self.currency_01 = self.env['res.currency'].create({
            'name': ''.join(random.choices(string.ascii_uppercase + string.digits, k=3)),
            'symbol': ''.join(random.choices(string.ascii_uppercase + string.digits, k=3)),
            'rate_ids': [(0, 0, {'rate': 0.27})]
        })

        self.currency_02 = self.env['res.currency'].create({
            'name': ''.join(random.choices(string.ascii_uppercase + string.digits, k=3)),
            'symbol': ''.join(random.choices(string.ascii_uppercase + string.digits, k=3)),
            'rate_ids': [(0, 0, {'rate': 0.27})]
        })

        # Dummy PO
        self.po_id = self.env['budget.purchase.order'].create({
            'currency_id': self.currency_01.id
        })

    def test_same_currency(self):
        invoice_id = self.env['budget.invoice.invoice'].create({
            'po_id': self.po_id.id,
            'amount_ids': [(0, 0, {'budget_type': 'capex',
                                   'invoice_type': 'others',
                                   'payment_type': 'others',
                                   'currency_id': self.currency_01.id,
                                   'amount': 3000})]
        })
        self.assertTrue(invoice_id, "PO currency: {} and Invoice currency: {}, should be same".
                        format(self.po_id.currency_id.name, self.currency_01.name))

    def test_different_currency(self):
        with self.assertRaises(ValidationError):
            self.env['budget.invoice.invoice'].create({
                'po_id': self.po_id.id,
                'amount_ids': [(0, 0, {'budget_type': 'capex',
                                       'invoice_type': 'others',
                                       'payment_type': 'others',
                                       'currency_id': self.currency_02.id,
                                       'amount': 3000})]
            })

    def test_no_po(self):
        invoice_id = self.env['budget.invoice.invoice'].create({
            'po_id': False,
            'amount_ids': [(0, 0, {'budget_type': 'capex',
                                   'invoice_type': 'others',
                                   'payment_type': 'others',
                                   'currency_id': self.currency_02.id,
                                   'amount': 3000})]
        })
        self.assertTrue(invoice_id, "PO ID: {}, Invoice is not expected to have PO.".
                        format(', '.join(invoice_id.mapped('po_id.id'))))

    def test_edit_invoice(self):
        invoice_id = self.env['budget.invoice.invoice'].create({
            'po_id': self.po_id.id,
            'amount_ids': [(0, 0, {'budget_type': 'capex',
                                   'invoice_type': 'others',
                                   'payment_type': 'others',
                                   'currency_id': self.currency_01.id,
                                   'amount': 3000})]
        })
        with self.assertRaises(ValidationError):
            for amount_id in invoice_id.amount_ids:
                amount_id.currency_id = self.currency_02.id


