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
    sale_id = fields.Many2one('sale.order','sale order', required=True)
    date_delay = fields.Date(string='Date Delay')
    customer_id = fields.Many2one(related='sale_id.partner_id')
    reason = fields.Text(string = 'Reason', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('reject', 'Reject'),

    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)


    def action_confirmed(self):
        for rec in self:
            name = rec.sale_id.name
            date_now =  fields.Datetime.now()
            print('naaaaaaaaaaaaame',date_now)

            obj_mrp = self.env['mrp.production'].search([('origin','=', name)])
            for obj in obj_mrp:
                # if date_now > obj.date_planned_start :
                #     days_immpelmented_spent = abs((date_now - obj.date_planned_start).days)# number of days finch from implemented period in contract
                # else :
                #     days_immpelmented_spent = 0
                #
                # obj.reminder_period = rec.sale_id.implemented_period  - days_immpelmented_spent

                obj.write({'state':'delay', 'task_timer':False,'end_date':False})
                taks_object = self.env['project.task'].search([('project_id', '=', obj.project_id.id)])
                if taks_object:
                    for task in taks_object:
                        task.unlink()

            rec.state = 'confirmed'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'


   
    # def create(self, vals):
    #     # Ensures default picking type and currency are taken from the right company.
    #     if vals.get('name', 'New') == 'New':
    #         vals['name'] = self.env['ir.sequence'].next_by_code('request.delay')
    #         res = super(RequestDelay, self).create(vals)
    #
    #         return res
    #


    


