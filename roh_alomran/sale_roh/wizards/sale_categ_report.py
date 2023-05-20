# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
import psycopg2
import pytz
from datetime import timedelta
from functools import partial
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
from odoo.tools import float_is_zero, float_round


class pos_report(models.AbstractModel):
    _name = 'report.sale_fadil.report_sale_detail'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        customer_id = data['customer_id']
        if data['customer_id'] and data['sale_person']:
            orders_lines_ids = self.env['sale.order.line'].search(
                [('order_id.date_order', '>=', data['start_date']), ('order_id.date_order', '<=', data['end_date']),
                 ('order_id.state', '=', 'sale'), ('warehouse_id', '=', data['warehouse_id']),
                 ('order_id.partner_id', '=', data['customer_id']),
                 ('order_id.user_id', '=', data['sale_person']),
                 ('product_id.categ_id', 'in', data['category_id'])])
        elif data['customer_id'] and not data['sale_person']:
            orders_lines_ids = self.env['sale.order.line'].search(
                [('order_id.date_order', '>=', data['start_date']), ('order_id.date_order', '<=', data['end_date']),
                 ('order_id.state', '=', 'sale'), ('warehouse_id', '=', data['warehouse_id']),
                 ('order_id.partner_id', '=', data['customer_id']),
                 ('product_id.categ_id', 'in', data['category_id'])])

        elif not data['customer_id'] and data['sale_person']:
            orders_lines_ids = self.env['sale.order.line'].search(
                [('order_id.date_order', '>=', data['start_date']), ('order_id.date_order', '<=', data['end_date']),
                 ('order_id.state', '=', 'sale'), ('warehouse_id', '=', data['warehouse_id']),
                 ('order_id.user_id', '=', data['sale_person']),
                 ('product_id.categ_id', 'in', data['category_id'])])
        elif not data['customer_id'] and not data['sale_person']:
            orders_lines_ids = self.env['sale.order.line'].search(
                [('order_id.date_order', '>=', data['start_date']), ('order_id.date_order', '<=', data['end_date']),
                 ('order_id.state', '=', 'sale'), ('warehouse_id', '=', data['warehouse_id']),
                 ('product_id.categ_id', 'in', data['category_id'])])

        records = []
        if orders_lines_ids:
            lines = []
            records = self.env['sale.order.line'].browse(orders_lines_ids.ids)
            # for order in orders_lines_ids:
            #     lines.append({
            #         'order':order.pos_reference,'time':order.date_order.time(),'date':order.date_order.date(),'amount':order.amount_total,'customer':order.partner_id.name})
            # data.update({'lines':lines})
            orders = []
            for order in orders_lines_ids:
                qty_ids = self.env['stock.quant'].search(
                    [('product_id', '=', order.product_id.id), ('location_id', '=', data['location_id'])])
                qty = sum(qty_ids.mapped('available_quantity'))
                # sele_convert_qty = order.product_uom._compute_quantity(order.product_uom_qty, data['uom_id'])
                orders.append({'code': order.product_id.default_code, 'qty': qty, 'product_name': order.product_id.name,
                               'order_qty': order.product_uom_qty, 'uom': order.product_uom.name,
                               'price': order.price_unit})
            data.update({'orders': orders})
        return {'data': data, 'docs': records, 'orders': orders}
