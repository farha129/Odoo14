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
                print('ffffffffffffffffffffftry', rec.name)
                print('dayuuuuuuuuuuuuuuuuuuuuuuuuuu', date_try_s)
                print('dayuuuuuuuuuuuuuuuuuuummmmmmmmmmmmmmmmmuuuuuuu', date_try)

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



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[]")
    product_height = fields.Float(string='Height(Mt)', digits='Product Height', default=0)
    product_width = fields.Float(string='Width(Mt)', digits='Product Width by mater', default=0)
    product_area = fields.Float(string='Area(Mt2)', digits='Product Area(Width*Height*Quantity) by mater', default=1 , compute= 'compute_area')

    @api.depends('product_height', 'product_width','product_uom_qty')
    def compute_area(self):
        for rec in self:
            rec.product_area = rec.product_height * rec.product_width * rec.product_uom_qty

