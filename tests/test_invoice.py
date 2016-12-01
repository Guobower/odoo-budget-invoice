# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


# TODO Test Transition
# TODO Test Compute Field
# TODO Problem


# class TestInvoice(TransactionCase):
#     at_install = False
#     post_install = True
#
#     def setUp(self):
#         super(TestInvoice, self).setUp()
#
#     def test_compute_problem(self):
#         """
#             Check Problem Conditions
#         """
#         task = self.env['budget.capex.task'].create(
#             {
#                 u'authorized_amount': 100,
#                 u'task_no': u'Task - 1',
#                 u'total_amount': 50        # FN actual
#             }
#         )
#
#         # authorized amount = 100
#         # FN amount = 50
#         # IM amount = 25 + 25 + 25
#         task.write({
#             'invoice_ids': [(0, 0, {
#                 'invoice_no': 'Invoice #',
#                 'revenue_amount': 25,
#                 'opex_amount': 25,
#                 'capex_amount': 25
#             })]
#         })
#         self.assertTrue(task.invoice_ids[0].problem == 'overrun')
#
#     def test_compute_invoice_amount(self):
#         """
#         field dependencies: 'opex_amount', 'capex_amount', 'revenue_amount', 'penalty'
#         affected fields: 'invoice_amount'
#         """
#         pass
#
#     def test_workflow(self):
#         """
#         field dependencies: 'opex_amount', 'capex_amount', 'revenue_amount', 'penalty'
#         affected fields: 'invoice_amount'
#         """
#         pass
