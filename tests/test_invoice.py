# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
import random

# TODO test_compute_problem_invoice_overrun
# TODO test_compute_problem_cear_overrun


class TestInvoice(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoice, self).setUp()
        # DUMMY CONTRACTOR
        contractor_vals01 = {
            'name': 'Test Contractor 1',
            'alias': 'TC{}'.format(random.randint(0, 1000)),
            # DUMMY CONTRACT
            # with capex and opex part
            'contract_ids': [(0, 0, {'no': '99H/9999',
                                     'change_type': 'principal',
                                     'is_capex': True,
                                     'is_opex': True
                                     }),
                             ]
        }
        contractor_vals02 = {
            'name': 'Test Contractor 2',
            'alias': 'TC{}'.format(random.randint(0, 1000)),
            # DUMMY CONTRACT
            # with capex and opex part
            'contract_ids': [(0, 0, {'no': '100H/9999',
                                     'change_type': 'principal',
                                     'is_capex': True,
                                     'is_opex': True
                                     }),
                             ]
        }

        self.contractor_id = self.env['budget.contractor.contractor'].create(contractor_vals01)
        self.contractor_id = self.env['budget.contractor.contractor'].create(contractor_vals02)
        self.env.cr.commit()

    # def test_duplicate_different_vendor_same_invoice_no(self):
    #     """
    #         Check DUPLICATE
    #         Must not be True
    #         Invoices with same invoice_no but different in contractor is not duplicate
    #     """
    #
    #     invoice_vals01 = {
    #         'invoice_no': 'diff_vendor_same_invoice_no',
    #         'contract_id': self.env['budget.contractor.contract'].search([])[0].id,
    #         'contractor_id': self.env['budget.contractor.contract'].search([])[0].contractor_id.id
    #     }
    #     invoice_vals02 = {
    #         'invoice_no': 'diff_vendor_same_invoice_no',
    #         'contract_id': self.env['budget.contractor.contract'].search([])[1].id,
    #         'contractor_id': self.env['budget.contractor.contract'].search([])[1].contractor_id.id
    #     }
    #
    #     invoice01 = self.env['budget.invoice.invoice'].create(invoice_vals01)
    #     invoice01.signal_workflow('verify')
    #     self.env.cr.commit()
    #
    #     invoice02 = self.env['budget.invoice.invoice'].create(invoice_vals02)
    #     self.env.cr.commit()
    #
    #     self.assertTrue(invoice01.problem != 'duplicate', 'problem must not be duplicate, but given {}'.
    #                     format(invoice01.problem))
    #
    #     self.assertTrue(invoice02.problem != 'duplicate', 'problem must not be duplicate, but given {}'.
    #                     format(invoice02.problem))
    #
    # def test_duplicate_same_vendor_same_invoice_no(self):
    #     """
    #         Check DUPLICATE
    #         Must be True
    #         Invoices with same invoice_no and same contractor is duplicate
    #     """
    #
    #     invoice_vals01 = {
    #         'invoice_no': 'same_vendor_same_invoice_no',
    #         'contract_id': self.env['budget.contractor.contract'].search([])[1].id,
    #         'contractor_id': self.env['budget.contractor.contract'].search([])[1].contractor_id.id
    #     }
    #     invoice_vals02 = {
    #         'invoice_no': 'same_vendor_same_invoice_no',
    #         'contract_id': self.env['budget.contractor.contract'].search([])[1].id,
    #         'contractor_id': self.env['budget.contractor.contract'].search([])[1].contractor_id.id
    #     }
    #
    #     invoice01 = self.env['budget.invoice.invoice'].create(invoice_vals01)
    #     invoice01.signal_workflow('verify')
    #     self.env.cr.commit()
    #
    #     invoice02 = self.env['budget.invoice.invoice'].create(invoice_vals02)
    #     self.env.cr.commit()
    #
    #     self.assertTrue(invoice01.problem == 'duplicate', 'problem must be duplicate, but given {}'.
    #                     format(invoice01.problem))
    #
    #     self.assertTrue(invoice02.problem == 'duplicate', 'problem must be duplicate, but given {}'.
    #                     format(invoice02.problem))

    # def test_duplicate_updating(self):
    #     """
    #         Check DUPLICATE
    #         Must be True
    #         Invoices with same invoice_no and same contractor is duplicate
    #     """
    #
    #     invoice_vals01 = {
    #         'invoice_no': 'updating',
    #         'contract_id': self.env['budget.contractor.contract'].search([])[0].id
    #     }
    #     invoice_vals02 = {
    #         'invoice_no': 'updating',
    #         'contract_id': self.env['budget.contractor.contract'].search([])[0].id
    #     }
    #
    #     invoice01 = self.env['budget.invoice.invoice'].create(invoice_vals01)
    #     invoice01.signal_workflow('verify')
    #     self.env.cr.commit()
    #
    #     invoice02 = self.env['budget.invoice.invoice'].create(invoice_vals02)
    #     self.env.cr.commit()
    #
    #     invoice01.write({
    #         'invoice_no': 'updated'
    #     })
    #     self.env.cr.commit()
    #
    #     self.assertTrue(invoice01.problem != 'duplicate', 'problem must be duplicate, but given {}'.
    #                     format(invoice01.problem))
    #
    #     self.assertTrue(invoice02.problem != 'duplicate', 'problem must be duplicate, but given {}'.
    #                     format(invoice02.problem))

    def test_computations_no_other_deduction(self):
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
        self.assertTrue(invoice.capex_amount == 3000.00, "Capex Amount must be {}, Given {}". \
                        format(14000.00, invoice.capex_amount))

        # OPEX AMOUNT
        self.assertTrue(invoice.opex_amount == 4000.00, "Opex Amount must be {}, Given {}". \
                        format(4000.00, invoice.opex_amount))

        # REVENUE AMOUNT
        self.assertTrue(invoice.revenue_amount == 7000.00, "Revenue Amount must be {}, Given {}". \
                        format(7000.00, invoice.revenue_amount))

        # CEAR AMOUNT
        self.assertTrue(invoice.cear_amount == 10000.00, "CEAR Amount must be {}, Given {}". \
                        format(10000.00, invoice.cear_amount))
        # OEAR AMOUNT
        self.assertTrue(invoice.oear_amount == 4000.00, "OEAR Amount must be {}, Given {}". \
                        format(4000.00, invoice.oear_amount))

        # INVOICE AMOUNT
        self.assertTrue(invoice.invoice_amount == 14000.00, "Invoice Amount must be {}, Given {}". \
                        format(14000.00, invoice.invoice_amount))

        # PENALTY AMOUNT
        self.assertTrue(invoice.penalty_amount == 1960.00, "Penalty Amount must be {}, Given {}". \
                        format(1960.00, invoice.penalty_amount))

        # DISCOUNT AMOUNT
        self.assertTrue(invoice.discount_amount == 1680.00, "Discount Amount must be {}, Given {}". \
                        format(1680.00, invoice.discount_amount))

        # ON HOLD AMOUNT
        # HOLD AMOUNT is against certified amount
        self.assertTrue(invoice.on_hold_amount == 1346.80, "On Hold Amount must be {}, Given {}". \
                        format(1346.80, invoice.on_hold_amount))

        # CERTIFIED INVOICE AMOUNT
        self.assertTrue(invoice.certified_invoice_amount == 10360.00, "Certified Invoice Amount must be {}, Given {}". \
                        format(10360.00, invoice.certified_invoice_amount))
