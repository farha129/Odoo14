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
    supplement_name = fields.Many2one('product.product', string='Supplement', required=True)
    dimensions_number = fields.Selection([('one', 'One Dimension'), ('two', 'TWO Dimensions')],default='one',
                                         string='Dimensions Number')
    measured_from = fields.Selection(
        [('height', 'Height'), ('width', 'Width'), ('h_w', 'High and Width'),
         ('side_heel', 'Side and Heel')], string='Measured From')
    height = fields.Float(string='Height', digits='Product Height', default=0)
    width = fields.Float(string='Width', digits='Product Width by mater', default=0)
    side = fields.Float(string='Side', digits='Side', default=0)
    heel = fields.Float(string='Heel', digits='Heel', default=0)
    is_side = fields.Boolean(string='Is Side')
    is_heel = fields.Boolean(string='Is Heel')

    division_number = fields.Integer('/', default=1)
    # dimension_one = fields.Float(string='One Dimension', digits='Product Width by mater', default=0)


   

    

   
