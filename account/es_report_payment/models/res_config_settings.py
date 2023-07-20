# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ceo_id = fields.Many2one('hr.employee', related='company_id.ceo_id', readonly=False, string="CEO",
                             help="CEO used to print on cash or bank payment of es_report_payment module.")
    accountant_id = fields.Many2one('hr.employee', related='company_id.accountant_id', readonly=False,
                                    string="Accountant",
                                    help="Accountant used to print on cash or bank payment of es_report_payment module.")
