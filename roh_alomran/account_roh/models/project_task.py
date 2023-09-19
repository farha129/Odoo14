# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

class ProjectTask(models.Model):
    _inherit = "project.task"
   
    @api.onchange('stage_id')
    def onchange_stage(self):
        res = super(ProjectTask, self).onchange_stage()
        today = fields.Date.today()
        for task in self:
            sale_obj = self.env['sale.order'].search([('project_id','=', task.project_id.id)])
            for sale in sale_obj:
                payment_obj = self.env['account.payment'].search([('sale_id', '=', sale.id)])
                for pay in payment_obj:
                    if task.task_type == pay.install_id.apply_after and task.stage_id.is_closed:
                        pay.update({'date':today})
        return res








    

