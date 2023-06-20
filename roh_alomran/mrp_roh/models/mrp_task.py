# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta


class MrpProduction(models.Model):
    """ MRP  Case """
    _inherit = "mrp.production"

    def task_count(self):
        task_obj = self.env['project.task']
        self.task_number = task_obj.search_count([('mrp_id', 'in', [a.id for a in self])])

    task_number = fields.Integer(compute='task_count', string='Tasks')
    day_number_work = fields.Integer(compute='_get_number_day_work', string='Day Work')

    def _get_number_day_work(self):
        one_day = self.company_id.number_meter / self.company_id.number_day
        print('onnnnnnnnnnnnnnnnnnnnne day',one_day)
        print('onnnnnnnnnnnnnnnnnnnnne number_meter',self.company_id.number_meter )
        print('onnnnnnnnnnnnnnnnnnnnne  self.company_id.number_day', self.company_id.number_day)
        if self.product_qty /one_day == 0:
            self.day_number_work = 1
        else:

           self.day_number_work = self.product_qty /one_day




class mrp_task_wizard(models.TransientModel):
    _name = 'mrp.production.task.wizard'
    _description = "MRP Task Wizard"
    
    
    def get_name(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        mrp_brw = self.env['mrp.production'].browse(active_id)
        name = mrp_brw.product_id.name
        return name
    
    
    project_id = fields.Many2one('project.project','Project')
    dead_line = fields.Date('Deadline')
    name = fields.Char('Task Name',default = get_name)
    user_id = fields.Many2one('res.users', 'Assigned To', default=lambda self: self.env.uid,
                              index=True)
    # user_ids = fields.Many2many('res.users', 'Assignees', default=lambda self: self.env.uid,
    #                             index=True)
    # user_ids = fields.Many2many('res.users', relation='project_task_assignee_rel', column1='task_id', column2='user_id',
    #                             string='Assignees', default=lambda self: self.env.user)


    def create_task(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        mrp_brw = self.env['mrp.production'].browse(active_id)
        # user = []
        # for users in self.user_ids:
        #     user.append(users.id)
        vals = {'name': self.name,
                'project_id':mrp_brw.project_id.id,
                'user_id':self.user_id.id or False,
                'date_deadline':  self.dead_line or False,
                'partner_id': mrp_brw.partner_id.id or False,
                'analytic_account_id': mrp_brw.analytic_account_id.id or False,
                'mrp_id': mrp_brw.id or False
                }
        self.env['project.task'].create(vals)
        
class project_Task(models.Model):
    _inherit='project.task'
    
    mrp_id =  fields.Many2one('mrp.production', 'mrp')





