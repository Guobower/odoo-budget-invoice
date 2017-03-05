# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons.budget_core.models.utilities import choices_tuple

from ..xlsx_creator.creator import Creator

class InvoiceSummary(models.Model):
    _name = 'budget.invoice.invoice.summary'
    _rec_name = 'summary_no'
    _description = 'Invoice Summary'
    _order = 'id desc'
    _inherit = ['mail.thread']

    # CHOICES
    # ----------------------------------------------------------
    STATES = choices_tuple(['draft', 'file generated', 'under certification',
                            'sent to finance', 'closed', 'cancelled'], is_sorted=False)
    SIGNATURES = choices_tuple(['cse.png', 'fan.png', '713h_1.png', '713h_2.png'])
    FORMS = choices_tuple(['form_a0001ver01.xlsx', 'form_b0001ver01.xlsx', 'form_b0001ver02.xlsx'])
    OBJECTIVES = choices_tuple(['invoice certification', 'on hold certification'])

    # BASIC FIELDS
    # ----------------------------------------------------------
    # TODO CONSIDER MAKING SUMMARY NO AS NAME
    summary_no = fields.Char(string='Summary No',
                             default=lambda self: self._get_default_summary_no())
    state = fields.Selection(STATES)
    form = fields.Selection(FORMS)
    signature = fields.Selection(SIGNATURES)

    objective = fields.Selection(OBJECTIVES, default='invoice certification')

    signed_date = fields.Date(string='Signed Date')
    closed_date = fields.Date(string='Closed Date')
    sent_finance_date = fields.Date(string='Sent to Finance Date')
    sequence = fields.Integer(string='Sequence')

    # RELATIONSHIPS
    # ----------------------------------------------------------
    # TODO MUST NOT EDITABLE WHEN ON PROCESS, CHECK RULE ACCESS
    invoice_ids = fields.Many2many('budget.invoice.invoice',
                                   'budget_invoice_summary_invoice',
                                   'summary_id',
                                   'invoice_id')
    section_id = fields.Many2one('res.partner', string='Section',
                                 domain=[('is_budget_section', '=', True)])

    # CONSTRAINTS
    # ----------------------------------------------------------
    _sql_constraints = [
        (
            '_uniq_summary_no',
            'UNIQUE(summary_no)',
            'summary must be unqiue!',
        )
    ]

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

        summaries = self.search(domain)
        if len(summaries) == 0:
            sr = 1
        else:
            sr = summaries[0].summary_no.split('-')[-1]
            sr = int(sr) + 1

        return 'IM-%s%s-%03d' % (month, year, sr)

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update(summary_no=self._get_default_summary_no())
        return super(InvoiceSummary, self).copy(default)

    @api.one
    def form_a0001ver01(self, creator):
        """
        GENERATE FORM ACCORDING TO form_a0001ver01
        """

        wb = creator.get_wb()

        # WORK SHEET MAIN
        # ----------------------------------------------------------
        row = 12
        column = 1
        sr = 1
        signature_coor = "B17"  # B18
        logo_coor = "K1"  # J1
        ws = wb.get_sheet_by_name('main')

        ws.cell("C5").value = self.summary_no
        ws.cell("C6").value = fields.Datetime.from_string(self.create_date).strftime('%d-%b-%Y')

        # Create Table
        ws.insert_rows(row, len(self.invoice_ids) - 1)

        # No, Reg, Contractor, Invoice No, Contract, Revenue, OpEx, CapEx, Total Amt, Budget/Yr.
        # 1 , 2  , 3,        , 4         , 5  6    , 7      , 8   , 9    , 10       , 11
        for r in self.invoice_ids.sorted(key=lambda self: self.sequence):
            ws.cell(row=row, column=column).value = sr
            ws.cell(row=row, column=column + 1).value = r.region_id.alias.upper() or ''
            ws.cell(row=row, column=column + 2).value = r.contract_id.contractor_id.name or ''
            ws.cell(row=row, column=column + 3).value = r.invoice_no or ''
            ws.cell(row=row, column=column + 4).value = r.contract_id.no or ''
            ws.cell(row=row, column=column + 5).value = r.revenue_amount or ''
            ws.cell(row=row, column=column + 6).value = r.opex_amount or ''
            ws.cell(row=row, column=column + 7).value = r.capex_amount or ''
            ws.cell(row=row, column=column + 8).value = r.certified_invoice_amount or ''
            #ws.cell(row=row, column=column + 9).value = r.cear_allocation_ids.cear_id.im_utilized_amount
            ws.cell(row=row, column=column + 10).value = ', '.join(r.mapped('cear_allocation_ids.cear_id.no'))
            row += 1
            sr += 1

        # INSERT HEADER LOGO AND SIGNATURE
        ws.add_image(creator.logo, logo_coor)
        ws.add_image(creator.signature, "%s" % signature_coor[0] + str(int(signature_coor[1:]) + sr))


        # SAVE FINAL ATTACHMENT
        creator.save()
        creator.attach(self.env)

    @api.one
    def form_b0001ver01(self, creator):
        """
        GENERATE FORM ACCORDING TO form_a0001ver01
        """

        wb = creator.get_wb()

        # WORK SHEET MAIN
        # ----------------------------------------------------------
        row = 18
        column = 2
        sr = 1
        signature_coor = "B28"  # B18
        logo_coor = "L1"
        ws = wb.get_sheet_by_name('main')

        approval_refs = set([i if i else '' for i in self.mapped('invoice_ids.approval_ref')])
        contractor_names = set([i if i else '' for i in self.mapped('invoice_ids.contractor_id.name')])
        contract_nos = set([i if i else '' for i in self.mapped('invoice_ids.contract_id.no')])
        section_aliases = set([i if i else '' for i in self.mapped('invoice_ids.section_id.alias')])
        ws.cell("B11").value = self.summary_no
        ws.cell("B15").value = fields.Datetime.from_string(self.create_date).strftime('%d-%b-%Y')
        ws.cell("E15").value = ', '.join(approval_refs)
        ws.cell("I11").value = ', '.join(contractor_names)
        ws.cell("I15").value = ', '.join(contract_nos)
        ws.cell("L15").value = ', '.join(section_aliases)

        # Create Table
        ws.insert_rows(row, len(self.invoice_ids) - 1)

        # No, Reg, Contractor, Invoice No, Contract, Revenue, OpEx, CapEx, Total Amt, Budget/Yr.
        # 1 , 2  , 3,        , 4         , 5  6    , 7      , 8   , 9    , 10       , 11
        for r in self.invoice_ids.sorted(key=lambda self: self.sequence):
            ws.cell(row=row, column=column).value = sr
            ws.cell(row=row, column=column + 1).value = fields.Datetime.from_string(r.invoice_date).strftime('%d-%b-%Y') or ''
            ws.cell(row=row, column=column + 2).value = r.invoice_no or ''
            ws.cell(row=row, column=column + 3).value = r.description or ''
            ws.cell(row=row, column=column + 4).value = r.revenue_amount or 0
            ws.cell(row=row, column=column + 5).value = r.opex_amount or 0
            ws.cell(row=row, column=column + 6).value = r.capex_amount or 0
            ws.cell(row=row, column=column + 7).value = r.certified_invoice_amount or 0
            ws.cell(row=row, column=column + 8).value = r.po_id.no or ''
            ws.cell(row=row, column=column + 9).value = r.cear_allocation_ids.cear_id.no
            ws.cell(row=row, column=column + 10).value = '{} & {}'.format(r.cost_center_id.cost_center, r.account_code_id.account_code)
            ws.cell(row=row, column=column + 11).value = 71101
            row += 1
            sr += 1

        # INSERT HEADER LOGO AND SIGNATURE
        ws.add_image(creator.logo, logo_coor)
        ws.add_image(creator.signature, "%s" % signature_coor[0] + str(int(signature_coor[1:]) + sr))


        # SAVE FINAL ATTACHMENT
        creator.save()
        creator.attach(self.env)

    @api.one
    def form_b0001ver02(self, creator):
        """
        GENERATE FORM ACCORDING TO form_a0001ver01
        """

        wb = creator.get_wb()

        # WORK SHEET MAIN
        # ----------------------------------------------------------
        row = 18
        column = 2
        sr = 1
        signature_coor = "B28"  # B18
        logo_coor = "M1"
        ws = wb.get_sheet_by_name('main')

        approval_refs = set([i if i else '' for i in self.mapped('invoice_ids.approval_ref')])
        contractor_names = set([i if i else '' for i in self.mapped('invoice_ids.contractor_id.name')])
        contract_nos = set([i if i else '' for i in self.mapped('invoice_ids.contract_id.no')])
        section_aliases = set([i if i else '' for i in self.mapped('invoice_ids.section_id.alias')])
        ws.cell("B11").value = self.summary_no
        ws.cell("B15").value = fields.Datetime.from_string(self.create_date).strftime('%d-%b-%Y')
        ws.cell("E15").value = ', '.join(approval_refs)
        ws.cell("J11").value = ', '.join(contractor_names)
        ws.cell("J15").value = ', '.join(contract_nos)
        ws.cell("M15").value = ', '.join(section_aliases)

        # Create Table
        ws.insert_rows(row, len(self.invoice_ids) - 1)

        # No, Reg, Contractor, Invoice No, Contract, Revenue, OpEx, CapEx, Total Amt, Budget/Yr.
        # 1 , 2  , 3,        , 4         , 5  6    , 7      , 8   , 9    , 10       , 11
        for r in self.invoice_ids.sorted(key=lambda self: self.sequence):
            ws.cell(row=row, column=column).value = sr
            ws.cell(row=row, column=column + 1).value = fields.Datetime.from_string(r.invoice_date).strftime('%d-%b-%Y') or ''
            ws.cell(row=row, column=column + 2).value = r.invoice_no or ''
            ws.cell(row=row, column=column + 3).value = r.description or ''
            ws.cell(row=row, column=column + 4).value = r.revenue_amount or 0
            ws.cell(row=row, column=column + 5).value = r.opex_amount or 0
            ws.cell(row=row, column=column + 6).value = r.capex_amount or 0
            ws.cell(row=row, column=column + 8).value = r.certified_invoice_amount or 0
            ws.cell(row=row, column=column + 9).value = r.po_id.no or ''
            ws.cell(row=row, column=column + 10).value = r.cear_allocation_ids.cear_id.no or ''
            ws.cell(row=row, column=column + 11).value = '{} {}'.format(r.cost_center_id.cost_center or '', r.account_code_id.account_code or '')
            ws.cell(row=row, column=column + 12).value = 71101
            ws.cell(row=row, column=column + 14).value = r.discount_amount or 0
            ws.cell(row=row, column=column + 15).value = r.discount_percentage or 0

            row += 1
            sr += 1

        # INSERT HEADER LOGO AND SIGNATURE
        ws.add_image(creator.logo, logo_coor)
        ws.add_image(creator.signature, "%s" % signature_coor[0] + str(int(signature_coor[1:]) + sr))


        # SAVE FINAL ATTACHMENT
        creator.save()
        creator.attach(self.env)

    # ONCHANGE
    # ----------------------------------------------------------
    @api.onchange('objective')
    def _check_objective(self):
        if self.objective == 'invoice certification':
            return {
                'domain': {'invoice_ids': [('state', '=', 'verified')]}
            }
        elif self.objective == 'on hold certification':
            return {
                'domain': {'invoice_ids': [('state', '=', 'amount hold')]}
            }

    # BUTTONS/TRANSITIONS
    # ----------------------------------------------------------
    # TODO MUST DO A TRANSITION FOR RETURNING TO DRAFT

    @api.one
    def set2draft(self):
        self.state = 'draft'

    @api.one
    def set2file_generated(self):
        if len(self.invoice_ids) == 0:
            raise ValidationError('Empty Invoice List')

        creator = Creator(summary_no=self.summary_no,
                          summary_res_id=self.id,
                          signature=self.signature,
                          form_filename=self.form)

        # get attribute from form name removing .xlsx
        form = getattr(self, self.form.split('.')[0])
        form(creator)

        # Set related invoices state to "summary generated"
        for invoice in self.invoice_ids:
            invoice.signal_workflow('summary_generate')

        self.state = 'file generated'

    @api.one
    def set2under_certification(self):
        for invoice in self.invoice_ids:
            invoice.signal_workflow('certify')
        self.state = 'under certification'

    @api.one
    def set2sent_to_finance(self):
        if self.signed_date is False:
            raise ValidationError('Signed Date is Required')
        elif self.sent_finance_date is False:
            raise ValidationError('Sent to Finance Date is Required')

        for invoice in self.invoice_ids:
            invoice.sent_finance_date = self.sent_finance_date
            invoice.signed_date = self.signed_date
            invoice.signal_workflow('send_to_finance')
        self.state = 'sent to finance'

    @api.one
    def set2closed(self):
        if self.closed_date is False:
            raise ValidationError('Close Date is Required')
        for invoice in self.invoice_ids:
            invoice.closed_date = self.closed_date
            if invoice.on_hold_amount > 0 and invoice.state != 'amount hold':
                invoice.signal_workflow('amount_hold')
            else:
                invoice.signal_workflow('close')
        self.state = 'closed'

    @api.one
    def set2cancelled(self):
        for invoice in self.invoice_ids:
            invoice.signal_workflow('cancel')
        self.state = 'cancelled'

    # POLYMORPH FUNCTIONS
    @api.one
    def unlink(self):
        self.invoice_ids.delete_workflow()
        self.invoice_ids.create_workflow()
        self.invoice_ids.signal_workflow('verify')
        return super(InvoiceSummary, self).unlink()
