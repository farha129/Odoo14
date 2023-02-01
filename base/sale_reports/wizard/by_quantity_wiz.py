# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportQuantityWizard(models.TransientModel):
    _name = "by.quantity.wizard"
    _description = 'Report'

    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, domain=[('customer', '=', True)])
    product_id = fields.Many2one('product.product', string='Product')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
		'ids': self.ids,
		'model': self._name,
		'form': data,
 
		}
        
        return self.env.ref('sale_reports.report_sale_by_quantity_id').report_action(self, data=datas)
