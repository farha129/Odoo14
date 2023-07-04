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

    sale_id = fields.Many2one('sale.order','sale order' ,required = True)
    customer_id = fields.Many2one(related='sale_id.partner_id')


# class PurchaserderLine(models.Model):
#     _inherit = 'purchase.order.line'
#     hi_wi = fields.Float(string = 'total_hi_wi',digits = 'total height and width /2')
#     is_5_80 = fields.Boolean(string = '5.80' , default = True)
#
#



class DimensionSupplement(models.Model):
    _name = "dimension.supplement"
    _description = "Dimension Supplement"

    sale_id = fields.Many2one('sale.order', string = 'Dimension Sector')
    sector_id = fields.Many2one('sector.order.line', string = 'Dimension Sector')
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

    # def _default_end_date_order(self):
    #     days = self.implemented_period end_date_order
    #     if days > 0:
    #

    installation = fields.Boolean('Installation requested?')
    end_date_order = fields.Date(string = 'End Date',readonly=True)
    sector_order_line = fields.One2many('sector.order.line', 'sale_id',string='Sectors Order Lines', copy=True)
    destination = fields.Char(string='Destination', readonly=False)
    is_delivery = fields.Boolean('Delivery request?')
    dimension_supplement_ids = fields.One2many('dimension.supplement', 'sale_id',string = 'Dimension' ,readonly=False)
    sale_accessory_ids = fields.One2many('sale.accessory','sale_id',string = 'Accessory',  readonly = False )
    number_payment = fields.Selection([('one','One'),('two','Two'),('three','Three'),('more','More')],string='Number Of Payment' )
    destination_payment  =  fields.Text(string = 'Description Payment')
    destination_paint  =  fields.Char(string = 'Description paint')
    destination_glass  =  fields.Char(string = 'Description glass')
    implemented_period = fields.Integer(string = 'implemented period', digits = 'By The Days' )
    count = fields.Integer( string='Count')
    po_count = fields.Integer(compute='_get_po', string='Request Purchase')
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=False, auto_join=True)
    contract_note = fields.Text(string = "Nots")
    state = fields.Selection(
        selection_add=[('again', 'Try Again'),('compute', 'Computed')])




    # @api.model
    # def create(self, vals):
    #     order = super(SaleOrder,self.with_context(mail_create_nolog=True)).create(vals)
    #     order.sudo().create_order_line()
    #     return order


    def action_cancel(self):
        res = super(SaleOrder, self).action_draft()
        for orders in self:
            request_ids = self.env['request.purchase'].search([('sale_id', '=', orders.id)])
            if request_ids:
                request_ids.write({'state':'cancel'})



    def _get_po(self):
        for orders in self:
            request_ids = self.env['request.purchase'].search([('sale_id', '=', orders.id)])
            self.po_count = len(request_ids)


    # def create_order_line(self):
    #
    #     val= []
    #     list = []
    #
    #     acc_all = self.env['product.product'].search([('is_accessory', '=', True)])
    #     # for all in acc_all:
    #     #     val.append(all.id)
    #
    #     for sect_obj in self.sector_order_line:
    #         sale = self.order_line.create({'product_id': sect_obj.final_product.id,
    #                        'name': sect_obj.name,
    #                        'order_id': self.id,
    #                        'product_uom_qty': sect_obj.product_area,
    #                                        })
    #
    #
    #     for all in acc_all:
    #
    #         qyt = 0
    #         for sec in self.sector_order_line:
    #
    #             acc_obj = self.env['product.accessory'].search([('product_acc_id.name', '=', sec.product_id.name),('accessory_name','=',all.id)])
    #             if acc_obj:
    #                 for obj in acc_obj:
    #                     qyt += obj.accessory_uom_qty * sec.product_number
    #
    #
    #         if qyt != 0 :
    #             self.sale_accessory_ids.create({'accessory_name': all.id,
    #                                                   'accessory_uom_qty': qyt,
    #                                                   'sale_id': self.id,
    #                                                   'product_uom': all.uom_id.id,
    #                                               })
    #
    #     self.count = 1

    #create request purchase

    def action_create_request_purchase(self):
        value = []

        self.ensure_one()
        res = self.env['request.purchase'].browse(self._context.get('id', []))
        so = self.env['sale.order'].browse(self._context.get('active_id'))
        sale_order_name = so.name
        company_id = self.env.company
        currency_id = self.env.company.currency_id.id


        request_id = res.create({
            'date_order': str(self.date_order),
            # 'name': sale_order_name,
            'customer_id': self.partner_id.id,
            'sale_id': self.id,
            'currency_id': currency_id
        })
        sale_order = self.env['sale.order'].browse(self._context.get('active_ids', []))
        message = "Request Purchase created " + '<a href="#" data-oe-id=' + str(
            request_id) + ' data-oe-model="purchase.order">@' + request_id.name + '</a>'
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
            if ava_qty > 0:

                if data.product_uom_qty > ava_qty :

                    product_quantity = data.product_uom_qty - ava_qty

                    purchase_qty_uom = data.product_uom._compute_quantity(product_quantity, data.product_id.uom_po_id)

                    # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
                    # Note: one partner can have multiple supplier info for the same product


                    value.append({
                        'product_id': data.product_id.id,
                        'name': data.product_id.name,
                        'product_qty': product_quantity,
                        'request_id': request_id.id,
                        'product_uom': data.product_uom.id,
                    })
            else:
                product_quantity = data.product_uom_qty

                value.append({
                    'product_id': data.product_id.id,
                    'name': data.product_id.name,
                    'product_qty': product_quantity,
                    'request_id': request_id.id,
                    'product_uom': data.product_uom.id,
                })

        for data in self.dimension_supplement_ids:
            qty_ids = self.env['stock.quant'].search(
                [('product_id', '=', data.supplement_name.id), ('location_id', '=', self.warehouse_id.lot_stock_id.id)])
            if qty_ids:
                ava_qty = sum(qty_ids.mapped('available_quantity'))
            else :
                ava_qty = 0.0
            if ava_qty > 0:
                if data.purchase_uom_qty > ava_qty :

                    product_quantity = data.purchase_uom_qty - ava_qty

                    value.append({
                        'product_id': data.supplement_name.id,
                        'name': data.supplement_name.name,
                        'product_qty': product_quantity,
                        'request_id': request_id.id,
                        'product_uom': data.product_uom.id,
                    })
            else:
                product_quantity = data.purchase_uom_qty

                value.append({
                    'product_id': data.supplement_name.id,
                    'name': data.supplement_name.name,
                    'product_qty': product_quantity,
                    'request_id': request_id.id,
                    'product_uom': data.product_uom.id,
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
            if ava_qty > 0 :


                if data.accessory_uom_qty > ava_qty :

                    product_quantity = data.accessory_uom_qty - ava_qty

                    value.append({
                        'product_id': data.accessory_name.id,
                        'name': data.accessory_name.name,
                        'product_qty': product_quantity,
                        'request_id': request_id.id,
                        'product_uom': data.product_uom.id,
                    })
            else:
                product_quantity = data.accessory_uom_qty

                value.append({
                    'product_id': data.accessory_name.id,
                    'name': data.accessory_name.name,
                    'product_qty': product_quantity,
                    'request_id': request_id.id,
                    'product_uom': data.product_uom.id,
                })

        self.env['request.purchase.line'].create(value)

        return request_id

    def action_open_request(self):
        tree_id = self.env.ref("sale_roh.request_purchase_tree").id
        form_id = self.env.ref("sale_roh.request_purchase_order_form").id
        return {
            "name": _("Requests Purchase"),
            "view_mode": "tree,form",
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            "res_model": "request.purchase",
            "domain": [('sale_id', '=', self.id)],
            "type": "ir.actions.act_window",
            "target": "current",
        }

    # @api.constrains('order_line')
    # def _order_line_null(self):
    #     if not self.order_line :
    #         raise ValidationError(_('Please Add products or Line' ))

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        days = self.implemented_period

        self.end_date_order =  fields.Date.to_string(self.date_order + timedelta(days))

        self.action_create_request_purchase()

        return res

    @api.depends('sector_order_line')
    def _get_supp(self):
        self.dimension_supplement_ids = [(5, 0)]
        for rec in self.sector_order_line:
            if not rec:
                continue
            else:
                heel = 0.0
                side = 0.0
                qyt = 0.0
                val = []
                val_with = []
                width2 = 0.0
                if not rec.product_id.supplement_sector_ids:
                    continue
                    # raise ValidationError(_('Please Configratin Dimension for this Sector'))


                else:
                    for sect in rec.product_id.supplement_sector_ids:
                        qyt = 0.0
                        sum = 0.0
                        toral_var = 0.0
                        toral_har = 0.0

                        obj_ditails = self.env['ditals.sector'].search([('sector_id', '=', rec.id)])
                        for obj in obj_ditails:
                            product_hight = (obj.height * 100) + 30
                            product_width = (obj.width * 100) + 30
                            var_cutter = obj.var_cutter
                            hor_cutter = obj.hor_cutter

                            sum_hight = 0.0
                            sum_with = 0.0

                            if sect.type == 'other':
                                height = (product_hight + sect.height) * sect.nmuber
                                width = (product_width + sect.width) * sect.nmuber
                                sum += height + width
                                qyt = (sum / 5.80)/ 100


                            if sect.type == 'cutter_hor' and hor_cutter:
                                if hor_cutter > 0 :
                                    sum += hor_cutter
                                qyt = sum/5.80

                            if sect.type == 'cutter_var' and var_cutter:
                                if var_cutter > 0 :
                                    sum += var_cutter
                                qyt = sum/5.80
                            if sect.type == 'side':
                                sum += ((product_hight + sect.height) * sect.nmuber)
                                side = product_hight + sect.height
                                val.append(side)
                                qyt = (sum / 5.80)/ 100

                            if sect.type == 'heel':
                                sum += ((product_width + sect.width) / sect.division_number) * sect.nmuber
                                heel = ((product_width + sect.width) / sect.division_number)
                                val_with.append(heel)
                                qyt = (sum / 5.80)/ 100

                            if sect.type == 'glass':
                                if val and val_with:
                                    for i in range(len(obj_ditails)):
                                        side = val[i]
                                        hight2 = sect.side + side
                                        heel = val_with[i]
                                        width2 = sect.heel + heel
                                        area = ((hight2 * width2) * sect.nmuber) / 100
                                        sum += area
                                    qyt = (sum / 7.42)/ 100
                                    break


                                else:
                                    hight2 = product_hight + sect.height
                                    width2 = product_width + sect.width

                                    area = ((hight2 * width2) * sect.nmuber) / 100
                                    sum += area
                                qyt = (sum / 7.42)/ 100


                            if sect.type == 'wire':
                                print(val)
                                if val and val_with:
                                    for i in range(len(obj_ditails)):
                                        side = val[i]
                                        sum_hight += (sect.side + side) * sect.nmuber
                                        # sum_hight += hight2
                                        heel = val_with[i]
                                        sum_with += (sect.heel + heel) * sect.nmuber
                                total = sum_hight / 5.80 + sum_with / 5.80
                                qyt = total/ 100

                        self.dimension_supplement_ids.create({'supplement_name': sect.supplement_name.id,
                                                                           'purchase_uom_qty': qyt ,
                                                                           'product_uom': sect.supplement_name.uom_id.id,
                                                                           'sector_id': rec.id,
                                                                           'sale_id': self.id,
                                                                           })
                        # if sup_ids:
                        #     self.update({'dimension_supplement_ids': [(4, sup_ids.id)]})



    # @api.depends('sector_order_line')
    # def _get_supp(self):
    #     for sale in self:
    #
    #         if sale.sector_order_line:
    #
    #
    #             for rec in sale.sector_order_line:
    #
    #                     heel = 0.0
    #                     side = 0.0
    #                     qyt = 0.0
    #                     val = []
    #                     val_with = []
    #
    #                     width2 = 0.0
    #
    #                     if not rec.product_id.supplement_sector_ids:
    #                         raise ValidationError(_('Please Configratin Dimension for this Sector'))
    #
    #                     else:
    #                         for sect in rec.product_id.supplement_sector_ids:
    #                                 qyt = 0.0
    #                                 sum = 0.0
    #                                 obj_ditails = self.env['ditals.sector'].search([('sector_id', '=', rec.id)])
    #                                 for obj in obj_ditails:
    #                                     product_hight = (obj.height * 100) + 30
    #                                     product_width = (obj.width * 100) + 30
    #
    #                                     sum_hight = 0.0
    #                                     sum_with = 0.0
    #                                     if sect.type == 'other':
    #                                         height=  (product_hight + sect.height) * sect.nmuber
    #                                         width=  (product_width + sect.width) * sect.nmuber
    #                                         sum += height + width
    #                                         qyt = sum / 5.80
    #
    #                                     if sect.type == 'side':
    #
    #                                        sum +=((product_hight + sect.height) * sect.nmuber)
    #                                        side = product_hight + sect.height
    #                                        val.append(side)
    #                                        qyt = sum /5.80
    #
    #                                     if sect.type == 'heel':
    #                                         sum +=( (product_width + sect.width) / sect.division_number) * sect.nmuber
    #                                         heel = ((product_width + sect.width) / sect.division_number)
    #                                         val_with.append(heel)
    #                                         qyt = sum / 5.80
    #
    #
    #                                     if sect.type == 'glass':
    #                                         for i in range(len(obj_ditails)):
    #                                             if val[i]:
    #                                                 side = val[i]
    #                                                 hight2 = sect.side + side
    #                                                 heel = val_with[i]
    #                                                 width2 = sect.heel + heel
    #
    #                                             else:
    #                                                 hight2 =  product_hight + sect.height
    #                                                 width2 = product_width + sect.width
    #
    #                                             area = ((hight2 * width2) * sect.nmuber) / 100
    #                                             sum += area
    #                                         qyt = sum / 7.42
    #                                         break
    #
    #                                     if sect.type == 'wire':
    #                                         print(val)
    #                                         for i in range(len(obj_ditails)):
    #                                             if val[i]:
    #                                                 side = val[i]
    #                                                 sum_hight += (sect.side + side) * sect.nmuber
    #                                                 # sum_hight += hight2
    #
    #                                                 heel = val_with[i]
    #                                                 sum_with +=( sect.heel + heel) * sect.nmuber
    #                                                 total = sum_hight/5.80 + sum_with/ 5.80
    #                                             else:
    #                                                 total = 0
    #                                         qyt = total
    #
    #                                 if qyt != 0:
    #                                     sup_ids= self.env['dimension.supplement'].create({'supplement_name': sect.supplement_name.id,
    #                                                                  'purchase_uom_qty': qyt/100,
    #                                                                  'product_uom': sect.supplement_name.uom_id.id,
    #                                                                  'sale_id': self.id, })
    #                                     if sup_ids:
    #                                         self.write({'dimension_supplement_ids': [(4,sup_ids.id)]})
    #
    #         else:
    #
    #             continue

            #


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




class DimensionLineWidth(models.Model):


    _name = 'dimension.line.width'
    _description = "Width"


    name = fields.Float(string='Tag Name')

# product_uom_qty
class DitalsSector(models.Model):
    _name = 'ditals.sector'
    _description = "Detals"
    name = fields.Char(string = 'Name' , )
    width = fields.Float(string ='width', digits=(3,4),store= True)
    height = fields.Float(string='height',digits=(3,4),store= True)
    hor_cutter = fields.Float(string='Horizantol Cutter',digits=(3,4),store= True)
    var_cutter = fields.Float(string='vertical Cutter',digits=(3,4),store= True)
    cutter_type = fields.Selection(related ='sector_id.cutter_type')
    sector_id = fields.Many2one('sector.order.line',string='Sector')
    is_edit = fields.Boolean(related ='sector_id.is_edit',readonly = False)

    @api.onchange('width','height')
    def onchange_width_height(self):
        self.is_edit = False

class SectorOderLine(models.Model):
    _name = 'sector.order.line'
    _description = "sector order line"
    height = []
    width = []

    name = fields.Char(string = "Description", required=True)
    detals_id = fields.One2many('ditals.sector','sector_id',string="Detils")

    product_id = fields.Many2one('product.product', string='Sector',domain="[('is_sector', '=', True)]", required=True) # Unrequired company
    final_product = fields.Many2one('product.product', string='Final Product', required=True)
    product_number = fields.Integer(string='Product Number',compute='_get_number_product')

    product_template_id = fields.Many2one(related="final_product.product_tmpl_id",
                                          string="Template Id of Selected"
                                                 " Product")

    product_heights = fields.Many2many('dimension.line.height', string='Height(Mt)', required=False, store = True)
    product_widths = fields.Many2many('dimension.line.width',string='Width(Mt)', required=False,store = True)
    hi_wi = fields.Float(string = 'total_hi_wi',digits = 'total height and width /2')
    is_5_80 = fields.Boolean(string = '5.80' , default = True)
    sale_id = fields.Many2one('sale.order', string = 'Sectors')
    is_edit = fields.Boolean(string = 'Is Edit', default = True)
    cutter_type = fields.Selection([('hor','Horizantol'),('vertical','Vertical'),('both','Both')],string = 'Cutter Type')
    dimension_supplement_ids = fields.One2many('dimension.supplement', 'sector_id', string = 'Dimension' , store=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    product_uom_qty = fields.Float(
        'Purchase Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)

    product_qty_new = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)

    def _get_number_product(self):
        for rec in self:
            ditals_ids = self.env['ditals.sector'].search([('sector_id', '=', rec.id)])
            rec.product_number = len(ditals_ids)


    def action_open_ditals_order(self):
        tree_id = self.env.ref("sale_roh.ditals_view_tree").id
        form_id = self.env.ref("sale_roh.view_detial_form").id

        return {
            "name": _("Height And Width"),
            "view_mode": "tree,form",
            'views': [(tree_id, 'tree'),(form_id, 'form')],
            "res_model": "ditals.sector",
            "domain": [('sector_id', '=', self.id)],
            "type": "ir.actions.act_window",
            "target": "current",
            "context": {'default_sector_id': self.id,'create':True},

        }



    product_area = fields.Float(string='Area(Mt2)', digits='Product Area(Width*Height*Quantity) by mater', default=1 , compute= 'compute_area',store = True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        value=[]
        self.ensure_one()
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.name = self.product_id.name

        # for rec in self:
        #     print('teeeeeeeeeeeest',self.id)
        #     if rec:
        #         heel = 0.0
        #         side = 0.0
        #         qyt = 0.0
        #         val = []
        #         listitem = []
        #         val_with = []
        #         width2 = 0.0
        #         if  rec.product_id.supplement_sector_ids:
        #             # raise ValidationError(_('Please Configratin Dimension for this Sector'))
        #             for sect in rec.product_id.supplement_sector_ids:
        #                 qyt = 0.0
        #                 sum = 0.0
        #                 obj_ditails = self.env['ditals.sector'].search([('sector_id', '=', rec.id)])
        #                 for obj in obj_ditails:
        #                     product_hight = (obj.height * 100) + 30
        #                     product_width = (obj.width * 100) + 30
        #                     sum_hight = 0.0
        #                     sum_with = 0.0
        #                     if sect.type == 'other':
        #                         height = (product_hight + sect.height) * sect.nmuber
        #                         width = (product_width + sect.width) * sect.nmuber
        #                         sum += height + width
        #                         qyt = sum / 5.80
        #
        #                     if sect.type == 'side':
        #                         sum += ((product_hight + sect.height) * sect.nmuber)
        #                         side = product_hight + sect.height
        #                         val.append(side)
        #                         qyt = sum / 5.80
        #
        #                     if sect.type == 'heel':
        #                         sum += ((product_width + sect.width) / sect.division_number) * sect.nmuber
        #                         heel = ((product_width + sect.width) / sect.division_number)
        #                         val_with.append(heel)
        #                         qyt = sum / 5.80
        #
        #                     if sect.type == 'glass':
        #                         for i in range(len(obj_ditails)):
        #                             if val[i]:
        #                                 side = val[i]
        #                                 hight2 = sect.side + side
        #                                 heel = val_with[i]
        #                                 width2 = sect.heel + heel
        #
        #                             else:
        #                                 hight2 = product_hight + sect.height
        #                                 width2 = product_width + sect.width
        #
        #                             area = ((hight2 * width2) * sect.nmuber) / 100
        #                             sum += area
        #                         qyt = sum / 7.42
        #                         break
        #
        #
        #                     if sect.type == 'wire':
        #                         print(val)
        #                         for i in range(len(obj_ditails)):
        #                             side = val[i]
        #                             sum_hight += (sect.side + side) * sect.nmuber
        #                             # sum_hight += hight2
        #
        #                             heel = val_with[i]
        #                             sum_with += (sect.heel + heel) * sect.nmuber
        #                         total = sum_hight / 5.80 + sum_with / 5.80
        #                         qyt = total
        #
        #                 value = {'supplement_name': sect.supplement_name.id,
        #                                                            'purchase_uom_qty': qyt / 100,
        #                                                            'product_uom': sect.supplement_name.uom_id.id,
        #                                                            # 'sale_id': rec.sale_id.id,
        #                                                            }
        #
        #                 listitem.append((0,0,value))
        #
        #
        #                 rec.sale_id.dimension_supplement_ids = listitem
        #
        #                 # return {'value': value}
        #             # self.sale_id.update({
        #             #     'dimension_supplement_ids': value})
        #
        #             # print("ggggggggggggggggg/ggggggggg",value)
        #             print("ggggggggggggggggg/gggggggggvalue",self.sale_id.dimension_supplement_ids)

    @api.depends('is_edit','product_qty_new')
    def compute_area(self):
        for rec in self:
            total = 0.0
            area = 0.0
            obj_ditails = self.env['ditals.sector'].search([('sector_id','=',rec.id)])
            for obj in obj_ditails:
                height = obj.height
                width = obj.width
                if  height and width :
                    total += ((height + 0.3) * 2) + ((width + 0.3) * 2)
                    if height < 1:
                        height = 1
                    if width < 1:
                        width = 1
                    area += height *  width * rec.product_qty_new
                    rec.product_area = area
                    rec.product_uom_qty = (total / 5.80) * rec.product_qty_new
                    rec.hi_wi = total

                else:
                    raise ValidationError(_('Please Enter Width and height Togter'))

        return True



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

