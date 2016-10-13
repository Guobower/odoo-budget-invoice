# -*- coding: utf-8 -*-
from openerp import http

# class BudgetInvoice(http.Controller):
#     @http.route('/budget_invoice/budget_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/budget_invoice/budget_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('budget_invoice.listing', {
#             'root': '/budget_invoice/budget_invoice',
#             'objects': http.request.env['budget_invoice.budget_invoice'].search([]),
#         })

#     @http.route('/budget_invoice/budget_invoice/objects/<model("budget_invoice.budget_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('budget_invoice.object', {
#             'object': obj
#         })