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
        type = data['form']['report_type']
        docss    = []
        docs_cut    = []
        docs_gath    = []
        docs_glass    = []
        docs_install    = []
        docs_employee    = []
        # docss.append({
        #     'name':name,
        # })
        if type == 'report_production':
            obj_sale = self.env['sale.order'].search([('date_order','>=', st_date),('date_order','<=',end_date),('state','=','sale')])
            for obj in obj_sale:
                area = sum(rec.product_uom_qty for rec in obj.order_line)
                docss.append({
                    'customer': obj.partner_id.name,
                    'total_mater': area,
                    'date': (obj.date_order).strftime('%Y-%m-%d'),
                })

            obj_cut = self.env['project.task'].search(
                [('date_stage', '>=', st_date), ('date_stage', '<=', end_date), ('task_type', '=', 'cut')])
            for obj in obj_cut:
                docs_cut.append({
                    'customer': obj.partner_id.name,
                    'total_mater': obj.total_mater,
                    'date':obj.date_stage,
                })

            obj_gath = self.env['project.task'].search(
                [('date_stage', '>=', st_date), ('date_stage', '<=', end_date), ('task_type', '=', 'gathering')])
            for obj in obj_gath:
                docs_gath.append({
                    'customer': obj.partner_id.name,
                    'total_mater': obj.total_mater,
                    'date':obj.date_stage,
                })

            obj_glass = self.env['project.task'].search(
                [('date_stage', '>=', st_date), ('date_stage', '<=', end_date), ('task_type', '=', 'glass')])
            for obj in obj_glass:
                docs_glass.append({
                    'customer': obj.partner_id.name,
                    'total_mater': obj.total_mater,
                    'date':obj.date_stage,
                })

            obj_install = self.env['project.task'].search(
                [('date_stage', '>=', st_date), ('date_stage', '<=', end_date), ('task_type', '=', 'installation')])
            for obj in obj_install:
                docs_install.append({
                    'customer': obj.partner_id.name,
                    'total_mater': obj.total_mater,
                    'date':obj.date_stage,
                })



            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docss': docss,
                'docs_cut': docs_cut,
                'docs_gath': docs_gath,
                'docs_glass': docs_glass,
                'docs_install': docs_install,
                'st_date':st_date,
                'end_date':end_date,

                }


        else:
            obj_employee = self.env['hr.employee'].search([('tech_type', '!=', False)])
            if obj_employee :
                for obj in obj_employee:
                    if obj.tech_type == 'tech_cut':
                        name = arabic_reshaper.reshape('فني قص')
                    if obj.tech_type == 'tech_gathering':
                        name = arabic_reshaper.reshape('فني تجميع')
                    if obj.tech_type == 'tech_glass':
                        name = arabic_reshaper.reshape('فني زجاج')
                    if obj.tech_type == 'tech_install':
                        name = arabic_reshaper.reshape('فني تركيب')

                    sum_maters = 0
                    print('rrrrrrrrrrrrrrrrrrrrrr',obj.name)
                    obj_task = self.env['project.task'].search([('employee_ids','in',obj.id),('date_stage', '>=', st_date), ('date_stage', '<=', end_date)])
                    for task in obj_task:
                        count = 0
                        count = len(task.employee_ids)
                        if task.total_mater != 0 and count !=0:
                            sum_maters += task.total_mater/count

                    docs_employee.append({
                        'employee': obj.name,
                        'tec_type': name,
                        'sum_maters': sum_maters,
                    })

            return{

            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs_employee': docs_employee,
            'st_date': st_date,
            'end_date': end_date,
            'report_type': type,

            }





 
