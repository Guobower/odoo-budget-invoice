# -*- coding: utf-8 -*-
import random, string
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons.budget_utilities.models.utilities import choices_tuple
from ..xlsx_creator.creator import Creator


class InvoiceSummaryTransient(models.TransientModel):
    _name = 'budget.invoice.invoice.summary.transient'
    _description = 'Invoice Summary Transient'
    _inherit = ['budget.invoice.invoice.summary']

    invoice_ids = fields.Many2many('budget.invoice.invoice',
                                   'budget_invoice_summary_invoice_transient',
                                   'summary_id',
                                   'invoice_id')

    @api.multi
    def set2file_generated(self):
        if len(self.invoice_ids) == 0:
            raise ValidationError('Empty Invoice List')

        currency_names = self.mapped("invoice_ids.currency_id.name")
        if len(set(currency_names)) > 1:
            raise ValidationError("Summary can only be generated for invoices with same currency.")

        invoice_id = self.invoice_ids.mapped('id')
        if len(invoice_id) >= 1:
            invoice_id = invoice_id[0]
        elif len(invoice_id) == 0:
            raise ValidationError("Invoice Required")

        creator = Creator(summary_no=self.summary_no,
                          res_id=invoice_id,
                          form_filename=self.form,
                          res_model='budget.invoice.invoice')

        form = getattr(self, self.form.split('.')[0])
        form(creator)

    @api.model
    def _get_default_summary_no(self):
        return 'invoice_certification'

    _sql_constraints = [
        (
            '_uniq_summary_no',
            '(1==1)',
            'removed',
        )
    ]

    # POLYMORPH FUNCTIONS
    # ----------------------------------------------------------
    @api.one
    def unlink(self):
        return super(InvoiceSummaryTransient, self).unlink()
