# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    contract_text = fields.Text(string="Contract Text")
    percent_period_date = fields.Integer(string='Percent Calculation Mrp date',
                                         help='Scheduled Date in MRP Calculation from This percent and implemented period in SO ')

#
# class ResDiscountSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     percent_period_date = fields.Integer(related='company_id.percent_period_date', readonly =False)
#     # contract_text = fields.Text(string = "Contract Text",related='company_id.contract_text', readonly =False)
#




    
