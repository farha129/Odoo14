# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import  arabic_reshaper
import math


import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta


class MrpProduction(models.Model):
    """ MRP  Case """
    _inherit = "mrp.production"

    def task_count(self):
        for rec in self:
            task_obj = self.env['project.task'].search([('project_id', '=', rec.project_id.id)])
            rec.task_number = len(task_obj)


    task_number = fields.Integer(compute='task_count', string='Tasks')
    day_number_work = fields.Integer(string='nu')
    day_number_cut = fields.Float(compute='_get_number_day_work', string='The days of Cut')
    overtime_cut = fields.Integer(compute='_get_number_day_work')
    day_number_install = fields.Float(compute='_get_number_day_work', string='The days Of Install')
    overtime_install = fields.Integer(compute='_get_number_day_work')
    day_number_gathering = fields.Float(compute='_get_number_day_work', string='The days Of Gathering')
    overtime_gath = fields.Integer(compute='_get_number_day_work')
    day_number_glass = fields.Float(compute='_get_number_day_work', string='The days Of Glass')
    overtime_glass = fields.Integer(compute='_get_number_day_work')
    total_day = fields.Float(compute='_get_number_day_work', string='Manufactur Period')
    day_in_factory = fields.Float(compute='_get_number_day_work', string='Period In Factory')
    day_out_factory = fields.Float(compute='_get_number_day_work', string='Period Out Factory')

    def action_get_task(self):
        form_id = self.env.ref("project.view_task_form2").id
        tree_id = self.env.ref("project.view_task_tree2").id
        kanban_id = self.env.ref("project.view_task_kanban").id
        calendar_id = self.env.ref("project.view_task_calendar").id
        pivot_id = self.env.ref("project.view_project_task_pivot").id
        return {
            "name": _("Tasks"),
            "view_mode": "tree,form",
            'views': [(tree_id, 'tree'), (pivot_id, 'pivot'), (kanban_id, 'kanban'), (form_id, 'form'), (calendar_id, 'calendar')],
            "res_model": "project.task",
            "domain": [('project_id', '=', self.project_id.id)],
            "type": "ir.actions.act_window",
            "target": "current",
        }


    #
    # def create_task_mrp(self):
    #     sale_obj = self.env['sale.order'].search([('state','=','sale')])
    #     print('llllllllllllllllllem',sale_obj)
    #     for so in sale_obj:
    #         today_s = fields.Date.today()
    #         today = today_s.strftime('%Y-%m-%d')
    #         days = so.implemented_period * (so.company_id.percent_period_date / 100)
    #         date_mrp = fields.Date.to_string(so.date_order + timedelta(days))
    #         if today == date_mrp :
    #             print('oooooooooooooooooooookkkkkkkkkkkkkkkkkkk sooooooooooooooooooooooooooooo',so.name)
    #             mrp_object = self.env['mrp.production'].search([('origin','=',so.name)])
    #             obj_employees = self.env['hr.employee'].search([])
    #             employees_cut = []
    #             employees_gath = []
    #             employees_glass = []
    #             employees_install = []
    #             day_number_cut = 0
    #             overtime_cut = 0
    #             day_number_install = 0
    #             overtime_install = 0
    #             day_number_gathering = 0
    #             overtime_gath = 0
    #             day_number_glass = 0
    #             overtime_glass = 0
    #             text = ''
    #             qty= ''
    #
    #             for emp in obj_employees:
    #                 if emp.tech_type == 'tech_cut':
    #                     employees_cut.append(emp.id)
    #                 if emp.tech_type == 'tech_gathering':
    #                     employees_gath.append(emp.id)
    #                 if emp.tech_type == 'tech_glass':
    #                     employees_glass.append(emp.id)
    #                 if emp.tech_type == 'tech_install':
    #                     employees_install.append(emp.id)
    #             for p in mrp_object:
    #                 day_number_cut += p.day_number_cut
    #                 day_number_install += p.day_number_install
    #                 day_number_gathering += p.day_number_gathering
    #                 day_number_glass += p.day_number_glass
    #                 overtime_cut += p.overtime_cut
    #                 overtime_install += p.overtime_install
    #                 overtime_gath += p.overtime_gath
    #                 overtime_glass += p.overtime_glass
    #
    #                 qty= str(p.product_qty)
    #                 text += p.product_id.name + arabic_reshaper.reshape(' مساحتها ') + '      ' + qty + '      '+       "\n"
    #
    #             deadline_cut = fields.Date.to_string(p[0].date_planned_start + timedelta(day_number_cut))
    #             deadline_gathering = fields.Date.to_string(datetime.strptime(deadline_cut, "%Y-%m-%d").date() + timedelta(day_number_gathering))
    #             deadline_glass = fields.Date.to_string(datetime.strptime(deadline_gathering, "%Y-%m-%d").date() + timedelta(day_number_glass))
    #             deadline_install = fields.Date.to_string(datetime.strptime(deadline_glass, "%Y-%m-%d").date()+ timedelta(day_number_install))
    #
    #             vals4 = {'name': arabic_reshaper.reshape('تركيب') + ' ' + arabic_reshaper.reshape(
    #                 'للعميل ') + ' ' + so.partner_id.name,
    #                      'project_id': so.project_id.id,
    #                      'employee_ids': employees_install or False,
    #                      'task_type': 'installation' or False,
    #                      'user_id': False,
    #                      'description': text or False,
    #
    #                      'date_deadline': deadline_install or False,
    #                      'partner_id': so.partner_id.id or False,
    #                      'analytic_account_id': so.analytic_account_id.id or False,
    #                      # 'mrp_id': p.id or False
    #                      }
    #             self.env['project.task'].create(vals4)
    #             vals3 = {'name': arabic_reshaper.reshape('زجاج') + ' ' + arabic_reshaper.reshape(
    #                 'للعميل ') + ' ' + so.partner_id.name,
    #                      'project_id': so.project_id.id,
    #                      'employee_ids': employees_glass or False,
    #                      'task_type': 'glass' or False,
    #                      'user_id': False,
    #                      'description': text or False,
    #
    #                      'date_deadline': deadline_glass or False,
    #                      'partner_id': so.partner_id.id or False,
    #                      'analytic_account_id': so.analytic_account_id.id or False,
    #                      # 'mrp_id': p.id or False
    #                      }
    #             self.env['project.task'].create(vals3)
    #             vals2 = {'name': arabic_reshaper.reshape('تجميع') + ' ' + arabic_reshaper.reshape(
    #                 'للعميل ') + ' ' + so.partner_id.name,
    #                      'project_id': so.project_id.id,
    #                      'employee_ids': employees_gath or False,
    #                      'task_type': 'gathering' or False,
    #                      'user_id': False,
    #                      'description': text or False,
    #
    #                      'date_deadline': deadline_gathering or False,
    #                      'partner_id': so.partner_id.id or False,
    #                      'analytic_account_id': so.analytic_account_id.id or False,
    #                      # 'mrp_id': p.id or False
    #                      }
    #             self.env['project.task'].create(vals2)
    #
    #             vals = {'name': arabic_reshaper.reshape('قص') + ' ' + arabic_reshaper.reshape(
    #                 'للعميل ') + ' ' + so.partner_id.name,
    #                     'project_id': so.project_id.id,
    #                     'employee_ids': employees_cut or False,
    #                     'task_type': 'cut' or False,
    #                     'description': text or False,
    #                     'user_id': False,
    #                     'date_deadline': deadline_cut,
    #                     'partner_id': so.partner_id.id or False,
    #                     'analytic_account_id': so.analytic_account_id.id or False,
    #                     # 'mrp_id': p.id or False
    #                     }
    #             self.env['project.task'].create(vals)
    #             overtime = {
    #                     # 'project_id': so.project_id.id,
    #                     'note': text or False,
    #                     'deadline_cut': deadline_cut,
    #                     'deadline_gathering': deadline_gathering,
    #                     'deadline_glass': deadline_glass,
    #                     'deadline_install': deadline_install,
    #                     'number_hours_cut': overtime_cut,
    #                     'number_hours_gathering': overtime_gath,
    #                     'number_hours_glass': overtime_glass,
    #                     'number_hours_install': overtime_install,
    #                     'customer_id': so.partner_id.id or False,
    #                     'sale_id': so.id or False,
    #                     # 'analytic_account_id': so.analytic_account_id.id or False,
    #                     # 'mrp_id': p.id or False
    #                     }
    #             self.env['overtime.mrp'].create(overtime)



    def _get_number_day_work(self):
       # self.ensure_one()
       for rec in self :

           config_obj = self.env['config.worker.task'].search([])
           for config in config_obj:
               if config.name == 'cut':
                   day_number_cut = math.modf(rec.product_qty /config.workers_in_day)[1]
                   overtime_cut =math.modf(rec.product_qty /config.workers_in_day)[0]*10
                   if overtime_cut >= 5 :
                       rec.day_number_cut = day_number_cut + 1
                       rec.overtime_cut = 0
                   if overtime_cut < 5:
                       rec.day_number_cut = day_number_cut
                       rec.overtime_cut = overtime_cut

               if config.name == 'gathering':
                   day_number_gathering = math.modf(rec.product_qty / config.workers_in_day)[1]
                   overtime_gath = math.modf(rec.product_qty / config.workers_in_day)[0] * 10
                   if overtime_gath >= 5:
                       rec.day_number_gathering = day_number_gathering + 1
                       rec.overtime_gath = 0
                   if overtime_gath < 5:
                       rec.day_number_gathering = day_number_gathering
                       rec.overtime_gath = overtime_gath

               if config.name == 'installation':
                   day_number_install = math.modf(rec.product_qty / config.workers_in_day)[1]
                   overtime_install = math.modf(rec.product_qty / config.workers_in_day)[0] * 10
                   if overtime_install >= 5:
                       rec.day_number_install = day_number_install + 1
                       rec.overtime_install = 0
                   if overtime_install < 5:
                       rec.day_number_install = day_number_install
                       rec.overtime_install = overtime_install

               if config.name == 'glass':

                   day_number_glass = math.modf(rec.product_qty / config.workers_in_day)[1]
                   overtime_glass = math.modf(rec.product_qty / config.workers_in_day)[0] * 10
                   if overtime_glass >= 5:
                       rec.day_number_glass = day_number_glass + 1
                       rec.overtime_glass = 0
                   if overtime_glass < 5:
                       rec.day_number_glass = day_number_glass
                       rec.overtime_glass = overtime_glass

           rec.total_day = rec.day_number_cut + rec.day_number_gathering + rec.day_number_install + rec.day_number_glass
           rec.day_in_factory = rec.day_number_cut + rec.day_number_gathering  + rec.day_number_glass
           rec.day_out_factory = rec.day_number_install




class project_Task(models.Model):
    _inherit='project.task'
    
    mrp_id =  fields.Many2one('mrp.production', 'mrp')
    task_type = fields.Selection([('cut','Cut'),('gathering','Gathering'),('installation','Installation'),('glass','Glass')],string = 'Task Name')
    employee_ids = fields.Many2many('hr.employee',string = 'Employees')






