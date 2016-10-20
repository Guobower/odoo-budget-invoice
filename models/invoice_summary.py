# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from .utils import choices_tuple
import os


class InvoiceSummary(models.Model):
    _name = 'budget.invoice.summary'
    _rec_name = 'summary_no'
    _description = 'Invoice Summary'
    _order = 'id desc'

    # CHOICES
    # ----------------------------------------------------------
    STATES = choices_tuple(['draft', 'generated', 'sent to finance', 'closed', 'canceled'], is_sorted=False)
    SECTIONS = choices_tuple(['cse', 'fan'], is_sorted=False)

    # BASIC FIELDS
    # ----------------------------------------------------------
    state = fields.Selection(STATES, default='draft')
    section = fields.Selection(SECTIONS)
    summary_no = fields.Char(string='Summary No',
                             default = lambda self: self._get_default_summary_no())

    # RELATIONSHIPS
    # ----------------------------------------------------------
    invoice_ids = fields.One2many('budget.invoice',
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
            ),
    ]
    # MISC FUNCTIONS
    # ----------------------------------------------------------
    @api.one
    def export_file(self):
        attachment_id = None
        filename=None
        if len(self.attachment_ids) > 0:
            attachment_id = self.attachment_ids[0].id

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s' % (attachment_id, filename),
            'target': 'self',
        }

    @api.model
    def _get_default_summary_no(self):
        import datetime
        from datetime import datetime as dt
        now = dt.utcnow()
        month = '{:%^b}'.format(now)
        year = '{:%y}'.format(now)
        start = dt(now.year, now.month, 1)
        end = dt(now.year, now.month + 1, 1) - datetime.timedelta (days = 1)
        domain = [('create_date', '>=', fields.Datetime.to_string(start)),
                  ('create_date', '<=', fields.Datetime.to_string(end))]

        summaries = self.env['budget.invoice.summary'].search(domain)
        if len(summaries) == 0:
            sr = 1
        else:
            sr = summaries[0].summary_no.split('-')[-1]
            sr = int(sr) + 1

        return 'IM-%s%s-%03d' % (month, year, sr)

    # dt = fields.Datetime.to_string(datetime.utcnow() - timedelta(days=7))
    # repartition = record.channel_ids.rating_get_grades([('create_date', '>=', dt)])
    # BUTTONS/TRANSITIONS
    # ----------------------------------------------------------
    @api.one
    def set2generated(self):
        """
        generate/create a invoice summary
        set STATE to GENERATED
        """
        if not self.section in [i[0] for i in self.SECTIONS]:
            raise ValidationError('Section must be specified')

        from ..xlsx_creator.creator import Creator
        import tempfile, shutil
        # OPEN FORM TEMPLATE

        creator = Creator(section=self.section)
        wb = creator.get_wb()
        # WORK SHEET MAIN
        # ----------------------------------------------------------
        row = 7
        column = 1
        sr = 1
        ws = wb.get_sheet_by_name('main')

        # Create Table
        ws.insert_rows(row, len(self.invoice_ids) - 1)
        #No, Reg, Contractor, Invoice No, Contract, Revenue, OpEx, CapEx, Total Amt, Budget/Yr.
        #1 , 2  , 3,        , 4         , 5  6    , 7      , 8   , 9    , 10       , 11
        for r in self.invoice_ids:
            ws.cell(row=row, column=column).value = sr
            ws.cell(row=row, column=column + 1).value = r.region.upper() or ''
            ws.cell(row=row, column=column + 2).value = r.compute_contractor_id.name or ''
            ws.cell(row=row, column=column + 3).value = r.invoice_no or ''
            ws.cell(row=row, column=column + 4).value = r.contract_id.contract_no or ''
            ws.cell(row=row, column=column + 5).value = ''
            ws.cell(row=row, column=column + 6).value = r.revenue_amount or ''
            ws.cell(row=row, column=column + 7).value = r.opex_amount or ''
            ws.cell(row=row, column=column + 8).value = r.capex_amount or ''
            ws.cell(row=row, column=column + 9).value = r.invoice_amount or ''
            ws.cell(row=row, column=column + 10).value = r.task_id.task_no or ''

            row += 1
            sr += 1

        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir,'tmp.xlsx')
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
            invoice_summary_id=self.id,
            res_id=self.id,
            res_model='budget.invoice.summary',
            type='binary',
            datas=data,
        )
        ir_attach.create(values)

        # Clear
        shutil.rmtree(temp_dir)
        self.state = 'generated'

        # Set related invoices state to "summary generated"
        for invoice in self.invoice_ids:
            invoice.state = 'summary printed'

    @api.one
    def set2sent_to_finance(self):
        for invoice in self.invoice_ids:
            invoice.state = 'sent to finance'
        self.state = 'sent to finance'

    @api.one
    def set2closed(self):
        for invoice in self.invoice_ids:
            invoice.state = 'closed'
        self.state = 'closed'

    @api.one
    def set2canceled(self):
        for invoice in self.invoice_ids:
            invoice.state = 'verified'
        self.state = 'canceled'
