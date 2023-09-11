# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

# from . import amount_to_ar

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_supplement = fields.Boolean(string = 'Is supplement')
    is_sector = fields.Boolean(string = 'Is Sector')
    is_accessory = fields.Boolean(string = 'Is Accessory')
    accessory_ids = fields.One2many('product.accessory', 'product_acc_id',string ='Accessorys')
    supplement_sector_ids = fields.One2many('supplement.sector','product_id',string = 'Supplement' )
    supplier_company = fields.Many2one('res.company', string='Supplier Company')
    sector_type = fields.Selection([('drag','Drag'),('drag_roll','Drag Roll'),('fixed','Fixed'),('sketchure','Sketchure'),('upside_down','Upside down'),('hinges','Hinges'),('tipper','Tipper'),('cartel_roll','Cartel Roll')],string ='Sector Type')
#
class ProductProduct(models.Model):
    _inherit = 'product.product'
    is_supplement = fields.Boolean(related='product_tmpl_id.is_supplement',readonly=False)
    is_sector = fields.Boolean(related='product_tmpl_id.is_sector',readonly=False)
    is_accessory = fields.Boolean(related='product_tmpl_id.is_accessory',readonly=False)
    sector_type = fields.Selection(related = 'product_tmpl_id.sector_type',readonly=False)
    

class ProductAccessory(models.Model):
    _name = "product.accessory"
    _description = "Accessory"

    product_acc_id = fields.Many2one('product.template', string='product')
    accessory_name = fields.Many2one('product.product', string='Accessory')
    accessory_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)
    sale_id = fields.Many2one('sale.order', string = 'Accessory')


class SupplementSector(models.Model):
    _name = "supplement.sector"
    _description = "Supplement Sector"

    product_id = fields.Many2one('product.template', string = 'product')
    supplement_name = fields.Many2one('product.product', string='Supplement')
    dimensions_number = fields.Selection([('one', 'One Dimension'), ('two', 'TWO Dimensions')],default='one',
                                         string='Dimensions Number')
    measured_from = fields.Selection(
        [('height', 'Height'), ('width', 'Width'), ('h_w', 'High and Width'),
         ('side_heel', 'Side and Heel')], string='Measured From')
    height = fields.Float(string='Height', digits='Product Height', default=0)
    number_height = fields.Float(string='Height Number', digits='Height Number', default=0)
    number_width = fields.Float(string='Width Number', digits='width Number ', default=0)
    width = fields.Float(string='Width', digits='Product Width by mater', default=0)
    nmuber = fields.Float(string='Number', digits='Number of Supplement', default=1)
    side = fields.Float(string='Side', digits='Side', default=0)
    heel = fields.Float(string='Heel', digits='Heel', default=0)
    is_side = fields.Boolean(string='Is Side')
    is_heel = fields.Boolean(string='Is Heel')
    type = fields.Selection(
        [('side', 'Side'), ('heel', 'Heel'), ('cutter_hor', 'Cutter Hor'),('cutter_var', 'Cutter Var'),('tranzium', 'Tranzium'),('bercluz', 'Bercluz'),('tabsha', 'Tabsha'),('motor', 'Motor'),('shater', 'Shater'),
         ('wire', 'Wire'),('glass', 'Glass'),('silicon', 'Silicon'),('alrubl', 'Alrubl'),('other','other')], string='Type')
    division_number = fields.Integer('/', default=1)
    # dimension_one = fields.Float(string='One Dimension', digits='Product Width by mater', default=0)