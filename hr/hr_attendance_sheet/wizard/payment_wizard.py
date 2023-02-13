# -*- coding: utf-8 -*-
from odoo import models, fields

class PaymentWizard(models.TransientModel):
    _name = 'payment.wizard'

    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    date = fields.Date(string='Date',default=fields.date.today())
    
    def create_payment(self):
       salary_rule_obj = self.env['hr.salary.rule'].search([],order='sequence desc' , limit=1)
       for i in salary_rule_obj:
           i.account_debit = self.account_debit

    