# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import  arabic_reshaper

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
    day_number_work = fields.Integer(string='nu')
    day_number_cut = fields.Float(compute='_get_number_day_work', string='The days of Cut')
    day_number_install = fields.Float(compute='_get_number_day_work', string='The days Of Install')
    day_number_gathering = fields.Float(compute='_get_number_day_work', string='The days Of Gathering')
    day_number_glass = fields.Float(compute='_get_number_day_work', string='The days Of Glass')


    def _get_number_day_work(self):
       config_obj = self.env['config.worker.task'].search([])
       for config in config_obj:
           if config.name == 'cut':
               self.day_number_cut = self.product_qty /config.workers_in_day
           if config.name == 'gathering':
               self.day_number_gathering = self.product_qty /config.workers_in_day
           if config.name == 'installation':
               self.day_number_install = self.product_qty /config.workers_in_day
           if config.name == 'glass':
               self.day_number_glass = self.product_qty /config.workers_in_day





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
    task_type = fields.Selection([('cut','Cut'),('gathering','Gathering'),('installation','Installation'),('glass','Glass')],string = 'Task Name',required = True)

    name = fields.Char('Task Name',default = get_name)
    user_id = fields.Many2one('res.users', 'Assigned To', default=lambda self: self.env.uid,
                              index=True)

    @api.onchange('task_type')
    def _onchange_task_type(self):
        print('hhhhhhhhhhhhhhhhhhhhhhhh')
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        mrp_brw = self.env['mrp.production'].browse(active_id)
        if self.task_type == 'cut':
            self.name = arabic_reshaper.reshape('قص') + ' ' + mrp_brw.product_id.name
        if self.task_type == 'gathering':
            self.name = arabic_reshaper.reshape('تجميع') + ' ' + mrp_brw.product_id.name
        if self.task_type == 'installation':
            self.name = arabic_reshaper.reshape('تركيب') + ' ' + mrp_brw.product_id.name
        if self.task_type == 'glass':
            self.name = arabic_reshaper.reshape('زجاج') + ' ' + mrp_brw.product_id.name
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
    task_type = fields.Selection([('cut','Cut'),('gathering','Gathering'),('installation','Installation'),('glass','Glass')],string = 'Task Name')






