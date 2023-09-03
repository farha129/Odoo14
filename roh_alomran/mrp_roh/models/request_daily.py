# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError


from dateutil.relativedelta import relativedelta

#This Class For Request purchase From sale Before RFQ Because deffirent Vender

class RequestDelay(models.Model):
    _name = 'request.delay'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Request Delay"


    name = fields.Char(strig= 'Name', default='New')
    date_order = fields.Datetime(string = 'Date Order',default=fields.Datetime.now)
    customer_id = fields.Many2one('res.partner', string='Customer')
    sale_id = fields.Many2one('sale.order','sale order', required=True)
    reason = fields.Text(string = 'Reason', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('reject', 'Reject'),

    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    # def action_draft(self):
    #     for rec in self:
    #         rec.state = 'draft'

    
    def action_confirmed(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'


   
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('request.delay') or '/'
            res = super(RequestDelay, self_comp).create(vals)

            return res



    


