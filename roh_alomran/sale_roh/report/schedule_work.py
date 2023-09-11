# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError


class ScheduleWork(models.AbstractModel):
    _name = 'report.sale_roh.report_schedule_work_temp_id'
    _description = 'Schedule Work Report'


    def _get_report_values(self, docids, data=None):
       
        st_date = data['form']['date_from']
        end_date = data['form']['date_to']
        docs = []
        obj_sale = self.env['sale.order'].search([('date_order','>=', st_date),('date_order','<=',end_date),('state','=','sale')])
        for obj in obj_sale:

            mrp = self.env['mrp.production'].search([('origin','=', obj.name),('state','!=','done')],limit=1)
            if mrp :
                area = sum(rec.product_uom_qty for rec in obj.order_line)
                # docs = obj_sale
                if obj.partner_id.street :
                    address = obj.partner_id.street
                else:
                    address = False
                docs.append({
                    'customer': obj.partner_id.name,
                    'area':round(area),
                    'end_date_order':obj.end_date_order,
                    'address': address ,
                })


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'st_date':st_date,
	        'end_date':end_date,

            }


 
