# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError


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
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',)
    product_id = fields.Many2one('product.template', string = 'product')
    purchase_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)



class SaleAccessory(models.Model):
    _name = "sale.accessory"
    _description = "Accessory"

    accessory_name = fields.Many2one('product.product', string='Accessory')
    accessory_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',)
    sale_id = fields.Many2one('sale.order', string = 'Accessory')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    installation = fields.Boolean('Installation requested?')
    order_line = fields.One2many('sale.order.line', 'order_id',string='Order Lines',domain= [('is_active','=',True)],  states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    destination = fields.Char(string='Destination', readonly=False)
    is_delivery = fields.Boolean('Delivery request?')


    # supplement_ids = fields.One2many('dimension.supplement','sale_id',string = 'Dimension' )
    dimension_supplement_ids = fields.One2many('dimension.supplement','sale_id',string = 'Dimension' )
    sale_accessory_ids = fields.One2many('sale.accessory',compute='_get_acc',string = 'Accessory', readonly = False )
    number_payment = fields.Selection([('one','One'),('two','Two'),('three','Three'),('more','More')],string='Number Of Payment' )
    destination_payment  =  fields.Text(string = 'Description Payment')
    implemented_period = fields.Integer(string = 'implemented period', digits = 'By The Days' )
    state = fields.Selection(
        selection_add=[('again', 'Try Again'),('compute', 'Computed')])

    @api.constrains('order_line')
    def _order_line_null(self):
        if not self.order_line :
            raise ValidationError(_('Please Add products or Line' ))

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for acc in self.sale_accessory_ids:
            sale = self.order_line.create({
                'order_id': self.id,
                'product_id': acc.accessory_name.id,
                'product_uom_qty': acc.accessory_uom_qty,
                'name': acc.accessory_name.name,
                'is_active': False,
                'price_unit':acc.price_unit,
            })




        return res

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

    def _get_acc(self):
        # acc_ids = []

        for rec in self.order_line:
            if not rec:
                continue
            else:

                acc_obj = self.env['product.accessory'].search([('product_acc_id.name', '=', rec.product_id.name)])
                if acc_obj:

                    for obj in acc_obj:
                        acc_ids = self.env['sale.accessory'].create({'accessory_name': obj.accessory_name.id,
                                                        'accessory_uom_qty': obj.accessory_uom_qty,
                                                        'sale_id': self.id,
                                                        'product_uom': obj.accessory_name.uom_id.id,
                                                        'price_unit':rec._get_display_price(obj.accessory_name),


                                                           })

                    self.write({'sale_accessory_ids':[(4,acc_ids.id)]})
                else :
                    self.write({'sale_accessory_ids':[(4,0)]})


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


    def compute_dimension_id(self):

            for rec in self.order_line:
                heel = 0.0
                side = 0.0
                hight2 = 0.0
                width2 = 0.0

                if rec.product_id.is_sector:

                        for sect in rec.product_id.supplement_sector_ids:

                            height = [{'name': res.name} for res in rec.product_heights]
                            width = [{'name': res.name} for res in rec.product_widths]
                            if height and width and range(len(height)) == range(len(width)):



                                qyt = 0.0

                                for i in range(len(height)):

                                    product_hight = height[i]['name']  * 100
                                    product_width = width[i]['name'] * 100
                                    print('yyyyyyyyyyyyyyyyyyyy',product_hight)
                                    if sect.type == 'side':

                                       qyt += (product_hight + sect.height) * sect.nmuber
                                       side = (product_hight + sect.height) * sect.nmuber

                                    if sect.type == 'heel':
                                        qyt += ((product_width + sect.width) / sect.division_number) * sect.nmuber
                                        heel = ((product_width + sect.width) / sect.division_number) * sect.nmuber

                                    if sect.type == 'glass':
                                        hight2 = sect.side + side
                                        print('hight2glass',hight2)
                                        print('hight2glasssect.side',sect.side)
                                        print('hight2glassside',side)
                                        width2 = sect.heel + heel
                                        qyt += (hight2 *width2) / 5
                                    if sect.type == 'wire':
                                        hight2 = sect.side + side
                                        print('hight2wwww', hight2)
                                        print('hight2www.side', sect.side)
                                        print('hight2wwwwside', side)
                                        width2 = sect.heel + heel
                                        qyt += (hight2 + width2)


                                rec.order_id.dimension_supplement_ids.create({'supplement_name': sect.supplement_name.id,
                                                             'purchase_uom_qty': qyt,
                                                             'product_id': sect.product_id.id,
                                                             'product_uom': sect.product_id.uom_id.id,
                                                             'sale_id': self.id, })

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

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    height = []
    width = []

    product_heights = fields.Many2many('dimension.line.height', string='Height(Mt)')
    product_widths = fields.Many2many('dimension.line.width',string='Width(Mt')
    hi_wi = fields.Float(string = 'total_hi_wi',digits = 'total height and width /2')
    is_5_80 = fields.Boolean(string = '5.80' , default = True)
    is_active = fields.Boolean(string = 'Is active', default = True)
    # note_glass = fields.Char(string = 'Description Glass')

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

                    total +=  ((height[i]['name']  +  width[i]['name']) *2)
                    if height[i]['name'] < 1 :
                        height[i]['name'] = 1
                    if width[i]['name'] < 1 :
                        width[i]['name'] = 1

                    rec.product_area += height[i]['name']  *  width[i]['name'] * rec.product_qty_new
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

    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_area,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.depends('product_area', 'discount', 'price_unit', 'tax_id')
    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.product_area,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id if not self.display_type else False,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

    # def _acc_in_move(self):
    #
    #     for rec in self:
    #
    #         for obj in rec.order_id.sale_accessory_ids :
    #             # for line in rec.order_line.move_ids:
    #             #     line.append([(0, 0, {'product_id': obj.accessory_name.id, 'sale_line_id': rec.id,'product_uom': obj.accessory_name.uom_po_id.id,'product_uom_qty': obj.accessory_uom_qty})])
    #             val = {'product_id': obj.accessory_name.id,
    #                                             'name': rec.name or '',
    #                                             'product_uom': obj.accessory_name.uom_po_id.id,
    #                                             'product_uom_qty': obj.accessory_uom_qty,
    #                                             'location_id': rec.warehouse_id.lot_stock_id.id,
    #                                             'location_dest_id':  self.env.ref("stock.stock_location_customers").id,
    #                                              'sale_line_id': rec.id,
    # #
    #                                                }
    #         move_id = self.env['stock.move'].create(val)
    #         rec.update({'move_ids': [(4, move_id.id)]})
    #
    #         print('00000000000000000000000000000000000000000000000000000000000000000000000000000000000rec.move_idsrec.move_ids',rec.move_ids)




