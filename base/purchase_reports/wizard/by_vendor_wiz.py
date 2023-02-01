# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportvendorWizard(models.TransientModel):
    _name = "by.vendor.wizard"
    _description = 'Report'

    date_from = fields.Datetime('Start Date', required=True)
    date_to = fields.Datetime('End Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor',)
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')])


    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
		'ids': self.ids,
		'model': self._name,
		'form': data,
 
		}
        
        return self.env.ref('purchase_reports.report_purchase_by_customer_id').report_action(self, data=datas)
