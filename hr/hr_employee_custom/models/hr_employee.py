# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class HrEmployeePrivate(models.Model):

    _inherit ='hr.employee'
    name_eng = fields.Char(string='Name English')
    religion_id = fields.Many2one('hr.religion', string='Religion')


class HrReligion(models.Model):
    _name = 'hr.religion'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)






