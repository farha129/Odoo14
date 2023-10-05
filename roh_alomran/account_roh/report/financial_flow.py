# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
import  arabic_reshaper



class FinancialFlow(models.AbstractModel):
    _name = 'report.account_roh.report_financial_flow_temp_id'
    _description = 'Financial Flow Report'


    def _get_report_values(self, docids, data=None):
       
        # st_date = data['form']['date_from']
        # end_date = data['form']['date_to']
        report_type = data['form']['report_type']
        customer_id = data['form']['customer_id']

        docs = []
        if report_type == 'report_finan_follow':
            obj_sale = self.env['sale.order'].search([('state','=','sale')])
            for obj in obj_sale:
                all_payment = self.env['account.payment'].search([('sale_id', '=', obj.id), ('state', '=', 'draft')])
                if all_payment:
                    all_payment_not_payied = sum(rec.amount for rec in all_payment)
                payment = self.env['account.payment'].search([('sale_id','=', obj.id),('state','=','draft')],order='id',limit=1)
                for pay in payment:
                    if pay :
                        if obj.end_date_order == pay.date and pay.install_id.apply_after != 'in_contract':
                            state = arabic_reshaper.reshape('مهمة لم تنتهي')
                        else:
                            state = arabic_reshaper.reshape('يجب تأكيد الدفع')

                        docs.append({
                            'customer': pay.partner_id.name,
                            'date':pay.date,
                            'amount':pay.amount,
                            'description':pay.description,
                            'all_amount':all_payment_not_payied,
                            'state':state,
                            # 'address': address ,
                        })
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': docs,

                'report_type': report_type,
            }

        else:
            payment = self.env['account.payment'].search(
                [('partner_id.id', '=', customer_id[0])],order='id')
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

                'report_type': report_type,
                'customer_id': customer_id[1],

            }




 
