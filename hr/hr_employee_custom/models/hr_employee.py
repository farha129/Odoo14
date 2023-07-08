# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta



class HrEmployeePrivate(models.Model):

    _inherit ='hr.employee'
    name_eng = fields.Char(string='Name English')
    number = fields.Char(string='number')
    religion_id = fields.Many2one('hr.religion', string='Religion')
    tech_type = fields.Selection(related='category_ids.tech_type')



    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].get('hr.employee.seq') or ' '
        res = super(HrEmployeePrivate, self).create(vals)
        return res


class HrEmployeeCategory(models.Model):
    _inherit = 'hr.employee.category'
    tech_type = fields.Selection([('tech_cut','Cut Technician'),('tech_gathering','Gathering Technician'),('tech_glass','Glass Technician'),('tech_install','Install Technician')],string= 'Type Technician')


class HrReligion(models.Model):
    _name = 'hr.religion'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)






