# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
import random


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

        self.contractor01_id = self.env['budget.contractor.contractor'].create(contractor_vals01)
        self.contractor02_id = self.env['budget.contractor.contractor'].create(contractor_vals02)

    def test_duplicate_create(self):
        invoice01_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': 'create duplicate invoice 01',
            'contractor_id': self.contractor01_id.id
        })

        invoice02_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': 'create duplicate invoice 01',
            'contractor_id': self.contractor01_id.id
        })

        self.assertEqual(invoice01_id.problem, 'duplicate')
        self.assertEqual(invoice02_id.problem, 'duplicate')

    def test_duplicate_unlink(self):
        invoice01_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': 'create duplicate invoice 01',
            'contractor_id': self.contractor01_id.id
        })

        invoice02_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': 'create duplicate invoice 01',
            'contractor_id': self.contractor01_id.id
        })

        invoice02_id.unlink()
        self.assertFalse(invoice01_id.problem)

    def test_duplicate_write_invoice_no(self):
        invoice01_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': 'write duplicate invoice 01',
            'contractor_id': self.contractor01_id.id
        })

        invoice02_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': 'write duplicate invoice 02',
            'contractor_id': self.contractor01_id.id
        })

        invoice02_id.write({
            'invoice_no': 'write duplicate invoice 01',
        })

        self.assertEqual(invoice01_id.problem, 'duplicate')
        self.assertEqual(invoice02_id.problem, 'duplicate')

        invoice02_id.write({
            'invoice_no': 'write duplicate invoice 02',
        })

        self.assertFalse(invoice01_id.problem)
        self.assertFalse(invoice02_id.problem)

    def test_duplicate_write_contractor_id(self):
        invoice01_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': 'write duplicate invoice 01',
            'contractor_id': self.contractor01_id.id
        })

        invoice02_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': 'write duplicate invoice 01',
            'contractor_id': self.contractor02_id.id
        })

        invoice02_id.write({
            'contractor_id': self.contractor01_id.id
        })

        self.assertEqual(invoice01_id.problem, 'duplicate')
        self.assertEqual(invoice02_id.problem, 'duplicate')
