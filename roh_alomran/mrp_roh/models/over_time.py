# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError


from dateutil.relativedelta import relativedelta

#This Class For Request purchase From sale Before RFQ Because deffirent Vender

class OvertimeMrp(models.Model):
    _name = 'overtime.mrp'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(strig= 'Name', default='New')
    deadline_cut = fields.Date(string = 'Deadline Cut')
    deadline_gathering = fields.Date(string = 'Deadline Gathering')
    deadline_glass = fields.Date(string = 'Deadline Glass')
    deadline_install = fields.Date(string = 'Deadline Install')
    number_hours_cut = fields.Integer(string='Number Hours Cut')
    number_hours_gathering = fields.Integer(string='Number Hours Gathering')
    number_hours_glass = fields.Integer(string='Number Hours Glass')
    number_hours_install= fields.Integer(string='Number Hours Install')
    customer_id = fields.Many2one('res.partner', string='Customer',readonly = True)
    sale_id = fields.Many2one('sale.order','sale order' ,readonly = True)
    currency_id = fields.Many2one('res.currency',string= 'Currency')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)
    line_ids = fields.One2many('overtime.line','overtime_id',string='Line')
    note = fields.Text(string = 'Description')




    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    # def action_draft(self):
    #     for rec in self:
    #         rec.state = 'draft'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_confirmed(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'



    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('overtime.mrp') or '/'
            res = super(OvertimeMrp, self_comp).create(vals)

            return res

    
    # def action_open_purchase_order(self):
    #     tree_id = self.env.ref("purchase.purchase_order_kpis_tree").id
    #     form_id = self.env.ref("purchase.purchase_order_form").id
    #     return {
    #         "name": _("Requests for Quotation"),
    #         "view_mode": "tree,form",
    #         'views': [(tree_id, 'tree'), (form_id, 'form')],
    #         "res_model": "purchase.order",
    #         "domain": [('sale_id', '=', self.sale_id.id)],
    #         "type": "ir.actions.act_window",
    #         "target": "current",
    #     }



class OvertimeLine(models.Model):
    _name = 'overtime.line'

    name = fields.Text(string='Description', required=False)
    worker_name = fields.Many2one('hr.employee', string='Worker')
    salary_hour = fields.Float(string='Salary Hour',  required=False)
    number_hour = fields.Integer(string ='Number Hours')
    total_salary = fields.Float(string='Salary', compute='_compute_total_salary')
    overtime_id = fields.Many2one('overtime.mrp',string = 'overtime')

    def _compute_total_salary(self):
        for rec in self:
            rec.total_salary = rec.number_hour * rec.salary_hour



   








