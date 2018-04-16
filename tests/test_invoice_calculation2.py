from odoo.tests.common import TransactionCase
import random
import math
from datetime import datetime

class TestInvoiceCalculation03(TransactionCase):
    """
    Test to check capex_amount, capex_aed_amount, opex_amount,
    opex_aed_amount, revenue_amount, revenue_aed_amount
    invoice_amount, invoice_aed_amount
    """

    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoiceCalculation03, self).setUp()

        curr_id = self.env['res.currency'].search([('name', '=', 'QWE')],
                                                      limit=1).id
        if not curr_id:
            currency_id = self.env['res.currency'].create({
                'name': 'QWE',
                'symbol': 'QWE',
                'rate_ids': [(0, 0, {
                    'name': datetime.today(),
                    'rate': 0.272183,
                    'company_id': 1
                })]
            })
            curr_id = currency_id.id

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
                'currency_id': curr_id,
                'amount_ids': [(0, 0, {'budget_type': 'capex',
                                       'invoice_type': 'others',
                                       'payment_type': 'others',
                                       'amount': 3000,
                                       'currency_id': curr_id}),
                               (0, 0, {'budget_type': 'opex',
                                       'invoice_type': 'others',
                                       'payment_type': 'others',
                                       'amount': 4000,
                                       'currency_id': curr_id}),
                               (0, 0, {'budget_type': 'revenue',
                                       'invoice_type': 'others',
                                       'payment_type': 'others',
                                       'amount': 7000,
                                       'currency_id': curr_id})
                               ],
                'cear_allocation_ids': [(0, 0, {
                    'amount': 3000,
                    'currency_id': curr_id
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

    def test_calculation_invoice_amount(self):
        # INVOICE AMOUNT
        expected_amount = 14000.00
        self.assertTrue(self.invoice.invoice_amount == expected_amount, "Invoice Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.invoice_amount))

    def test_calculation_capex_aed_amount(self):
        # CAPEX AED AMOUNT
        expected_amount = 11022.00

        self.assertTrue(self.invoice.capex_aed_amount == expected_amount, "Capex Amount (AED) must be {}, Given {}".
                        format(expected_amount, self.invoice.capex_aed_amount))

    def test_calcuation_opex_aed_amount(self):
        # OPEX AED AMOUNT
        expected_amount = 14695.99
        self.assertTrue(self.invoice.opex_aed_amount == expected_amount, "Opex Amount (AED) must be {}, Given {}".
                        format(expected_amount, self.invoice.opex_aed_amount))

    def test_calculation_revenue_aed_amount(self):
        # REVENUE AED AMOUNT
        expected_amount = 25717.99
        self.assertTrue(self.invoice.revenue_aed_amount == expected_amount, "Revenue Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.revenue_aed_amount))

    def test_calculation_invoice_aed_amount(self):
        # INVOICE AED AMOUNT
        expected_amount = 51435.98
        self.assertTrue(self.invoice.invoice_aed_amount == expected_amount, "Invoice Amount must be {}, Given {}".
                        format(expected_amount, self.invoice.invoice_aed_amount))

    def test_calculation_certified_aed_invoice_amount(self):
        # CERTIFIED INVOICE AED AMOUNT
        expected_amount = 22631.83
        self.assertTrue(self.invoice.certified_aed_invoice_amount == expected_amount,
                        "Certified invoice amount in aed must be "
                        "{}, given {}". format(expected_amount, self.invoice.certified_aed_invoice_amount))

    def test_calculation_certified_aed_capex_amount(self):
        # CERTIFIED CAPEX AED AMOUNT
        expected_amount = 4849.68
        self.assertTrue(self.invoice.certified_aed_capex_amount == expected_amount,
                        "Certified capex amount in aed must be "
                        "{}, given {}". format(expected_amount, self.invoice.certified_aed_capex_amount))

    def test_calculation_certified_aed_opex_amount(self):
        # CERTIFIED OPEX AED AMOUNT
        expected_amount = 6466.24
        self.assertTrue(self.invoice.certified_aed_opex_amount == expected_amount,
                        "Certified opex amount in aed must be {},"
                        " given {}". format(expected_amount, self.invoice.certified_aed_opex_amount))

    def test_calculation_certified_aed_revenue_amount(self):
        # CERTIFIED REVENUE AED AMOUNT
        expected_amount = 11315.92
        self.assertTrue(self.invoice.certified_aed_revenue_amount == expected_amount,
                        "Certified revenue amount in aed must be"
                        " {}, given {}". format(expected_amount, self.invoice.certified_aed_revenue_amount))

    def test_calculation_penalty_aed_amount(self):
        # PENALTY AED AMOUNT
        expected_amount = 7201.04
        self.assertTrue(self.invoice.penalty_aed_amount == expected_amount,
                        "Penalty amount in aed must be "
                        "{}, given {}". format(expected_amount, self.invoice.penalty_aed_amount))

    def test_calculation_discount_aed_amount(self):
        # DISCOUNT AED AMOUNT
        expected_amount = 6172.32
        self.assertTrue(self.invoice.discount_aed_amount == expected_amount,
                        "Discount amount in aed must be "
                        "{}, given {}". format(expected_amount, self.invoice.discount_aed_amount))

    def test_calculation_on_hold_aed_amount(self):
        # DISCOUNT AED AMOUNT
        expected_amount = 6686.68
        self.assertTrue(self.invoice.on_hold_aed_amount == expected_amount,
                        "On hold amount in aed must be "
                        "{}, given {}". format(expected_amount, self.invoice.on_hold_aed_amount))

    def test_calculation_other_deduction_aed_amount(self):
        # DISCOUNT AED AMOUNT
        expected_amount = 8744.12
        self.assertTrue(self.invoice.other_deduction_aed_amount == expected_amount,
                        "Other deduction amount in aed must be "
                        "{}, given {}". format(expected_amount, self.invoice.other_deduction_aed_amount))

    def test_single_currency_in_invoice(self):
        usd_id = self.env["res.currency"].search([('name', '=', 'USD')], limit=1).id
        try:
            cear_id = self.env["budget.invoice.cear.allocation"].create({
                'amount': 3000,
                'currency_id': usd_id
            })
            if not cear_id:
                self.assertTrue(added, "CEAR with another currency must not be allowed to add.")
        except:
            
        finally:
            self.assertTrue(added, "CEAR with another currency must not be allowed to add.")

