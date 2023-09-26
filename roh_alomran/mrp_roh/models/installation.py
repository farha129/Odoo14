# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError


from dateutil.relativedelta import relativedelta

#This Class For Request purchase From sale Before RFQ Because deffirent Vender

class installMrp(models.Model):
    _name = 'install.mrp'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(strig= 'Name', default='New')
    address = fields.Char(string = 'Address')
    employee_ids = fields.Many2many('hr.employee',string= 'Employees')
    date_order = fields.Date(string = 'Date Order' ,readonly = True)
    deadline_install = fields.Date(string = 'Deadline Install',readonly = True)
    customer_id = fields.Many2one('res.partner', string='Customer',readonly = True)
    period_install= fields.Integer(string='Period Install',readonly = True)
    sale_id = fields.Many2one('sale.order','sale order' ,readonly = True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)
    # material_use_ids = fields.One2many('install.material_use.line','install_id',string='Material Use')
    material_return_ids = fields.One2many('install.material_return.line','install_id',string='Material Return')
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

            if self.material_return_ids:
                self._create_picking_return()


    def action_confirmed(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'



    def _create_picking_return(self):
        stock_picking = (
            self.env["stock.picking"].create(
                {

                    'picking_type_id': self.sale_id.warehouse_id.in_type_id.id,
                    'partner_id': self.customer_id.id,
                    'install_id': self.id,
                    'origin': self.sale_id.name,
                    'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                    'location_id': self.env.ref('stock.stock_location_customers').id,
                }
            )
        )
        for rec in self.material_return_ids:
            stock_move = self.env["stock.move"].create(
                {
                    "name": "Test Move",
                    "product_id": rec.product_id.id,
                    "product_uom_qty": rec.product_uom_qty,
                    "product_uom": rec.product_id.uom_id.id,
                    "picking_id": stock_picking.id,
                    'install_id': rec.install_id.id,
                    "state": "draft",
                    "location_dest_id": self.env.ref('stock.stock_location_stock').id,
                    "location_id": self.env.ref('stock.stock_location_customers').id,
                }
            )

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('install.mrp') or '/'
            res = super(installMrp, self_comp).create(vals)

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



class installMateriaUselLine(models.Model):
    _name = 'install.material_use.line'

    name = fields.Text(string='Description', required=False)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', )
    product_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)
    install_id = fields.Many2one('install.mrp',string = 'install')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        value = []
        self.ensure_one()
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.name = self.product_id.name

class installMateriaReturnlLine(models.Model):
    _name = 'install.material_return.line'

    name = fields.Text(string='Description', required=False)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', )
    product_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)
    install_id = fields.Many2one('install.mrp',string = 'install')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        value = []
        self.ensure_one()
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.name = self.product_id.name




class StockPicking(models.Model):
    _inherit = 'stock.picking'

    install_id = fields.Many2one("install.mrp", string="Install mrp", readonly=True)

class StockMove(models.Model):
    _inherit = 'stock.move'

    install_id = fields.Many2one("install.mrp", string="Install mrp",readonly=True)







