# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Company(models.Model):

    _inherit = 'res.company'

    number_day = fields.Integer(string= "Number of Day",help="Number days Can Three Worker Worked.")
    number_worker = fields.Integer(string= "Number of Worker" , default = 3)
    number_meter = fields.Integer(string= "Number of Meter",help="Number meter Can Three Worker Worked.")



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    number_day = fields.Integer(related='company_id.number_day', string="Number days", readonly=False,help="Number days Can Three Worker Worked  .")
    number_worker = fields.Integer(related='company_id.number_worker', string="Number of Worker", readonly=True)
    number_meter = fields.Integer(related='company_id.number_meter', string="Number of Meter", readonly=False,help="Number meter Can Three Worker Worked in Number Days.")
