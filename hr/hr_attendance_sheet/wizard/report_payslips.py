# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReportPayslips(models.AbstractModel):
    _name = 'report.hr_attendance_sheet.report_payslips'

    def get_payslips(self, docs):
        """input : name of project and the starting date and ending date
        output: timesheets by that particular project within that period and the total duration"""

        rec = self.env['hr.payslip'].search([('date_from', '>=', docs.date_from),
                                                ('date_to', '<=', docs.date_to),('state','=','done')])
       
        records = []
        
        for r in rec:
            vals = {'name': r.employee_id.name,
                    'job': r.employee_id.job_id.name,
                    'Refrence': r.number,
                    'Account': r.employee_id.bank_account_id.acc_number,
                    'line_ids': r.line_ids,
                    }
            records.append(vals)

        return [records]


  
    
    @api.model
    def _get_report_values(self, docids, data=None):
        """we are overwriting this function because we need to show values from other models in the report
        we pass the objects in the docargs dictionary"""
        docs = self.env['payslip_report.wizard'].browse(self.env.context.get('active_id'))

        payslips = self.get_payslips(docs)
        period = None
        if docs.date_from and docs.date_to:
            period = "From " + str(docs.date_from) + " To " + str(docs.date_to)
        elif docs.date_from:
            period = "From " + str(docs.date_from)
        elif docs.date_to:
            period = " To " + str(docs.date_to)
    
        return {
            'doc_ids': self.ids,
            'docs': docs,
            'payslips': payslips[0],
            'period': period,
        }
