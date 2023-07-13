# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ConfigWorkerTask(models.Model):
    _name = "config.worker.task"

    name = fields.Selection([('cut','Cut'),('gathering','Gathering'),('installation','Installation'),('glass','Glass')],string = 'Task Name',required = True)
    one_work_in_day = fields.Float(string = 'One Worker in Day',required = True)
    one_work_in_month = fields.Float(string = 'One Worker in Month', readonly=True, compute='_get_mater')
    number_worker = fields.Float(string = 'Number Worker',default = 1.0)
    workers_in_month = fields.Float(string='Workers In Month' , readonly=True,compute='_get_mater')
    workers_in_day = fields.Float(string='Workers In Day' , readonly=True,compute='_get_mater')

    def _get_mater(self):
        number_day_in_month = 27
        for rec in self:
            rec.one_work_in_month = rec.one_work_in_day * number_day_in_month
            rec.workers_in_month = rec.one_work_in_month * rec.number_worker
            rec.workers_in_day = rec.one_work_in_day * rec.number_worker

class ResDiscountSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    percent_period_date = fields.Integer(related='company_id.percent_period_date', readonly =False)
    # mrp_target_area = fields.Float(related='company_id.mrp_target_area', readonly =False)



class ResCompany(models.Model):
    _inherit = 'res.company'
    percent_period_date = fields.Integer(string = 'Percent Calculation Mrp date',help ='Scheduled Date in MRP Calculation from This percent and implemented period in SO ')
    # mrp_target_area = fields.Float(string = 'Target is The number of Area to be manufactured per month ')

