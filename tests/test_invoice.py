# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestInvoice(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestInvoice, self).setUp()

    def test_compute_problem_duplicate(self):
        """
            Check Problem Duplicate Conditions
        """
        task = self.env['budget.capex.task'].create(
            {
                u'authorized_amount': 100,
                u'task_no': u'Task - 1',
                u'total_amount': 50  # FN actual
            }
        )

        # authorized amount = 100
        # FN amount = 50
        # IM amount = 25 + 25 + 25
        task.write({
            'invoice_ids': [(0, 0, {
                'invoice_no': 'Invoice #',
                'revenue_amount': 25,
                'opex_amount': 25,
                'capex_amount': 25
            })]
        })
        # self.assertTrue(task.invoice_ids[0].problem == 'overrun')

        invoice_a = self.env['budget.invoice.invoice'].create(
            {'invoice_no': 'dup_check'}
        )
        invoice_b = self.env['budget.invoice.invoice'].create(
            {'invoice_no': 'dup_check'}
        )

        # Check duplicate
        self.assertTrue(invoice_a.problem != 'duplicate')
        self.assertTrue(invoice_b.problem == 'duplicate')

    def test_compute_problem_task_overrun(self):
        """
            Check Problem Task Overrun Conditions
        """
        task = self.env['budget.capex.task'].create(
            {
                u'authorized_amount': 200,
                u'task_no': u'Task - 1',
                u'total_amount': 50  # FN actual
            }
        )

        # authorized amount = 100
        # FN amount = 50
        # IM amount = 25 + 25 + 25 + 25 + 25 + 25

        task.write({
            'invoice_ids': [
                (0, 0, {'invoice_no': 'Invoice 1',
                        'revenue_amount': 25,
                        'opex_amount': 25,
                        'capex_amount': 25
                        })
            ]
        })

        task.write({
            'invoice_ids': [
                (0, 0, {'invoice_no': 'Invoice 2',
                        'revenue_amount': 25,
                        'opex_amount': 25,
                        'capex_amount': 25
                        })
            ]
        })

        for invoice in task.invoice_ids:
            invoice.signal_workflow('verify')

        self.assertTrue(task.utilized_amount == 150.00, 'Utilized Amount {} is not 150.00'. \
                        format(task.utilized_amount))
        self.assertTrue(task.problem == 'ok', 'Must be OK Utilized Amount {}; Authorized Amount {}'. \
                        format(task.utilized_amount, task.authorized_amount))

        task.write({
            'invoice_ids': [
                (0, 0, {'invoice_no': 'Invoice 3',
                        'revenue_amount': 25,
                        'opex_amount': 25,
                        'capex_amount': 25
                        })
            ]
        })
        for invoice in task.invoice_ids:
            invoice.signal_workflow('verify')

        # Task Overrun
        self.assertTrue(task.problem == 'overrun', 'Must be Overrun Utilized Amount {}; Authorized Amount {}'. \
                        format(task.utilized_amount, task.authorized_amount))

    def test_compute_problem_invoice_overrun(self):
        """
            Check Problem Invoice Overrun Conditions
        """
        task = self.env['budget.capex.task'].create(
            {
                u'authorized_amount': 200,
                u'task_no': u'Task - 1',
                u'total_amount': 50  # FN actual
            }
        )

        # authorized amount = 100
        # FN amount = 50
        # IM amount = 25 + 25 + 25 + 25 + 25 + 25

        task.write({
            'invoice_ids': [
                (0, 0, {'invoice_no': 'Invoice 1',
                        'revenue_amount': 25,
                        'opex_amount': 25,
                        'capex_amount': 25
                        })
            ]
        })

        task.write({
            'invoice_ids': [
                (0, 0, {'invoice_no': 'Invoice 2',
                        'revenue_amount': 150,
                        'opex_amount': 0,
                        'capex_amount': 0
                        })
            ]
        })

        for inv in task.invoice_ids:
            inv.signal_workflow('verify')

        invoice = self.env['budget.invoice.invoice'].create(
            {'invoice_no': 'Invoice 3',
             'revenue_amount': 25,
             'opex_amount': 25,
             'capex_amount': 25,
             'task_id': task.id
             }
        )

        # Task Overrun

        self.assertTrue(invoice.problem == 'overrun', 'Must be Overrun Utilized Amount {}; Authorize Amount {}'. \
                        format(invoice.task_id.utilized_amount, invoice.task_id.authorized_amount))

    def test_compute_certified_invoice_amount(self):
        """
        field dependencies: 'opex_amount', 'capex_amount', 'revenue_amount', 'penalty_amount',
                            'on_hold_amount'
        affected fields: 'certified_invoice_amount'
        """
        invoice_a = self.env['budget.invoice.invoice'].create(
            {
                'invoice_no': 'invoice_qwefa',
                'revenue_amount': 1000.00,
                'opex_amount': 1000.00,
                'capex_amount': 1000.00,
                'penalty_amount': 1000.00,
                'on_hold_amount': 500
            }
        )

        self.assertTrue(invoice_a.certified_invoice_amount == 1500.00)

    def test_workflow_hold_amount(self):
        """
        field dependencies: 'opex_amount', 'capex_amount', 'revenue_amount', 'penalty'
        affected fields: 'invoice_amount'
        """

        invoice = self.env['budget.invoice.invoice'].create(
            {}
        )
