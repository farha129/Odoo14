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
    tech_type = fields.Selection([('tech_cut','Cut Technician'),('tech_gathering','Gathering Technician'),('tech_glass','Glass Technician'),('tech_install','Install Technician')],string= 'Type Technician')
    employee_partner_id  = fields.Many2one('res.partner',string = 'Partner')



    @api.onchange('category_ids')
    def _onchange_alias_name(self):
        for rec in self:
            for cat in rec.category_ids:
                if cat.tech_type:
                    rec.tech_type = cat.tech_type
                else:
                    rec.tech_type = False



    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].get('hr.employee.seq') or ' '
        res = super(HrEmployeePrivate, self).create(vals)
        if not res.user_id.id:

            partner = res.env['res.partner'].create({'name':res.name,
                                                      'email': res.work_email,
                                                      'mobile': res.mobile_phone, })
            res.employee_partner_id = partner.id
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






