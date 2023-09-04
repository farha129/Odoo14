# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ScheduleWorkWizard(models.TransientModel):
    _name = "schedule.work.wizard"
    _description = 'Schedule Work Wizard'

    date_from = fields.Datetime('Start Date')
    date_to = fields.Datetime('End Date')


    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
		'ids': self.ids,
		'model': self._name,
		'form': data,
 
		}
        
        return self.env.ref('sale_roh.report_schedule_Work_ids').report_action(self, data=datas)
