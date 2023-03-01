# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportpayslipsyWizard(models.TransientModel):
    _name = "by.payslips.wizard"
    _description = 'Report payslips'

    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)

    
    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
		'ids': self.ids,
		'model': self._name,
		'form': data,
		
 
		}
        
        return self.env.ref('report_by_payslips.report_payslips_id').report_action(self, data=datas)
