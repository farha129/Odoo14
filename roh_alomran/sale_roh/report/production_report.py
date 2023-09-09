# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
import  arabic_reshaper



class ProductionReport(models.AbstractModel):
    _name = 'report.sale_roh.report_production_temp_ids'
    _description = 'Production Report'


    def _get_report_values(self, docids, data=None):
       
        st_date = data['form']['date_from']
        end_date = data['form']['date_to']
        docss    = []
        name =  arabic_reshaper.reshape('التوريد')
        # docss.append({
        #     'name':name,
        # })
        obj_sale = self.env['sale.order'].search([('date_order','>=', st_date),('date_order','<=',end_date),('state','=','sale')])
        for obj in obj_sale:
            area = sum(rec.product_uom_qty for rec in obj.order_line)
            docss.append({

                'customer': obj.partner_id.name,
                'total_mater': area,
                'date': (obj.date_order).strftime('%Y-%m-%d'),
            })

        obj_sale = self.env['sale.order'].search(
            [('date_order', '>=', st_date), ('date_order', '<=', end_date), ('state', '=', 'sale')])
        for obj in obj_sale:
            area = sum(rec.product_uom_qty for rec in obj.order_line)
            docss.append({

                'customer': obj.partner_id.name,
                'total_mater': area,
                'date': (obj.date_order).strftime('%Y-%m-%d'),
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docss': docss,
            'st_date':st_date,
	        'end_date':end_date,

            }


 
