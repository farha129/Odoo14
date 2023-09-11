# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductionReportWizard(models.TransientModel):
    _name = "production.report.wizard"
    _description = 'Production Report Wizard'

    date_from = fields.Date('Start Date',required = True)
    date_to = fields.Date('End Date',required = True)
    report_type = fields.Selection([('report_production','Report Production'),('report_production_worker','Worker Production')],string = 'Report Type',required = True,default='report_production')


    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
		'ids': self.ids,
		'model': self._name,
		'form': data,
 
		}
        
        return self.env.ref('sale_roh.report_production_id2').report_action(self, data=datas)
