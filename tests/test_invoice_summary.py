# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestInvoiceSummary(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoiceSummary, self).setUp()

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
