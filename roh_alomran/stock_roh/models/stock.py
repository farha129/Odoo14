# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta



class Picking(models.Model):
    _inherit = "stock.picking"

    def _get_po(self):
        for orders in self:
            purchase_ids = self.env['purchase.order'].search([('partner_ref', '=', self.name)])
        orders.po_count = len(purchase_ids)

    po_count = fields.Integer(compute='_get_po', string='Purchase Orders')



    def action_create_purchase_order(self):
        self.ensure_one()

        res = self.env['purchase.order'].browse(self._context.get('id', []))
        picking = self.env['stock.picking'].browse(self._context.get('active_ids'))
        pricelist = self.partner_id.property_product_pricelist
        partner_pricelist = self.partner_id.property_product_pricelist
        picking_name = self.name

        company_id = self.env.company
        if self.partner_id.property_purchase_currency_id:
            currency_id = self.partner_id.property_purchase_currency_id.id
        else:
            currency_id = self.env.company.currency_id.id

        purchase_order = res.create({
            'partner_id': self.partner_id.id,
            'date_order': str(self.scheduled_date),
            'origin': picking_name,
            'currency_id': currency_id,
            'partner_ref': self.name,
            'picking_type_id': self.picking_type_id.warehouse_id.in_type_id.id,

        })

        message = "Purchase Order created " + '<a href="#" data-oe-id=' + str(
            purchase_order.id) + ' data-oe-model="purchase.order">@' + purchase_order.name + '</a>'
        self.message_post(body=message)
        for data in self.move_ids_without_package:
            picking_name = self.name
            if not picking_name:
                picking_name = self.name
            product_quantity = data.product_uom_qty - data.forecast_availability
            purchase_qty_uom = data.product_uom._compute_quantity(product_quantity, data.product_id.uom_po_id)

            # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
            # Note: one partner can have multiple supplier info for the same product
            supplierinfo = data.product_id._select_seller(
                partner_id=purchase_order.partner_id,
                quantity=purchase_qty_uom - data.forecast_availability,
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


            # compute unit price
            if supplierinfo:
                price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price,
                                                                                            data.product_id.supplier_taxes_id,
                                                                                            taxes, company_id)
                if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                    price_unit = supplierinfo.currency_id._convert(price_unit, purchase_order.currency_id,
                                                                   purchase_order.company_id,
                                                                   fields.datetime.today())

            if data.product_uom_qty != data.forecast_availability:

                if self.partner_id.property_purchase_currency_id:

                    value = {
                        'product_id': data.product_id.id,
                        'name': data.name,
                        'product_qty':  data.product_uom_qty - data.forecast_availability,
                        'order_id': purchase_order.id,
                        'product_uom': data.product_uom.id,
                        'taxes_id': data.product_id.supplier_taxes_id.ids,
                        'date_planned': data.date_planned,
                        # 'hi_wi': data.hi_wi,
                        # 'is_5_80': data.is_5_80,

                    }
                else:
                    value = {
                        'product_id': data.product_id.id,
                        'name': data.name,
                        'product_qty':  data.product_uom_qty - data.forecast_availability,
                        'order_id': purchase_order.id,
                        'product_uom': data.product_uom.id,
                        'taxes_id': data.product_id.supplier_taxes_id.ids,
                        'price_unit': price_unit,

                        # 'hi_wi': data.hi_wi,
                        # 'is_5_80': data.is_5_80,
                    }

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