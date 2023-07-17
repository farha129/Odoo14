# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError


from dateutil.relativedelta import relativedelta

#This Class For Request purchase From sale Before RFQ Because deffirent Vender

class RequestPurchase(models.Model):
    _name = 'request.purchase'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(strig= 'Name', default='New')
    date_order = fields.Date(string = 'Request Date')
    customer_id = fields.Many2one('res.partner', string='Customer',readonly = True)
    sale_id = fields.Many2one('sale.order','sale order' ,readonly = True)
    currency_id = fields.Many2one('res.currency',string= 'Currency')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)
    line_ids = fields.One2many('request.purchase.line','request_id',string='Line')
    po_count = fields.Integer(compute='_get_po', string='Request Purchase')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_purchase', 'Purchase Order'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    # def action_draft(self):
    #     for rec in self:
    #         rec.state = 'draft'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_in_purchase(self):
        for rec in self:
            rec.state = 'in_purchase'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'



    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('request.purchase') or '/'
            res = super(RequestPurchase, self_comp).create(vals)

            return res

    def _get_po(self):
        for orders in self:
            request_ids = self.env['purchase.order'].search([('sale_id', '=', self.sale_id.id)])
            self.po_count = len(request_ids)


    def action_open_purchase_order(self):
        tree_id = self.env.ref("purchase.purchase_order_kpis_tree").id
        form_id = self.env.ref("purchase.purchase_order_form").id
        return {
            "name": _("Requests for Quotation"),
            "view_mode": "tree,form",
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            "res_model": "purchase.order",
            "domain": [('sale_id', '=', self.sale_id.id)],
            "type": "ir.actions.act_window",
            "target": "current",
        }



class RequestPurchaseLine(models.Model):
    _name = 'request.purchase.line'

    name = fields.Text(string='Description', required=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    state_line = fields.Selection([('no','No Order'),('in_order','In Order'),('qty_no_match','Qty No Match'),('done','Done')],default = 'no',compute = '_get_state_line',string = 'State',readonly = False)
    request_id = fields.Many2one('request.purchase',string = 'Request Purchase')

    def _get_state_line(self):
        for rec in self :
            rec.state_line = 'no'

            po_obj = self.env['purchase.order'].search([('sale_id','=',rec.request_id.sale_id.id)])
            for line in po_obj.order_line :


                if line.product_id.id == rec.product_id.id and line.product_qty == rec.product_qty and line.order_id.state == 'purchase':
                    rec.state_line = 'done'

                if line.product_id.id == rec.product_id.id and line.product_qty == rec.product_qty and line.order_id.state == 'draft':
                    rec.state_line = 'in_order'


                if line.product_id.id == rec.product_id.id and line.product_qty != rec.product_qty:
                    rec.state_line = 'qty_no_match'










