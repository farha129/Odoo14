# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError


class ReportByQuantity(models.AbstractModel):
    _name = 'report.sale_reports.report_by_quantity_temp'
    _description = 'Quantity Report'


    @api.model
    def get_report_values(self, docids, data=None):
       
        st_date = data['form']['date_from']
        end_date = data['form']['date_to']
        partner_id = data['form']['partner_id']
        product_id = data['form']['product_id']
        warehouse_id = data['form']['warehouse_id']
        docs = []
        docses =[]
        total_amount = total_not_pay=0.0
       # sale_obj = self.env['sale.order.line']
     
        if st_date and end_date and partner_id and product_id:
            docs = self.env['sale.order.line'].search([('order_id.confirmation_date','>=', st_date),('order_id.confirmation_date','<=',end_date),  ('order_partner_id.name','in',partner_id),('product_id','=',product_id.id)])
          
        elif st_date and end_date and partner_id and warehouse_id:
            docs = self.env['sale.order.line'].search([('order_id.confirmation_date','>=', st_date),('order_id.confirmation_date','<=',end_date),('order_id.warehouse_id','=',warehouse_id)])
        elif st_date and end_date and partner_id:
            docs = self.env['sale.order.line'].search([('order_id.confirmation_date','>=', st_date),('order_id.confirmation_date','<=',end_date),  ('order_partner_id.name','in',partner_id)])
        elif st_date and end_date and partner_id:
            docs = self.env['sale.order.line'].search([('order_id.confirmation_date','>=', st_date),('order_id.confirmation_date','<=',end_date)])
        
        
        total_amount = sum(line.price_subtotal for line in docs)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'st_date':st_date,
	    'end_date':end_date,
	    'partner_id':partner_id,
	    'total_amount':total_amount,
            
            }


 
