# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.budget_utilities.models.utilities import choices_tuple
from odoo.tools.safe_eval import safe_eval


class VolumeDiscountRule(models.Model):
    _inherit = 'budget.contractor.discount.rule'

    # CHOICES
    # ----------------------------------------------------------

    # BASIC FIELDS
    # ----------------------------------------------------------
    code = fields.Text()

    # RELATIONSHIPS
    # ----------------------------------------------------------

    # DEFAULTS
    # ----------------------------------------------------------

    # COMPUTE FIELDS
    # ----------------------------------------------------------

    # CONSTRAINS FIELDS
    # ----------------------------------------------------------

    # BUTTON ACTIONS / TRANSITIONS
    # ----------------------------------------------------------
    @api.multi
    def run_rule_code(self, eval_context=None):
        safe_eval(self.code.strip(), eval_context, mode="exec", nocopy=True)
        return eval_context
