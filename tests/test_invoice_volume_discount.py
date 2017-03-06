# -*- coding: utf-8 -*-

from datetime import datetime as dt
from odoo.tests.common import TransactionCase

from ..models.invoice_volume_discount import check_overlapping_dates

class TestInvoiceVolumeDiscount(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoiceVolumeDiscount, self).setUp()

    def test_check_overlapping_dates(self):
        """
            Check Method for cehcking overlapping dates
        """

        # SET 1
        a = dt(2017, 1, 1).strftime('%Y-%m-%d')
        b = dt(2017, 3, 1).strftime('%Y-%m-%d')
        c = dt(2017, 2, 28).strftime('%Y-%m-%d')
        d = dt(2017, 4, 1).strftime('%Y-%m-%d')

        self.assertTrue(check_overlapping_dates(a,b,c,d) == 2, "expected 2 but given {}".format(check_overlapping_dates(a,b,c,d)))

        self.assertTrue(check_overlapping_dates(c,d,a,b) == 2, "expected 2 but given {}".format(check_overlapping_dates(a,b,c,d)))
