# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ConfigWorkerTask(models.Model):
    _name = "config.worker.task"

    name = fields.Selection([('cut','Cut'),('gathering','Gathering'),('installation','Installation'),('glass','Glass')],string = 'Task Name',required = True)
    one_work_in_day = fields.Float(string = 'One Worker in Day',required = True)
    one_work_in_month = fields.Float(string = 'One Worker in Month', readonly=True, compute='_get_mater')
    number_worker = fields.Float(string = 'Number Worker',default = 1.0,compute = 'compute_employee_number')
    workers_in_month = fields.Float(string='Workers In Month' , readonly=True,compute='_get_mater')
    workers_in_day = fields.Float(string='Workers In Day' , readonly=True,compute='_get_mater')

    @api.depends('name')
    def compute_employee_number(self):
        for rec in self:
            if rec.name =='cut':
                obj_employees = self.env['hr.employee'].search([('tech_type','=','tech_cut')])
                rec.number_worker = len(obj_employees)
            if rec.name =='gathering':
                obj_employees = self.env['hr.employee'].search([('tech_type','=','tech_gathering')])
                rec.number_worker = len(obj_employees)
            if rec.name =='glass':
                obj_employees = self.env['hr.employee'].search([('tech_type','=','tech_glass')])
                rec.number_worker = len(obj_employees)
            if rec.name =='installation':
                obj_employees = self.env['hr.employee'].search([('tech_type','=','tech_install')])
                rec.number_worker = len(obj_employees)

    def _get_mater(self):
        number_day_in_month = 27
        for rec in self:
            rec.one_work_in_month = rec.one_work_in_day * number_day_in_month
            rec.workers_in_month = rec.one_work_in_month * rec.number_worker
            rec.workers_in_day = rec.one_work_in_day * rec.number_worker

class ResSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mrp_target_area = fields.Float(related='company_id.mrp_target_area', readonly =False)
    deduction_amount = fields.Float(related='company_id.deduction_amount', readonly =False)



class ResCompany(models.Model):
    _inherit = 'res.company'

    mrp_target_area = fields.Float(string = 'Target Area' , help = 'Target is The number of Area to be manufactured per month ')
    deduction_amount = fields.Float(string = 'Deduction Amount' , help = 'An amount deducted when the request is delayed')

