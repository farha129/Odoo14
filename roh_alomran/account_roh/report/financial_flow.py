# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError


class FinancialFlow(models.AbstractModel):
    _name = 'report.account_roh.report_financial_flow_temp_id'
    _description = 'Financial Flow Report'


    def _get_report_values(self, docids, data=None):
       
        st_date = data['form']['date_from']
        end_date = data['form']['date_to']
        report_type = data['form']['report_type']
        customer_id = data['form']['customer_id']

        docs = []
        if report_type == 'report_finan_follow':
            obj_sale = self.env['sale.order'].search([('state','=','sale')])
            for obj in obj_sale:
                payment = self.env['account.payment'].search([('sale_id','=', obj.id),('state','=','draft'),('date','>=', st_date),('date','<=',end_date)],order='id',limit=1)
                for pay in payment:
                    if pay :

                        docs.append({
                            'customer': pay.partner_id.name,
                            'date':pay.date,
                            'amount':pay.amount,
                            'description':pay.description,
                            # 'address': address ,
                        })
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': docs,
                'st_date': st_date,
                'end_date': end_date,
                'report_type': report_type,
            }

        else:
            payment = self.env['account.payment'].search(
                [('partner_id.id', '=', customer_id[0]), ('date', '>=', st_date),
                 ('date', '<=', end_date)],order='id')
            print('kkkkkkkkkkkkkkkkkkkkk',customer_id[0])
            for pay in payment:
                if pay:
                    docs.append({
                        # 'customer': pay.partner_id.name,
                        'date': pay.date,
                        'description': pay.description,
                        'amount': pay.amount,
                        'state': pay.state ,
                    })
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': docs,
                'st_date': st_date,
                'end_date': end_date,
                'report_type': report_type,
                'customer_id': customer_id[1],

            }




 
