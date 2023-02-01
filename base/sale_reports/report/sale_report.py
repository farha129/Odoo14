# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError


class ReportByCustomer(models.AbstractModel):
    _name = 'report.sale_reports.report_by_customer_temp'
    _description = 'Customer Report'


    @api.model
    def _get_report_values(self, docids, data=None):
       
        st_date = data['form']['date_from']
        end_date = data['form']['date_to']
        partner_id = data['form']['partner_id']
        state = data['form']['state']

        docs = []
        docses =[]
        total_amount = total_not_pay=0.0
        
        #object_sale = self.env['sale.order.line'].search([('order_id.date_order','>=', st_date),('order_id.date_order','<=',end_date),  ('order_partner_id.name','in',partner_id)])
        
        if st_date and end_date and partner_id and state:
            docs = self.env['sale.order.line'].search([('order_id.date_order','>=', st_date),('order_id.date_order','<=',end_date),  ('order_partner_id.name','in',partner_id),('order_id.state','=',state)])
        
        elif st_date and end_date and partner_id:
            docs = self.env['sale.order.line'].search([('order_id.date_order','>=', st_date),('order_id.date_order','<=',end_date),  ('order_partner_id.name','in',partner_id)])
        elif  st_date and end_date  and state:
            docs = self.env['sale.order.line'].search([('order_id.date_order','>=', st_date),('order_id.date_order','<=',end_date),('order_id.state','=',state)])

        else:
            docs = self.env['sale.order.line'].search([('order_id.date_order','>=', st_date),('order_id.date_order','<=',end_date)])





        print("uuuuuuuuuuuuuuuuuuuuuu",docs)


        total_amount = sum(line.price_subtotal for line in docs)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
           # 'docses':docses,
            'st_date':st_date,
            'end_date':end_date,
            'partner_id':partner_id,
          #  'total_amount': total_amount,
            'total_amount':total_amount,
           # 'total_not_pay':total_not_pay,




            }


 
