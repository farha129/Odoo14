# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportCustomerWizard(models.TransientModel):
    _name = "by.custmomer.wizard"
    _description = 'REport'

    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer',)
    state = fields.Selection([
            ('draft','Draft'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ], string='Status')


    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
		'ids': self.ids,
		'model': self._name,
		'form': data,
 
		}
        
        return self.env.ref('sale_reports.report_sale_by_customer_id').report_action(self, data=datas)
