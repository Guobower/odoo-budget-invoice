# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from .utils import choices_tuple
import os


class InvoiceSummary(models.Model):
    _name = 'budget.invoice.summary'
    _rec_name = 'summary_no'
    _description = 'Invoice Summary'
    _order = 'id desc'

    # CHOICES
    # ----------------------------------------------------------
    STATES = choices_tuple(['draft', 'file generated', 'under certification',
                            'sent to finance', 'closed', 'canceled'], is_sorted=False)
    SECTIONS = choices_tuple(['cse', 'fan'], is_sorted=False)

    # BASIC FIELDS
    # ----------------------------------------------------------
    summary_no = fields.Char(string='Summary No',
                             default = lambda self: self._get_default_summary_no())
    state = fields.Selection(STATES, default='draft')
    section = fields.Selection(SECTIONS)

    # invoice_cert_date = fields.Date(string='Inv Certification Date')
    signed_date = fields.Date(string='Signed Date')
    closed_date = fields.Date(string='Closed Date')
    sent_finance_date = fields.Date(string='Sent to Finance Date')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    # TODO MUST NOT EDITABLE WHEN ON PROCESS, CHECK RULE ACCESS
    invoice_ids = fields.Many2many('budget.invoice.invoice',
                                  'budget_invoice_summary_invoice',
                                  'summary_id',
                                  'invoice_id')

    # TODO USE FOR TRANSFERING INVOICES
    tmp_invoice_ids = fields.One2many('budget.invoice.invoice',
                                  'invoice_summary_id',
                                  string="Invoices")
    attachment_ids = fields.One2many('ir.attachment',
                                     'invoice_summary_id',
                                     string="Attachments",
                                     auto_join=True)
    # CONSTRAINTS
    # ----------------------------------------------------------
    _sql_constraints = [
        (
            '_uniq_summary_no',
            'UNIQUE(summary_no)',
            'summary must be unqiue!',
            )
    ]
    # # MISC FUNCTIONS
    # # ----------------------------------------------------------
    # @api.one
    # def export_file(self):
    #     attachment_id = None
    #     filename=None
    #     if len(self.attachment_ids) > 0:
    #         attachment_id = self.attachment_ids[0].id
    #
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': '/web/content/%s/%s' % (attachment_id, filename),
    #         'target': 'self',
    #     }

    @api.model
    def _get_default_summary_no(self):
        from datetime import datetime as dt
        from dateutil.relativedelta import relativedelta
        now = dt.utcnow()
        month = '{:%^b}'.format(now)
        year = '{:%y}'.format(now)
        start = dt(now.year, now.month, 1)
        end = dt(now.year, now.month, 1) + relativedelta(months=1)
        # end should be the first day next month to make time consider as 23:59:99
        domain = [('create_date', '>=', fields.Datetime.to_string(start)),
                  ('create_date', '<', fields.Datetime.to_string(end))]

        summaries = self.env['budget.invoice.summary'].search(domain)
        if len(summaries) == 0:
            sr = 1
        else:
            sr = summaries[0].summary_no.split('-')[-1]
            sr = int(sr) + 1

        return 'IM-%s%s-%03d' % (month, year, sr)

    # @api.one
    # @api.returns('self', lambda value: value.id)
    # def copy(self, default=None):
    #     default = dict(default or {})
    #     default.update(summary_no=self._get_default_summary_no())
    #     default.update(invoice_ids = [(6, None, self.invoice_ids.mapped('id'))])
    #     return super(InvoiceSummary, self).copy(default)

    @api.one
    def generate_file(self):
        """
        generate/create a invoice summary
        set STATE to GENERATED
        """
        from openpyxl.drawing.image import Image
        from ..xlsx_creator.creator import Creator
        import tempfile, shutil
        # OPEN FORM TEMPLATE

        creator = Creator(section=self.section)
        wb, logo_img, signature_img = creator.get_context()

        # WORK SHEET MAIN
        # ----------------------------------------------------------
        row = 13
        column = 1
        sr = 1
        signature_coor = "B18" # B18
        logo_coor = "J1"     # J1
        ws = wb.get_sheet_by_name('main')

        ws.cell("C4").value = self.summary_no
        ws.cell("C5").value = fields.Datetime.from_string(self.create_date).strftime('%d-%b-%Y')

        # Create Table
        ws.insert_rows(row, len(self.invoice_ids) - 1)
        #No, Reg, Contractor, Invoice No, Contract, Revenue, OpEx, CapEx, Total Amt, Budget/Yr.
        #1 , 2  , 3,        , 4         , 5  6    , 7      , 8   , 9    , 10       , 11
        for r in self.invoice_ids:
            ws.cell(row=row, column=column).value = sr
            ws.cell(row=row, column=column + 1).value = r.region_id.alias.upper() or ''
            ws.cell(row=row, column=column + 2).value = r.contract_id.contractor_id.name or ''
            ws.cell(row=row, column=column + 3).value = r.invoice_no or ''
            ws.cell(row=row, column=column + 4).value = r.contract_id.contract_no or ''
            ws.cell(row=row, column=column + 5).value = r.revenue_amount or ''
            ws.cell(row=row, column=column + 6).value = r.opex_amount or ''
            ws.cell(row=row, column=column + 7).value = r.capex_amount or ''
            ws.cell(row=row, column=column + 8).value = r.invoice_amount or ''
            ws.cell(row=row, column=column + 9).value = r.task_id.task_no or fields.Datetime.from_string(r.rfs_date).strftime('%d-%b-%Y')

            row += 1
            sr += 1

        # INSERT HEADER LOGO AND SIGNATURE
        logo = Image(logo_img)
        signature = Image(signature_img)

        ws.add_image(logo, logo_coor)
        ws.add_image(signature, "%s" % signature_coor[0] + str(int(signature_coor[1:])+sr))

        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir,'%s.xlsx' % self.summary_no)
        wb.save(temp_file)

        # Attach generated document to filestore
        ir_attach = self.env['ir.attachment']
        full_path = os.path.join(temp_file)

        with open(full_path, 'r') as fp:
            data = fp.read().encode('base64')
        filename = os.path.split(full_path)[1]
        values = dict(
            name=filename,
            datas_fname=filename,
            res_id=self.id,
            res_model='budget.invoice.summary',
            type='binary',
            datas=data,
        )
        ir_attach.create(values)

        # Clear
        shutil.rmtree(temp_dir)

    # BUTTONS/TRANSITIONS
    # ----------------------------------------------------------
    @api.one
    def set2draft(self):
        self.state = 'draft'

    @api.one
    def set2file_generated(self):
        if not self.section in [i[0] for i in self.SECTIONS]:
            raise ValidationError('Section must be specified')
        elif len(self.invoice_ids) == 0:
            raise ValidationError('Empty Invoice List')

        self.generate_file()

        # Set related invoices state to "summary generated"
        for invoice in self.invoice_ids:
            invoice.signal_workflow('summary_generate')

        self.state = 'file generated'

    @api.one
    def set2under_certification(self):
        for invoice in self.invoice_ids:
            # invoice.invoice_cert_date = self.invoice_cert_date
            invoice.signal_workflow('certify')
        self.state = 'under certification'

    @api.one
    def set2sent_to_finance(self):
        # if self.invoice_cert_date is False:
        #     raise ValidationError('Invoice Certification Date is Required')
        if self.signed_date is False:
            raise ValidationError('Signed Date is Required')
        elif self.sent_finance_date is False:
            raise ValidationError('Sent to Finance Date is Required')

        for invoice in self.invoice_ids:
            invoice.sent_finance_date = self.sent_finance_date
            invoice.signed_date = self.signed_date
            # invoice.invoice_cert_date = self.invoice_cert_date
            invoice.signal_workflow('send_to_finance')
        self.state = 'sent to finance'

    @api.one
    def set2closed(self):
        if self.closed_date is False:
            raise ValidationError('Close Date is Required')
        for invoice in self.invoice_ids:
            invoice.closed_date = self.closed_date
            invoice.signal_workflow('close')
        self.state = 'closed'

    @api.one
    def set2canceled(self):
    # CONTINUE HERE
    # MUST DO A TRANSITION FOR RETURNING TO DRAFT
        for invoice in self.invoice_ids:
            invoice.signal_workflow('cancel')
        self.state = 'canceled'
