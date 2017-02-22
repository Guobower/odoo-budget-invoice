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
                'alias': 'TC{}'.format(random.randint(0, 1000))
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
        # self.invoice = self.env['budget.invoice.invoice'].new(invoice_vals)
        # self.invoice._onchange_contract_id()
        # invoice_vals.update(contractor_id=self.invoice.contractor_id.id)
        self.invoice = self.env['budget.invoice.invoice'].create(invoice_vals)

    def test_duplicate(self):
        """

            Check DUPLICATE
            respect to invoice_no and contractor_id
        """
        # TODO VERIFY TEST
        self.invoice.signal_workflow('verify')

        contractor_id = self.env['res.partner'].create(
            {
                'is_budget_contractor': True,
                'name': 'Test Contractor 1',
                'alias': 'TC{}'.format(random.randint(0, 1000))
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

    def test_computations(self):
        invoice = self.env['budget.invoice.invoice'].create(
            {
                'invoice_no': 'test invoice',
                'penalty_percentage': 14,
                'on_hold_percentage': 13,
                'discount_percentage': 12,
                'amount_ids': [(0, 0, {'budget_type': 'capex',
                                       'invoice_type': 'others',
                                       'payment_type': 'others',
                                       'amount': 3000}),
                               (0, 0, {'budget_type': 'opex',
                                       'invoice_type': 'others',
                                       'payment_type': 'others',
                                       'amount': 4000}),
                               (0, 0, {'budget_type': 'revenue',
                                       'invoice_type': 'others',
                                       'payment_type': 'others',
                                       'amount': 7000})
                               ],
                'cear_allocation_ids': [(0, 0, {
                    'amount': 10000
                })]
            }
        )

        # CAPEX AMOUNT
        self.assertTrue(invoice.capex_amount == 3000.00, "Capex Amount must be {}, Given {}".\
                        format(14000.00,invoice.capex_amount))

        # OPEX AMOUNT
        self.assertTrue(invoice.opex_amount == 4000.00, "Opex Amount must be {}, Given {}".\
                        format(4000.00,invoice.opex_amount))

        # REVENUE AMOUNT
        self.assertTrue(invoice.revenue_amount == 7000.00, "Revenue Amount must be {}, Given {}".\
                        format(7000.00,invoice.revenue_amount))

        # CEAR AMOUNT
        self.assertTrue(invoice.cear_amount == 10000.00, "CEAR Amount must be {}, Given {}".\
                        format(10000.00,invoice.cear_amount))
        # OEAR AMOUNT
        self.assertTrue(invoice.oear_amount == 4000.00, "OEAR Amount must be {}, Given {}".\
                        format(4000.00,invoice.oear_amount))

        # INVOICE AMOUNT
        self.assertTrue(invoice.invoice_amount == 14000.00, "Invoice Amount must be {}, Given {}".\
                        format(14000.00,invoice.invoice_amount))

        # PENALTY AMOUNT
        self.assertTrue(invoice.penalty_amount == 1960.00, "Penalty Amount must be {}, Given {}".\
                        format(1960.00,invoice.penalty_amount))

        # DISCOUNT AMOUNT
        self.assertTrue(invoice.discount_amount == 1680.00, "Discount Amount must be {}, Given {}".\
                        format(1680.00,invoice.discount_amount))

        # ON HOLD AMOUNT
        # HOLD AMOUNT is against certified amount
        self.assertTrue(invoice.on_hold_amount == 1346.80, "On Hold Amount must be {}, Given {}".\
                        format(1346.80,invoice.on_hold_amount))

        # CERTIFIED INVOICE AMOUNT
        self.assertTrue(invoice.certified_invoice_amount == 10360.00, "Certified Invoice Amount must be {}, Given {}".\
                        format(10360.00,invoice.certified_invoice_amount))
