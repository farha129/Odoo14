# -*- coding: utf-8 -*-
#################################################################################
#

from odoo import api,fields,models,_

class Employee(models.Model):
    _inherit="hr.employee" 
    
    task_ids=fields.One2many('project.task','employee_id' ,string='task') #One2many fields to get multiple taskids
    total_spent_hours=fields.Float(string='total hours',compute='hours_get') #Count total spent hours
    total_planned_hours=fields.Float(string='total planned hours',compute='hours_get') #Count Total planned hours
    late_time = fields.Float(string='late time',compute='hours_get')
    late_count = fields.Integer(string='late count',compute='hours_get')
    on_time_count = fields.Integer(string='On Time',compute='hours_get')
    on_work_count = fields.Integer(string='Not Work',compute='hours_get')
    sum_performance = fields.Integer(string='Performance',compute='compute_performance')
    performance = fields.Char(string='Performance',compute='compute_performance')




    def check_task(self):
        for record in self:
            if record.user_id:

                task_ids=self.env['project.task'].search([('user_id','=',record.user_id.id)])
                if task_ids:
                    record.task_ids=task_ids

    def hours_get(self):
        t_planned=0
        t_spent=0
        on_count=0
        l_time=0
        l_count=0
        no_work = 0
        time =0

        for task in self:
            name=[]
            self.check_task()
            if task.task_ids:

                for record in task.task_ids:
                    t_planned+=record.planned_hours
                    t_spent+=record.effective_hours


                    if record.timesheet_ids and record.date_deadline:
                        if record.planned_hours>=record.effective_hours and record.timesheet_ids[0].date <= record.date_deadline and record.stage_id.name =='Done':
                            print('daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaate time daye',record.timesheet_ids[0].date)
                            print('000000000000000000000000000000000000000',record.date_deadline )
                            print('000000000000000000000000000000000000000time',time )
                            on_count+=1
                        if (record.timesheet_ids[0].date > record.date_deadline and  (record.stage_id.name == 'Done' or record.stage_id.name == 'Done' )) or ( record.timesheet_ids[0].date >= record.date_deadline and (record.stage_id.name != 'Done' or record.stage_id.name != 'Done' )):
                            l_count +=1

                            print('daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaate time daye',
                                  record.timesheet_ids[0].date)
                            print('000000000000000000000000000000000000000', record.date_deadline)
                            print('000000000000000000000000000000000000000time', time)

                        if record.remaining_hours <0:

                            l_time+=abs(record.remaining_hours)
                    else:
                        no_work+=1


        task.total_spent_hours=t_spent
        task.total_planned_hours=t_planned
        task.late_time=l_time
        task.late_count=l_count
        task.on_time_count=on_count
        task.on_work_count=no_work

    def compute_performance(self):
        count_task  = 0
        for rec in self:
            for obj in rec.task_ids:
                if obj:
                    count_task+=1
                    print('8888888888888888888888888888888',count_task)
            if self.on_time_count:
                self.sum_performance = self.on_time_count/count_task * 100

            object_performance = self.env['employee.performance'].search([('max_rang', '>=', self.sum_performance), ('min_rang', '<=', self.sum_performance)])
            print("set nullbbbbbbbbb", object_performance)

            if object_performance:
                for rec in object_performance:
                    self.performance = rec.name






class Task(models.Model):
    _inherit="project.task"
    
    employee_id=fields.Many2one('hr.employee', string='employee')
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True, required=True)


    @api.model
    def get_emp_id(self):
        for record in self:
            if record.user_id:
                employees = self.env['hr.employee'].search([('user_id','=',record.user_id.id)])
                if employees:
                    emp_id = employees[0].id
                    record.employee_id = emp_id

class EmployeePerformance(models.Model):
    _name = "employee.performance"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string = 'Name')
    min_rang = fields.Integer(string='Minimum Percentage')
    max_rang = fields.Integer(string ='Maximum Percentage')
