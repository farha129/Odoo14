# -*- coding: utf-8 -*-
from odoo import models, fields

class PaymentWizard(models.TransientModel):
    _name = 'payslip_report.wizard'

    date_from = fields.Date(string='From',default=fields.date.today())
    date_to = fields.Date(string='To',default=fields.date.today())
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    def print_payslips(self):
        """Redirects to the report with the values obtained from the wizard
        'data['form']': name of project and the date duration"""
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return self.env.ref('hr_attendance_sheet.action_report_print_payslips').report_action(self, data=data)
