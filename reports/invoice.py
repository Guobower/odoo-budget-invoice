# -*- coding: utf-8 -*-

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class PartnerXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, invoices):
        for obj in invoices:
            report_name = obj.invoice_no
            # One sheet by partner
            sheet = workbook.add_worksheet('test')
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.id, bold)


PartnerXlsx("report.budget.invoice.xlsx",
            'budget.invoice')