# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
import random


class TestInvoiceCalculation01(TransactionCase):
    """
    Test Invoice function using percentage for the following
    penalty_percentage, on_hold_percentage, discount_percentage, other_deduction_percentage
    """
    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoiceCalculation01, self).setUp()

        self.invoice = self.env['budget.invoice.invoice'].create(
            {
                'invoice_no': 'test invoice 01',
                'penalty_percentage': 14,
                'on_hold_percentage': 13,
                'discount_percentage': 12,
                'other_deduction_percentage': 17,
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

    def test_calculation_capex_amount(self):
        # CAPEX AMOUNT
        expected_amount = 3000.00
        self.assertTrue(self.invoice.capex_amount == expected_amount, "Capex Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.capex_amount))

    def test_calculation_opex_amount(self):
        # OPEX AMOUNT
        expected_amount = 4000.00
        self.assertTrue(self.invoice.opex_amount == expected_amount, "Opex Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.opex_amount))

    def test_calculation_revenue_amount(self):
        # REVENUE AMOUNT
        expected_amount = 7000.00
        self.assertTrue(self.invoice.revenue_amount == expected_amount, "Revenue Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.revenue_amount))

    def test_calculation_cear_amount(self):
        # CEAR AMOUNT
        expected_amount = 10000.00
        self.assertTrue(self.invoice.cear_amount == expected_amount, "CEAR Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.cear_amount))

    def test_calculation_oear_amount(self):
        # OEAR AMOUNT
        expected_amount = 4000.00
        self.assertTrue(self.invoice.oear_amount == expected_amount, "OEAR Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.oear_amount))

    def test_calculation_invoice_amount(self):
        # INVOICE AMOUNT
        expected_amount = 14000.00
        self.assertTrue(self.invoice.invoice_amount == expected_amount, "Invoice Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.invoice_amount))

    def test_calculation_penalty_amount(self):
        # PENALTY AMOUNT
        expected_amount = 1960.00
        self.assertTrue(self.invoice.penalty_amount == expected_amount, "Penalty Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.penalty_amount))

    def test_calculation_discount_amount(self):
        # DISCOUNT AMOUNT
        expected_amount = 1680.00
        self.assertTrue(self.invoice.discount_amount == expected_amount, "Discount Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.discount_amount))

    def test_calculation_on_hold_amount(self):
        # ON HOLD AMOUNT
        expected_amount = 1820.00
        self.assertTrue(self.invoice.on_hold_amount == expected_amount, "On Hold Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.on_hold_amount))

    def test_calculation_other_deduction_amount(self):
        # ON HOLD AMOUNT
        expected_amount = 2380.00
        self.assertTrue(self.invoice.other_deduction_amount == expected_amount,
                        "Other Deduction Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.other_deduction_amount))

    def test_calculation_certified_invoice_amount(self):
        # CERTIFIED INVOICE AMOUNT
        expected_amount = 6160.00
        self.assertTrue(self.invoice.certified_invoice_amount == expected_amount,
                        "Certified Invoice Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.certified_invoice_amount))


class TestInvoiceCalculation02(TransactionCase):
    """
    Test Invoice function using explicit amount for the following
    input_penalty_amount, input_on_hold_amount, 
    input_discount_amount, input_other_deduction_amount
    """

    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoiceCalculation02, self).setUp()

        self.invoice = self.env['budget.invoice.invoice'].create(
            {
                'invoice_no': 'test invoice 02',
                'is_penalty_percentage': False,
                'is_on_hold_percentage': False,
                'is_discount_percentage': False,
                'is_other_deduction_percentage': False,
                'input_penalty_amount': 1960,
                'input_on_hold_amount': 1820,
                'input_discount_amount': 1680,
                'input_other_deduction_amount': 2380,
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

    def test_calculation_capex_amount(self):
        # CAPEX AMOUNT
        expected_amount = 3000.00
        self.assertTrue(self.invoice.capex_amount == expected_amount, "Capex Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.capex_amount))

    def test_calculation_opex_amount(self):
        # OPEX AMOUNT
        expected_amount = 4000.00
        self.assertTrue(self.invoice.opex_amount == expected_amount, "Opex Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.opex_amount))

    def test_calculation_revenue_amount(self):
        # REVENUE AMOUNT
        expected_amount = 7000.00
        self.assertTrue(self.invoice.revenue_amount == expected_amount, "Revenue Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.revenue_amount))

    def test_calculation_cear_amount(self):
        # CEAR AMOUNT
        expected_amount = 10000.00
        self.assertTrue(self.invoice.cear_amount == expected_amount, "CEAR Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.cear_amount))

    def test_calculation_oear_amount(self):
        # OEAR AMOUNT
        expected_amount = 4000.00
        self.assertTrue(self.invoice.oear_amount == expected_amount, "OEAR Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.oear_amount))

    def test_calculation_invoice_amount(self):
        # INVOICE AMOUNT
        expected_amount = 14000.00
        self.assertTrue(self.invoice.invoice_amount == expected_amount, "Invoice Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.invoice_amount))

    def test_calculation_penalty_amount(self):
        # PENALTY AMOUNT
        expected_amount = 1960.00
        self.assertTrue(self.invoice.penalty_amount == expected_amount, "Penalty Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.penalty_amount))

    def test_calculation_discount_amount(self):
        # DISCOUNT AMOUNT
        expected_amount = 1680.00
        self.assertTrue(self.invoice.discount_amount == expected_amount, "Discount Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.discount_amount))

    def test_calculation_on_hold_amount(self):
        # ON HOLD AMOUNT
        expected_amount = 1820.00
        self.assertTrue(self.invoice.on_hold_amount == expected_amount, "On Hold Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.on_hold_amount))

    def test_calculation_other_deduction_amount(self):
        # ON HOLD AMOUNT
        expected_amount = 2380.00
        self.assertTrue(self.invoice.other_deduction_amount == expected_amount,
                        "Other Deduction Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.other_deduction_amount))

    def test_calculation_certified_invoice_amount(self):
        # CERTIFIED INVOICE AMOUNT
        expected_amount = 6160.00
        self.assertTrue(self.invoice.certified_invoice_amount == expected_amount,
                        "Certified Invoice Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.certified_invoice_amount))
