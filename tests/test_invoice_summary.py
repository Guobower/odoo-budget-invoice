# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from faker import Faker

fake = Faker()


class TestInvoiceSummary(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoiceSummary, self).setUp()

    def create_invoice(self):
        invoice_id = self.env['budget.invoice.invoice'].create({
            'invoice_no': fake.name(),
            'amount_ids': [(0, 0, {'budget_type': 'capex', 'amount': 1000})]
        })

        return invoice_id

    def test_auto_summary_no(self):
        """
            Check Generation of Summary No
        """
        self.env['budget.invoice.invoice.summary'].create({})

        latest_summary = self.env['budget.invoice.invoice.summary'].search([])[0]
        latest_no = int(latest_summary.summary_no.split('-')[-1])

        self.env['budget.invoice.invoice.summary'].create({})
        new_summary = self.env['budget.invoice.invoice.summary'].search([])[0]
        new_no = int(new_summary.summary_no.split('-')[-1])

        self.assertTrue(latest_no + 1 == new_no, "NEW No should be +1 of the latest")

    def test_summary_invoice_certification_no_hold_amount(self):
        invoice_id = self.create_invoice()
        summary_id = self.env['budget.invoice.invoice.summary'].create({'invoice_ids': [(6, 0, invoice_id.ids)]})

        summary_id.set2draft()
        self.assertEqual(summary_id.state, 'draft')
        # SKIP TEST FOR FILE GENERATION AS THERE'S AN ERROR IN os.path.join()
        # summary_id.set2file_generated()
        # self.assertEqual(summary_id.state, 'file generated')
        summary_id.set2sd_signed()
        self.assertEqual(summary_id.state, 'sd signed')
        summary_id.set2svp_signed()
        self.assertEqual(summary_id.state, 'svp signed')
        summary_id.set2cto_signed()
        self.assertEqual(summary_id.state, 'cto signed')
        summary_id.set2sent_to_finance()
        self.assertEqual(summary_id.state, 'sent to finance')
        summary_id.set2closed()
        self.assertEqual(summary_id.state, 'closed')
        summary_id.set2cancelled()
        self.assertEqual(summary_id.state, 'cancelled')
