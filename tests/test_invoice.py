# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
import random

class TestInvoice(TransactionCase):
    at_install = False
    post_install = True


    def setUp(self):
        super(TestInvoice, self).setUp()
        self.contractor_id = self.env['res.partner'].create(
            {
                'is_budget_contractor': True,
                'name': 'Test Contractor 1',
                'alias': 'TC{}'.format(random.randint(0,1000))
            }
        )

        self.contract_id = self.env['budget.contractor.contract'].create(
            {
                'no': '35H/2003',
                'change_type': 'principal',
                'contractor_id': self.contractor_id.id
            }
        )
        invoice_vals = {
            'invoice_no': 'inv1',
            'contract_id': self.contract_id.id
        }
        self.invoice = self.env['budget.invoice.invoice'].new(invoice_vals)
        self.invoice._onchange_contract_id()
        invoice_vals.update(contractor_id=self.invoice.contractor_id.id)
        self.invoice = self.env['budget.invoice.invoice'].create(invoice_vals)

    def test_on_change_contract_id(self):
        """
            Check ONCHANGE Contract_id
        """
        self.assertTrue(self.invoice.contractor_id == self.contractor_id,'contract_contractor must be {}, given {}'.
                        format(self.contract_id.contractor_id, self.invoice.contractor_id))

    def test_duplicate(self):
        """
            Check DUPLICATE
            respect to invoice_no and contractor_id
        """
        self.invoice.signal_workflow('verify')

        contractor_id = self.env['res.partner'].create(
            {
                'is_budget_contractor': True,
                'name': 'Test Contractor 1',
                'alias': 'TC{}'.format(random.randint(0,1000))
            }
        )

        invoice0 = self.invoice

        invoice_vals = {
            'invoice_no': 'inv1',
            'contractor_id': self.contractor_id.id
        }

        invoice1 = self.env['budget.invoice.invoice'].create(invoice_vals)
        self.assertTrue(invoice1.problem == 'duplicate', 'problem must be duplicate, but given {}'.
                        format(invoice1.problem))

        invoice_vals = {
            'invoice_no': 'inv2',
            'contractor_id': self.contractor_id.id
        }
        invoice2 = self.env['budget.invoice.invoice'].create(invoice_vals)
        self.assertTrue(invoice2.problem != 'duplicate', 'problem must not be duplicate, but given {}'.
                        format(invoice2.problem))

        # Must not be Duplicate
        invoice1.write({
            'invoice_no': 'inv3'
        })
        self.assertTrue(invoice1.problem != 'duplicate', 'problem must not be duplicate, but given {}'.
                        format(invoice2.problem))
