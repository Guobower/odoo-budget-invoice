# -*- coding: utf-8 -*-

from odoo import api, models


class AutoVacuum(models.AbstractModel):
    _inherit = 'ir.autovacuum'

    @api.model
    def power_on(self, *args, **kwargs):
        self.env['budget.invoice.invoice.summary']._delete_attachments()
        return super(AutoVacuum, self).power_on(*args, **kwargs)
