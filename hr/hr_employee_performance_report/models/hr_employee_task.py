# -*- coding: utf-8 -*-


from odoo import api,fields,models,_

class HrEmployeeTask(models.Model):
    _name="hr.employee.task"
    _description = 'Employee Task'
   
    employee_id=fields.Many2one('hr.employee', string='Employee name')


   
		    

