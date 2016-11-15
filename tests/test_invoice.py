# -*- coding: utf-8 -*-

from odoo.tests import common


class TestInvoice(common.TransactionCase):
    def setUp(self):
        super(TestInvoice, self).setUp()

    def test_fields(self):
        req_fields = [
            'region_id',
            'related_authorized_amount',
            'company_currency_id',
            'expense_code',
            'revenue_amount',
            'cost_center',
            'contract_id',
            'invoice_summary_id',
            'invoice_amount',
            'penalty',
            'state',
            'proj_no',
            'capex_amount',
            'description',
            'end_date',
            'invoice_type',
            'opex_amount',
            'remarks',
            'invoice_no',
            'task_id',
            'payment_type',
            'problem',

            # Date fields
            'invoice_date',
            'invoice_cert_date',
            'rfs_date',
            'received_date',
            'signed_date',
            'sent_finance_date',
            'reject_date',
            'start_date',
            'closed_date',

            # Task related fields
            'related_utilized_amount',
            'related_total_amount',
            'related_contractor_id',
        ]
        model = self.env['budget.invoice']
        fields = model.fields_get_keys()

        set_fields = set(fields)
        set_req_fields = set(req_fields)
        self.assertTrue(False)
        self.assertFalse(True)
        self.assertFalse(len(set_fields & set_req_fields) == len(set(set_req_fields)),
                        'missing required fields %s' % ', '.join(set_req_fields - set_fields))

    def test_compute_problem(self):
        """
        field dependencies: 'invoice_type', 'invoice_no', 'invoice_amount',
                 'task_id.authorized_amount', 'task_id.utilized_amount', 'task_id.category'
        affected fields: 'problem'
        """
        pass

    def test_compute_invoice_amount(self):
        """
        field dependencies: 'opex_amount', 'capex_amount', 'revenue_amount', 'penalty'
        affected fields: 'invoice_amount'
        """
        pass

    # BUTTONS/TRANSITIONS
    # ----------------------------------------------------------
    def test_set2draft(self):
        pass
        #self.state = 'draft'

    def test_set2verified(self):
        pass
#        self.state = 'verified'

    def test_set2summary_generated(self):
        pass
#        self.state = 'summary generated'

    def test_set2under_certification(self):
        pass
#        self.state = 'under certification'

    def test_set2sent_to_finance(self):
        pass
#        self.state = 'sent to finance'

    def test_set2closed(self):
        pass
 #       self.state = 'closed'

    def test_set2on_hold(self):
        pass
#        self.state = 'on hold'

    def test_set2rejected(self):
        pass
#        self.state = 'rejected'
