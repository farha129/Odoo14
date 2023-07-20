# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    ceo_id = fields.Many2one('hr.employee', string='CEO',
                             help="CEO used to print on cash or bank payment of es_report_payment module.")
    accountant_id = fields.Many2one('hr.employee', string='Accountant',
                                    help="Accountant used to print on cash or bank payment of es_report_payment module.")
