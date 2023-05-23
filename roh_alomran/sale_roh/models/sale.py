# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta

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


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     @api.onchange('product_id')
#     def _onchange_product_id_id(self):
#         for line in self:
#             if line.product_id.is_sector:
#                 for sect in line.product_id.supplement_sector_ids:
#                     print('hhhhhhhhhhhhhhhhh',line.order_id.id)
#                     line.order_id.dimension_supplement_ids.create({'supplement_name': sect.supplement_name.id,})
#

class SaleAccessory(models.Model):
    _name = "sale.accessory"
    _description = "Accessory"

    accessory_name = fields.Many2one('product.product', string='Accessory')
    accessory_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)
    sale_id = fields.Many2one('sale.order', string = 'Accessory')




class SaleOrder(models.Model):
    _inherit = 'sale.order'



    installation = fields.Boolean('Installation requested?')
    destination = fields.Char(string='Destination', readonly=False)
    is_delivery = fields.Boolean('Delivery request?')
    dimension_supplement_ids = fields.One2many('dimension.supplement','sale_id',string = 'Dimension' )
    sale_accessory_ids = fields.One2many('sale.accessory','sale_id',string = 'Accessory' )

    state = fields.Selection(
        selection_add=[('again', 'Try Again'),('compute', 'Computed')])

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

    def _get_po(self):
        for orders in self:
            purchase_ids = self.env['purchase.order'].search([('partner_ref', '=', self.name)])
            print('iiiiiiiii8888888888888888888888iiiiii',purchase_ids)

        orders.po_count = len(purchase_ids)

    po_count = fields.Integer(compute='_get_po', string='Purchase Orders')

    def action_create_purchase_order(self):
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
            'currency_id': currency_id,
            'partner_ref': self.name,

        })
        # sale_order = self.env['sale.order'].browse(self._context.get('active_ids', []))
        message = "Purchase Order created " + '<a href="#" data-oe-id=' + str(
            purchase_order.id) + ' data-oe-model="purchase.order">@' + purchase_order.name + '</a>'
        self.message_post(body=message)
        for data in self.order_line:
            sale_order_name = data.order_id.name
            if not sale_order_name:
                sale_order_name = so.name
            product_quantity = data.product_uom_qty

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
                if price_unit and data.order_id.currency_id and data.order_id.company_id.currency_id != data.order_id.currency_id:
                    price_unit = data.order_id.company_id.currency_id._convert(
                        price_unit,
                        data.order_id.currency_id,
                        data.order_id.company_id,
                        self.date_order or fields.Date.today(),
                    )

            # compute unit price
            if supplierinfo:
                price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price,
                                                                                            data.product_id.supplier_taxes_id,
                                                                                            taxes, company_id)
                if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                    price_unit = supplierinfo.currency_id._convert(price_unit, purchase_order.currency_id,
                                                                   purchase_order.company_id,
                                                                   fields.datetime.today())

            if self.partner_id.property_purchase_currency_id:

                value = {
                    'product_id': data.product_id.id,
                    'name': data.name,
                    'product_qty': data.product_qty,
                    'order_id': purchase_order.id,
                    'product_uom': data.product_uom.id,
                    'taxes_id': data.product_id.supplier_taxes_id.ids,
                    'date_planned': data.date_planned,
                    'hi_wi': data.hi_wi,
                    'is_5_80': data.is_5_80,

                }
            else:
                value = {
                    'product_id': data.product_id.id,
                    'name': data.name,
                    'product_qty': data.product_uom_qty,
                    'order_id': purchase_order.id,
                    'product_uom': data.product_uom.id,
                    'taxes_id': data.product_id.supplier_taxes_id.ids,
                    'price_unit': price_unit,
                    'hi_wi': data.hi_wi,
                    'is_5_80': data.is_5_80,
                }

            self.env['purchase.order.line'].create(value)

        return purchase_order

    # total_amount_in_words = fields.Char(string="Amount in Words", required=False, compute='_compute_amount_total')
    # amount_in_words_arabic = fields.Char(string="Amount in Words Arabic", required=False,
    #                                      compute='_compute_amount_total')

    @api.onchange('order_line')
    def _onchange_pro(self):
        val= []
        for rec in self.order_line:
            acc_obj = self.env['product.accessory'].search([('product_acc_id.name', '=', rec.product_id.name)])
            for obj in acc_obj:
                # acc_obj = self.sale_accessory_ids.search([('accessory_name', '=', obj.accessory_name.id),('accessory_uom_qty','=',obj.accessory_uom_qty),('sale_id.id','=',self.id)])
                # print('ppppppppppppppppp',acc_obj)
                # if not acc_obj:
                print('ggggggggggggggggggggggggggggggg',acc_obj)
                self.sale_accessory_ids.create({'accessory_name': obj.accessory_name.id,
                                                'accessory_uom_qty': obj.accessory_uom_qty,
                                                'sale_id': self.id,

                                                    })


                # # obj_acc = self.sale_accessory_ids.search([('accessory_name', '=', obj.accessory_name.id),('accessory_uom_qty','!=',obj.accessory_uom_qty),('sale_id','=',self.id)])
                # # for line in obj_acc:
                # print('88888888888888888888888acc')
                # #
                # # for acc in self.sale_accessory_ids:
                # #     if acc :
                # #         print('88888888888888888888888acc',acc)
                # #         if acc.accessory_name.id != obj.accessory_name.id and acc.accessory_uom_qty != obj.accessory_uom_qty :
                # #             print('88888888888888888888888999999999', acc)
                # #
                #             self.sale_accessory_ids.create({'accessory_name': obj.accessory_name.id,
                #                                                      'accessory_uom_qty': obj.accessory_uom_qty,
                #                                                      'sale_id': self.id,
                #
                #                                          })
                #     else:
                #         print('goooooooooooooooooooooooooooooooooooooooooooooooooooood')
                #         self.sale_accessory_ids.create({'accessory_name': obj.accessory_name.id,
                #                                       'accessory_uom_qty': obj.accessory_uom_qty,
                #                                       'sale_id': self.id,
                #
                #                                       })



    def compute_dimension_id(self):

        for rec in self:
            for line in rec.order_line:
                if line.product_id.is_sector:
                    for sect in line.product_id.supplement_sector_ids:
                        dimension_one = 0.0
                        height = 0.0
                        width = 0.0
                        product_hight = line.product_height * 1000
                        product_width = line.product_width * 1000
                        if sect.dimensions_number == 'one':
                            if sect.measured_from == 'height':
                                dimension_one = (product_hight + sect.height) / sect.division_number
                                if sect.is_side == True:
                                    side = dimension_one
                            if sect.measured_from == 'width':
                                dimension_one = (product_width + sect.width) / sect.division_number
                                if sect.is_heel == True:
                                    heel = dimension_one

                            if sect.measured_from == 'h_w':
                                dimension_one =( (product_width + sect.width) + (product_hight + sect.height)) / sect.division_number
                        if  sect.dimensions_number == 'two':
                            if sect.measured_from == 'h_w':
                                height = (product_hight + sect.height)/ sect.division_number
                                width = (product_width + sect.width)/ sect.division_number
                        if  sect.dimensions_number == 'two':
                            if sect.measured_from == 'side_heel':
                                height =  sect.side + side
                                width =  sect.heel + heel

                        rec.dimension_supplement_ids.create({'supplement_name': sect.supplement_name.id,
                                                             'supplement_height': height,
                                                             'supplement_width': width,
                                                             'dimension_one': dimension_one,
                                                             'sale_id': rec.id, })
            rec.state = 'compute'


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

    # def prepare_massage(self):
    #
    #     admin = self.env['res.users'].search([('id', '=', 2)])
    #
    #     subtype = self.env['mail.message.subtype'].search([('name', '=', 'Activities')])
    #     # if rec.users.groups_id == rec.groups:
    #     #     new_group = rec.users
    #     # [(4, pid) for pid in create_values.get('partner_ids', [])]
    #
    #     for line in self:
    #
    #         mail_mass = self.env['mail.message'].create({
    #             'email_from': admin.partner_id.email,
    #             # 'email_to':6,
    #             'author_id': admin.partner_id.id,
    #             'model': 'sale.order',
    #             'message_type': 'notification',
    #             'body': "Record Need Action",
    #             'res_id': line.id,
    #             'channel_ids': [(6, 0, [subtype.id])],
    #             'subtype_id': subtype.id,
    #             'moderation_status': 'accepted',
    #             # 'needaction_partner_ids':[(4, pid) for pid in rec.groups.users.partner_id],
    #         })
    #
    #         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #
    #         if self.partner_id:
    #             list_partner = self.partner_id
    #
    #
    #         for uid in list_partner:
    #             massage_ids = self.env['mail.mail'].create({
    #                 'subject': 'This record need you action (%s)' % (
    #                         str('sale.order') + ': ' + str(line.name)),
    #                 'body_html': 'Dear %s ' % uid.name + '<br/>This record need you action <a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
    #                     base_url, 'sale.order', line.id),
    #                 'email_from': admin.partner_id.email,
    #                 'email_to': uid.email,
    #                 'auto_delete': True,
    #                 'state': 'outgoing',
    #                 'mail_message_id': mail_mass.id,
    #                 'body': 'Dear %s ' % uid.name + '<br/>This record need you action <a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
    #                     base_url, 'sale.order', line.id),
    #
    #             })
    #             print('uuuuuuuuuuuuuuuuuuuu8888888888888888888888888888888',massage_ids)
    #             massage_ids.send()
    #

class DimensionLineHeight(models.Model):
    _name = 'dimension.line.height'
    _description = "Height"

    name = fields.Float(string='Tag Name')


class DimensionLineWidth(models.Model):
    _name = 'dimension.line.width'
    _description = "Width"

    name = fields.Float(string='Tag Name')

# product_uom_qty

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    height = []
    width = []

    product_heights = fields.Many2many('dimension.line.height', string='Height(Mt)')
    product_widths = fields.Many2many('dimension.line.width',string='Width(Mt')
    hi_wi = fields.Float(string = 'total_hi_wi',digits = 'total height and width /2')
    is_5_80 = fields.Boolean(string = '5.80' , default = True)

    product_qty_new = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_area = fields.Float(string='Area(Mt2)', digits='Product Area(Width*Height*Quantity) by mater', default=1 , compute= 'compute_area')

    @api.depends('product_heights', 'product_widths','product_qty_new')
    def compute_area(self):
        for rec in self:
            total = 0.0
            height = [{'name': res.name} for res in  rec.product_heights]
            width = [{'name': res.name} for res in  rec.product_widths]
            if  height and width and  range(len(height)) == range(len(width)) :

                for i in range(len(height)):


                    rec.product_area += height[i]['name']  *  width[i]['name'] * rec.product_qty_new
                    total +=  ((height[i]['name']  +  width[i]['name']) *2)
                rec.product_uom_qty = total / 5.80
                rec.hi_wi = total

            else:
                print('pllllllllllllllllease')
                rec.product_area = 1
                rec.product_uom_qty = 1

    @api.onchange('is_5_80')
    def onchange_is_5(self):
        for rec in self:
            if rec.is_5_80:
                rec.product_uom_qty = rec.hi_wi / 5.80
            else:
                rec.product_uom_qty = rec.hi_wi / 6



