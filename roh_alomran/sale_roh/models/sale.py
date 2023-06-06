# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError


from dateutil.relativedelta import relativedelta

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    customer_id = fields.Many2one('res.partner', string='Customer',readonly = True)
    sale_id = fields.Many2one('sale.order','sale order' ,readonly = True)


class PurchaserderLine(models.Model):
    _inherit = 'purchase.order.line'
    hi_wi = fields.Float(string = 'total_hi_wi',digits = 'total height and width /2')
    is_5_80 = fields.Boolean(string = '5.80' , default = True)

    @api.onchange('is_5_80')
    def onchange_is_5(self):
        for rec in self:
            if rec.is_5_80:
                rec.product_qty = rec.hi_wi / 5.80
            else:
                rec.product_qty = rec.hi_wi / 6




class DimensionSupplement(models.Model):
    _name = "dimension.supplement"
    _description = "Dimension Supplement"

    sale_id = fields.Many2one('sale.order', string = 'Dimension Sector')
    supplement_name = fields.Many2one('product.product', string='Supplement', required=True)
    supplement_height = fields.Float(string='Height', digits='Supplement Height', default=0)
    supplement_width = fields.Float(string='Width', digits='Supplement Width by mater', default=0)
    dimension_one = fields.Float(string='One Dimension', digits='Product Width by mater', default=0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',)
    purchase_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)



class SaleAccessory(models.Model):
    _name = "sale.accessory"
    _description = "Accessory"

    accessory_name = fields.Many2one('product.product', string='Accessory')
    accessory_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',)
    sale_id = fields.Many2one('sale.order', string = 'Accessory')

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    installation = fields.Boolean('Installation requested?')
    sector_order_line = fields.One2many('sector.order.line', 'sale_id',domain= [('is_active','=',True)],string='Sectors Order Lines', copy=True)
    destination = fields.Char(string='Destination', readonly=False)
    is_delivery = fields.Boolean('Delivery request?')
    dimension_supplement_ids = fields.One2many('dimension.supplement','sale_id',compute='_get_supp', string = 'Dimension' , store=False)
    sale_accessory_ids = fields.One2many('sale.accessory','sale_id',string = 'Accessory',  readonly = False )
    number_payment = fields.Selection([('one','One'),('two','Two'),('three','Three'),('more','More')],string='Number Of Payment' )
    destination_payment  =  fields.Text(string = 'Description Payment')
    destination_paint  =  fields.Char(string = 'Description paint')
    destination_glass  =  fields.Char(string = 'Description glass')
    implemented_period = fields.Integer(string = 'implemented period', digits = 'By The Days' )
    count = fields.Integer( string='Count')
    po_count = fields.Integer(compute='_get_po', string='Purchase Orders')
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False, auto_join=True)


    state = fields.Selection(
        selection_add=[('again', 'Try Again'),('compute', 'Computed')])

    # @api.model
    # def create(self, vals):
    #     order = super(SaleOrder,self.with_context(mail_create_nolog=True)).create(vals)
    #     order.sudo().create_order_line()
    #     return order



    def _get_po(self):
        for orders in self:
            purchase_ids = self.env['purchase.order'].search([('partner_ref', '=', self.name)])
        orders.po_count = len(purchase_ids)


    def create_order_line(self):
        for sect_obj in self.sector_order_line:
            sale = self.order_line.create({'product_id': sect_obj.final_product.id,
                           'name': sect_obj.name,
                           'order_id': self.id,
                           'product_uom_qty': sect_obj.product_area,
                                           })
        self.count = 1

    def action_create_purchase_order(self):
        value = []

        self.ensure_one()
        res = self.env['purchase.order'].browse(self._context.get('id', []))
        so = self.env['sale.order'].browse(self._context.get('active_id'))
        pricelist = self.partner_id.property_product_pricelist
        partner_pricelist = self.partner_id.property_product_pricelist
        sale_order_name = so.name
        company_id = self.env.company

        if self.partner_id.property_purchase_currency_id:
            currency_id = self.partner_id.property_purchase_currency_id.id
        else:
            currency_id = self.env.company.currency_id.id

        purchase_order = res.create({
            'partner_id': self.partner_id.id,
            'date_order': str(self.date_order),
            'origin': sale_order_name,
            'partner_ref': self.name,
            'customer_id': self.partner_id.id,
            'sale_id': self.id,
            'currency_id': currency_id
        })
        sale_order = self.env['sale.order'].browse(self._context.get('active_ids', []))
        message = "Purchase Order created " + '<a href="#" data-oe-id=' + str(
            purchase_order.id) + ' data-oe-model="purchase.order">@' + purchase_order.name + '</a>'
        self.message_post(body=message)

        for data in self.sector_order_line:
            sale_order_name = data.sale_id.name
            if not sale_order_name:
                sale_order_name = so.name
            qty_ids = self.env['stock.quant'].search(
                [('product_id', '=', data.product_id.id), ('location_id', '=', self.warehouse_id.lot_stock_id.id)])
            if qty_ids:
                ava_qty = sum(qty_ids.mapped('available_quantity'))
            else :
                ava_qty = 0.0

            if data.product_uom_qty > ava_qty :

                product_quantity = data.product_uom_qty - ava_qty

                purchase_qty_uom = data.product_uom._compute_quantity(product_quantity, data.product_id.uom_po_id)

                # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
                # Note: one partner can have multiple supplier info for the same product
                supplierinfo = data.product_id._select_seller(
                    partner_id=purchase_order.partner_id,
                    quantity=purchase_qty_uom,
                    date=purchase_order.date_order and purchase_order.date_order.date(),
                    # and purchase_order.date_order[:10],
                    uom_id=data.product_id.uom_po_id
                )
                fpos = purchase_order.fiscal_position_id
                taxes = fpos.map_tax(data.product_id.supplier_taxes_id)
                if taxes:
                    taxes = taxes.filtered(lambda t: t.company_id.id == company_id.id)
                if not supplierinfo:
                    po_line_uom = data.product_uom or data.product_id.uom_po_id
                    price_unit = self.env['account.tax']._fix_tax_included_price_company(
                        data.product_id.uom_id._compute_price(data.product_id.standard_price, po_line_uom),
                        data.product_id.supplier_taxes_id,
                        taxes,
                        company_id,
                    )
                    if price_unit and self.sale_id.currency_id and data.sale_id.company_id.currency_id != data.sale_id.currency_id:
                        price_unit = data.sale_id.company_id.currency_id._convert(
                            price_unit,
                            data.sale_id.currency_id,
                            data.sale_id.company_id,
                            data.sale_id or fields.Date.today(),
                        )

                # compute unit price
                if supplierinfo:
                    price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price,
                                                                                                data.product_id.supplier_taxes_id,
                                                                                                taxes, company_id)
                    if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                        price_unit = supplierinfo.currency_id._convert(price_unit, purchase_order.currency_id,
                                                                       purchase_order.company_id, fields.datetime.today())

                if self.partner_id.property_purchase_currency_id:

                    value.append({
                        'product_id': data.product_id.id,
                        'name': data.name,
                        'product_qty': product_quantity,
                        'order_id': purchase_order.id,
                        'product_uom': data.product_uom.id,
                        'taxes_id': data.product_id.supplier_taxes_id.ids,
                        # 'date_planned': data.date_planned,
                    })
                else:
                    value.append({
                        'product_id': data.product_id.id,
                        'name': data.name,
                        'product_qty': product_quantity,
                        'order_id': purchase_order.id,
                        'product_uom': data.product_uom.id,
                        'taxes_id': data.product_id.supplier_taxes_id.ids,
                        # 'date_planned': data.date_planned,
                        'price_unit': price_unit,
                    })
        for data in self.dimension_supplement_ids:
            sale_order_name = data.sale_id.name
            if not sale_order_name:
                sale_order_name = so.name
            qty_ids = self.env['stock.quant'].search(
                [('product_id', '=', data.supplement_name.id), ('location_id', '=', self.warehouse_id.lot_stock_id.id)])
            if qty_ids:
                ava_qty = sum(qty_ids.mapped('available_quantity'))
            else :
                ava_qty = 0.0

            if data.purchase_uom_qty > ava_qty :

                product_quantity = data.purchase_uom_qty - ava_qty

                purchase_qty_uom = data.product_uom._compute_quantity(product_quantity, data.supplement_name.uom_po_id)

                # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
                # Note: one partner can have multiple supplier info for the same product
                supplierinfo = data.supplement_name._select_seller(
                    partner_id=purchase_order.partner_id,
                    quantity=purchase_qty_uom,
                    date=purchase_order.date_order and purchase_order.date_order.date(),
                    # and purchase_order.date_order[:10],
                    uom_id=data.supplement_name.uom_po_id
                )
                fpos = purchase_order.fiscal_position_id
                taxes = fpos.map_tax(data.supplement_name.supplier_taxes_id)
                if taxes:
                    taxes = taxes.filtered(lambda t: t.company_id.id == company_id.id)
                if not supplierinfo:
                    po_line_uom = data.product_uom or data.supplement_name.uom_po_id
                    price_unit = self.env['account.tax']._fix_tax_included_price_company(
                        data.supplement_name.uom_id._compute_price(data.supplement_name.standard_price, po_line_uom),
                        data.supplement_name.supplier_taxes_id,
                        taxes,
                        company_id,
                    )
                    if price_unit and self.sale_id.currency_id and data.sale_id.company_id.currency_id != data.sale_id.currency_id:
                        price_unit = data.sale_id.company_id.currency_id._convert(
                            price_unit,
                            data.sale_id.currency_id,
                            data.sale_id.company_id,
                            data.sale_id or fields.Date.today(),
                        )

                # compute unit price
                if supplierinfo:
                    price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price,
                                                                                                data.supplement_name.supplier_taxes_id,
                                                                                                taxes, company_id)
                    if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                        price_unit = supplierinfo.currency_id._convert(price_unit, purchase_order.currency_id,
                                                                       purchase_order.company_id, fields.datetime.today())

                if self.partner_id.property_purchase_currency_id:

                    value.append({
                        'product_id': data.supplement_name.id,
                        'name': data.supplement_name.name,
                        'product_qty': product_quantity,
                        'order_id': purchase_order.id,
                        'product_uom': data.product_uom.id,
                        'taxes_id': data.supplement_name.supplier_taxes_id.ids,
                        # 'date_planned': data.date_planned,
                    })
                else:
                    value.append({
                        'product_id': data.supplement_name.id,
                        'name': data.supplement_name.name,
                        'product_qty': product_quantity,
                        'order_id': purchase_order.id,
                        'product_uom': data.product_uom.id,
                        'taxes_id': data.supplement_name.supplier_taxes_id.ids,
                        # 'date_planned': data.date_planned,
                        'price_unit': price_unit,
                    })
        for data in self.sale_accessory_ids:
            sale_order_name = data.sale_id.name
            if not sale_order_name:
                sale_order_name = so.name
            qty_ids = self.env['stock.quant'].search(
                [('product_id', '=', data.accessory_name.id), ('location_id', '=', self.warehouse_id.lot_stock_id.id)])
            if qty_ids:
                ava_qty = sum(qty_ids.mapped('available_quantity'))
            else :
                ava_qty = 0.0

            if data.accessory_uom_qty > ava_qty :

                product_quantity = data.accessory_uom_qty - ava_qty

                purchase_qty_uom = data.product_uom._compute_quantity(product_quantity, data.accessory_name.uom_po_id)

                # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
                # Note: one partner can have multiple supplier info for the same product
                supplierinfo = data.accessory_name._select_seller(
                    partner_id=purchase_order.partner_id,
                    quantity=purchase_qty_uom,
                    date=purchase_order.date_order and purchase_order.date_order.date(),
                    # and purchase_order.date_order[:10],
                    uom_id=data.accessory_name.uom_po_id
                )
                fpos = purchase_order.fiscal_position_id
                taxes = fpos.map_tax(data.accessory_name.supplier_taxes_id)
                if taxes:
                    taxes = taxes.filtered(lambda t: t.company_id.id == company_id.id)
                if not supplierinfo:
                    po_line_uom = data.product_uom or data.accessory_name.uom_po_id
                    price_unit = self.env['account.tax']._fix_tax_included_price_company(
                        data.accessory_name.uom_id._compute_price(data.accessory_name.standard_price, po_line_uom),
                        data.accessory_name.supplier_taxes_id,
                        taxes,
                        company_id,
                    )
                    if price_unit and self.sale_id.currency_id and data.sale_id.company_id.currency_id != data.sale_id.currency_id:
                        price_unit = data.sale_id.company_id.currency_id._convert(
                            price_unit,
                            data.sale_id.currency_id,
                            data.sale_id.company_id,
                            data.sale_id or fields.Date.today(),
                        )

                # compute unit price
                if supplierinfo:
                    price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price,
                                                                                                data.accessory_name.supplier_taxes_id,
                                                                                                taxes, company_id)
                    if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                        price_unit = supplierinfo.currency_id._convert(price_unit, purchase_order.currency_id,
                                                                       purchase_order.company_id, fields.datetime.today())

                if self.partner_id.property_purchase_currency_id:

                    value.append({
                        'product_id': data.accessory_name.id,
                        'name': data.accessory_name.name,
                        'product_qty': product_quantity,
                        'order_id': purchase_order.id,
                        'product_uom': data.product_uom.id,
                        'taxes_id': data.accessory_name.supplier_taxes_id.ids,
                        # 'date_planned': data.date_planned,
                    })
                else:
                    value.append({
                        'product_id': data.accessory_name.id,
                        'name': data.accessory_name.name,
                        'product_qty': product_quantity,
                        'order_id': purchase_order.id,
                        'product_uom': data.product_uom.id,
                        'taxes_id': data.accessory_name.supplier_taxes_id.ids,
                        # 'date_planned': data.date_planned,
                        'price_unit': price_unit,
                    })


        self.env['purchase.order.line'].create(value)

        return purchase_order

    def action_open_purchase_order(self):
        tree_id = self.env.ref("purchase.purchase_order_kpis_tree").id
        form_id = self.env.ref("purchase.purchase_order_form").id
        return {
            "name": _("Requests for Quotation"),
            "view_mode": "tree,form",
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            "res_model": "purchase.order",
            "domain": [('partner_ref', '=', self.name)],
            "type": "ir.actions.act_window",
            "target": "current",
        }

    # @api.constrains('order_line')
    # def _order_line_null(self):
    #     if not self.order_line :
    #         raise ValidationError(_('Please Add products or Line' ))

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.action_create_purchase_order()

        return res


    # @api.onchange('sector_order_line')
    # def _onchange_get_acc(self):
    #     value = []
    #     for rec in self.sector_order_line:
    #
    #         if not rec:
    #             continue
    #         else:
    #             acc_obj = self.env['product.accessory'].search([('product_acc_id.name', '=', rec.product_id.name)])
    #
    #             if acc_obj:
    #                 for obj in acc_obj:
    #                     value.append({'accessory_name': obj.accessory_name.id,
    #                                                     'accessory_uom_qty': obj.accessory_uom_qty,
    #                                                     'sale_id': self.id,
    #                                                     'product_uom': obj.accessory_name.uom_id.id,
    #                                                        })
    #
    #
    #                     self.sale_accessory_ids.create(value)
    #



    # def _get_acc(self):
    #     acc_ids = []
    #     for rec in self.order_line:
    #         rec._onchange_discount()
    #         discount = rec.discount
    #         acc_obj = self.env['product.accessory'].search([('product_acc_id.name', '=', rec.product_id.name)])
    #         print('pppppppppppppppppppppppppppppppppacc_obj', acc_obj)
    #
    #         for obj in acc_obj:
    #             price_unit = rec._get_display_price(obj.accessory_name)
    #
    #             print('ppppppppppppppppppppppppppppppppp',obj)
    #             acc_ids = self.env['sale.order.option'].create({'product_id': obj.accessory_name.id,
    #                                             'quantity': obj.accessory_uom_qty,
    #                                             'name': obj.accessory_name.name,
    #                                             'discount': discount,
    #                                             'price_unit': price_unit,
    #                                             'is_present': True,
    #                                             'uom_id': obj.accessory_name.uom_id.id,
    #                                             'order_id': self.id,
    #
    #                                                 })
    #         self.write({'sale_order_option_ids':[(4,acc_ids.id)]})

    def _get_supp(self):

        for rec in self.sector_order_line:
            if not rec:
                continue
            else:
                heel = 0.0
                side = 0.0
                area = 0.0
                val = []
                val_with = []

                width2 = 0.0

                if rec.product_id.is_sector:

                        for sect in rec.product_id.supplement_sector_ids:

                            height = [{'name': res.name} for res in rec.product_heights]
                            width = [{'name': res.name} for res in rec.product_widths]
                            if height and width and range(len(height)) == range(len(width)):
                                qyt = 0.0
                                sum = 0.0
                                for i in range(len(height)):
                                    product_hight = (height[i]['name']  * 100) + 30
                                    product_width = (width[i]['name'] * 100) + 30
                                    if sect.type == 'side':
                                       sum +=((product_hight + sect.height) * sect.nmuber)
                                       side = product_hight + sect.height
                                       val.append(side)
                                    qyt = sum /5.80

                                    if sect.type == 'heel':
                                        sum +=( (product_width + sect.width) / sect.division_number) * sect.nmuber
                                        heel = ((product_width + sect.width) / sect.division_number)
                                        val_with.append(heel)
                                    qyt = sum / 5.80


                                    if sect.type == 'glass':
                                        for i in range(len(height)):
                                            side = val[i]
                                            hight2 = sect.side + side
                                            heel = val_with[i]
                                            width2 = sect.heel + heel
                                            area = hight2 *width2
                                            sum += area
                                        qyt = sum / 7.44
                                        break

                                    if sect.type == 'wire':
                                        print(val)
                                        for i in range(len(height)):
                                            side = val[i]
                                            hight2 = (sect.side + side) * sect.nmuber
                                            heel = val_with[i]
                                            width2 =( sect.heel + heel) * sect.nmuber
                                            total = hight2 + width2
                                            sum += total
                                        qyt = sum / 5.80

                                sup_ids= self.env['dimension.supplement'].create({'supplement_name': sect.supplement_name.id,
                                                             'purchase_uom_qty': qyt/100,
                                                             'product_uom': sect.supplement_name.uom_id.id,
                                                             'sale_id': self.id, })
                                if sup_ids:
                                    self.write({'dimension_supplement_ids': [(4, sup_ids.id)]})





        # rec.order_id.state = 'compute'


    # def compute_dimension_id(self):
    #
    #     # for rec in self:
    #         for rec in self.order_line:
    #             height2 = 0.0
    #             width2 = 0.0
    #             product_hight = 0.0
    #             product_width = 0.0
    #             height = [{'name': res.name} for res in rec.product_heights]
    #             width = [{'name': res.name} for res in rec.product_widths]
    #             if height and width and range(len(height)) == range(len(width)):
    #
    #                 for i in range(len(height)):
    #
    #                     if rec.product_id.is_sector:
    #                         for sect in rec.product_id.supplement_sector_ids:
    #                             dimension_one = 0.0
    #
    #                             product_hight = height[i]['name']  * 1000
    #                             product_width = width[i]['name'] * 1000
    #                             if sect.dimensions_number == 'one':
    #                                 if sect.measured_from == 'height':
    #                                     dimension_one = (product_hight + sect.height) * 2
    #                                     print('ggggggggggggggggggggggggggggggggggggggg',product_hight )
    #                                     print('ggggggggggggggggggggggggggggggggggggggg',sect.height )
    #                                     print('ggggggggggggggggggggggggggggggggggggggg',dimension_one)
    #                                     if sect.is_side == True:
    #                                         side = dimension_one
    #                                 if sect.measured_from == 'width':
    #                                     dimension_one = (product_width + sect.width) / sect.division_number
    #                                     if sect.is_heel == True:
    #                                         heel = dimension_one
    #
    #                                 if sect.measured_from == 'h_w':
    #                                     dimension_one =( (product_width + sect.width) + (product_hight + sect.height)) / sect.division_number
    #                             if  sect.dimensions_number == 'two':
    #                                 if sect.measured_from == 'h_w':
    #                                     height2 = (product_hight + sect.height)/ sect.division_number
    #                                     width2 = (product_width + sect.width)/ sect.division_number
    #                             if  sect.dimensions_number == 'two':
    #                                 if sect.measured_from == 'side_heel':
    #                                     height2 =  sect.side + side
    #                                     width2 =  sect.heel + heel
    #
    #                             self.dimension_supplement_ids.create({'supplement_name': sect.supplement_name.id,
    #                                                                  'supplement_height': height2,
    #                                                                  'supplement_width': width2,
    #                                                                  'dimension_one': dimension_one,
    #                                                              'sale_id': self.id, })
    #         rec.state = 'compute'
    #

    def action_try_agains(self):
        for rec in self:
            rec.state = 'again'


    def auto_send_message(self):
        """ Create mail specific for recipient containing notably its access token """
        sale_obj = self.env['sale.order'].search([])

        for rec in sale_obj:

            today_s = fields.Date.today()
            date_try_s  = rec.date_order
            today = today_s.strftime('%Y-%m-%d')
            date_try = (date_try_s + relativedelta(days=3)).strftime('%Y-%m-%d')

            if today == date_try and rec.state != 'sale':
                base_url = rec.env['ir.config_parameter'].sudo().get_param('web.base.url')
                mass = rec.env['mail.message'].create({'email_from': rec.env.user.partner_id.email,
                                                 'author_id': rec.env.user.partner_id.id,
                                                 'model': 'mail.channel',
                                                 'subtype_id': rec.env.ref('mail.mt_comment').id,
                                                 'body': 'Dear ALL ' + '<br/>This Quation'+'  '+ rec.name + '   Spent Three days need you action (Try Agin or Cancel) <a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
                                    base_url, 'sale.order', rec.id),
                                                 'channel_ids': [(4, rec.env.ref(
                                                     'sale_roh.channel_sale_group').id)],
                                                 'res_id': rec.env.ref(
                                                     'sale_roh.channel_sale_group').id,
                                                 })
                admin = rec.env['res.users'].search([('id', '=', 2)])
                partner_id_boolean = self.env.user.has_group('sale.group_sale_salesman')
                if partner_id_boolean:
                    group_id = rec.env.ref('sale.group_sale_salesman').users
                    partners_ids = group_id.mapped('partner_id').ids
                    for partenr in partners_ids:
                        partner_obj = rec.env['res.partner'].search([('id','=',partenr)])
                        if partner_obj.email:
                            massage_ids = rec.env['mail.mail'].create({
                                'subject': 'This record need you action (%s)' % (
                                        str('sale.order') + ': ' + str(rec.name)),
                                'body_html': 'Dear  All'   + '<br/>This Sale Quation'+'  '+ rec.name + '   Spent Three days need you action(Try Agin or Cancel) <a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
                                    base_url, 'sale.order', rec.id),
                                'email_from': admin.partner_id.email,
                                'email_to': partner_obj.email,
                                'auto_delete': True,
                                'state': 'outgoing',
                                'mail_message_id': mass.id,
                                'body': 'Dear ALL ' + '<br/>This Quation'+'  '+ rec.name + '   Spent Three days need you action (Try Agin or Cancel)  <a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
                                    base_url, 'sale.order', rec.id),
                            })
                            massage_ids.send()

            if today > date_try and rec.state in ('draft', 'again'):

                base_url = rec.env['ir.config_parameter'].sudo().get_param('web.base.url')
                mass = rec.env['mail.message'].create({'email_from': rec.env.user.partner_id.email,
                                                 'author_id': rec.env.user.partner_id.id,
                                                 'model': 'mail.channel',
                                                 'subtype_id': rec.env.ref('mail.mt_comment').id,
                                                 'body':  'Dear ALL ' +  '<br/>This Sale Quation'+'  '+ rec.name + '  Spent More Than Three days need you action(Confirm or Cancel) <a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
                                    base_url, 'sale.order', rec.id),
                                                 'channel_ids': [(4, rec.env.ref(
                                                     'sale_roh.channel_sale_group').id)],
                                                 'res_id': rec.env.ref(
                                                     'sale_roh.channel_sale_group').id,
                                                 })
                admin = rec.env['res.users'].search([('id', '=', 2)])
                partner_id_boolean = rec.env.user.has_group('sale.group_sale_salesman')
                if partner_id_boolean:
                    group_id = rec.env.ref('sale.group_sale_salesman').users
                    partners_ids = group_id.mapped('partner_id').ids
                    for partenr in partners_ids:
                        partner_obj = rec.env['res.partner'].search([('id','=',partenr)])
                        if partner_obj.email:
                            massage_ids = rec.env['mail.mail'].create({
                                'subject': 'This record need you action (%s)' % (
                                        str('sale.order') + ': ' + str(rec.name)),
                                'body_html': 'Dear  All' + '<br/>This Sale Quation'+'  '+ rec.name + '   Spent More Than Three days need you action(Confirm or Cancel)<a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
                                    base_url, 'sale.order', rec.id) ,
                                'email_from': admin.partner_id.email,
                                'email_to': partner_obj.email,
                                'auto_delete': True,
                                'state': 'outgoing',
                                'mail_message_id': mass.id,
                                'body': 'Dear ALL ' +'<br/>This Quation'+'  '+ rec.name + '   Spent More Than Three days need you action (Confirm or Cancel)<a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
                                    base_url, 'sale.order', rec.id),

                            })
                            massage_ids.send()


class DimensionLineHeight(models.Model):
    _name = 'dimension.line.height'
    _description = "Height"

    name = fields.Float(string='Tag Name')


class DimensionLineWidth(models.Model):
    _name = 'dimension.line.width'
    _description = "Width"

    name = fields.Float(string='Tag Name')

# product_uom_qty

class SectorOderLine(models.Model):
    _name = 'sector.order.line'
    _description = "sector order line"
    height = []
    width = []

    name = fields.Char(string = "Description", required=True)

    product_id = fields.Many2one('product.product', string='Sector',domain="[('is_sector', '=', True)]", required=True) # Unrequired company
    final_product = fields.Many2one('product.product', string='Final Product', required=True)

    product_heights = fields.Many2many('dimension.line.height', string='Height(Mt)', required=True)
    product_widths = fields.Many2many('dimension.line.width',string='Width(Mt)', required=True)
    hi_wi = fields.Float(string = 'total_hi_wi',digits = 'total height and width /2')
    is_5_80 = fields.Boolean(string = '5.80' , default = True)
    sale_id = fields.Many2one('sale.order', string = 'Sectors' , ondelete='cascade', index=True, copy=False)
    is_active = fields.Boolean(string = 'Is active', default = True)

    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    product_uom_qty = fields.Float(
        'Purchase Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)

    product_qty_new = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)



    product_area = fields.Float(string='Area(Mt2)', digits='Product Area(Width*Height*Quantity) by mater', default=1 , compute= 'compute_area',store = True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        value=[]
        self.ensure_one()
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.name = self.product_id.name
    #         acc_obj = self.env['product.accessory'].search([('product_acc_id.name', '=', self.product_id.name)])
    #         print("ooooooooooooooooooooooooooooooooooooooooooooooooooooooobbbbbbbbbbbbbbbbb",self.sale_id.partner_id)
    #
    #         if acc_obj:
    #             for obj in acc_obj:
    #                 acc= self.env['sale.accessory'].create({'accessory_name': obj.accessory_name.id,
    #                               'accessory_uom_qty': obj.accessory_uom_qty,
    #                               'sale_id': self.sale_id.id,
    #                               'product_uom': obj.accessory_name.uom_id.id,
    #                               })
    #             print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",acc)
    #             self.sale_id.write({'sale_order_option_ids': [(4, acc.id)]})
    #
    #             print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxhhh",self.sale_id.sale_accessory_ids.sale_id.id)
    #
    #


    @api.depends('product_heights', 'product_widths','product_qty_new')
    def compute_area(self):
        for rec in self:
            total = 0.0
            area = 0.0
            height = [{'name': res.name} for res in  rec.product_heights]
            width = [{'name': res.name} for res in  rec.product_widths]
            if  height and width and  range(len(height)) == range(len(width)) :

                for i in range(len(height)):

                    total +=  ((height[i]['name']+ 0.3)*2 )+ ((width[i]['name']+ 0.3)*2)
                    if height[i]['name'] < 1 :
                        height[i]['name'] = 1
                    if width[i]['name'] < 1 :
                        width[i]['name'] = 1

                    area += height[i]['name']  *  width[i]['name'] * rec.product_qty_new
                rec.product_area = area
                rec.product_uom_qty = total / 5.80
                rec.hi_wi = total

            else:
                print('pllllllllllllllllease')
                rec.product_area = 1
                rec.product_uom_qty = 1

    @api.constrains("product_heights", "product_widths")
    def check_with_and_hight(self):
        for rec in self:
            height = [{'name': res.name} for res in rec.product_heights]
            width = [{'name': res.name} for res in rec.product_widths]
            if not (height and width and range(len(height)) == range(len(width))):
                raise ValidationError(_('Enter Correct Height and Width'))



    @api.onchange('is_5_80')
    def onchange_is_5(self):
        for rec in self:
            if rec.is_5_80:
                rec.product_uom_qty = rec.hi_wi / 5.80
            else:
                rec.product_uom_qty = rec.hi_wi / 6


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    product_number = fields.Float(string='Product Number', default=1)

