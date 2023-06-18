# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_sector_det(self):
        tree_id = self.env.ref("sale_roh.ditals_view_tree").id
        for production in self:

            for sale in production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id:
                sale_obj = self.env['sale.order'].search([('id','=',sale.id)])
                for obj in sale_obj:
                    for sect in obj.sector_order_line:
                        if self.product_id.id == sect.final_product.id:
                            return {
                                "name": _("Width And Height"),
                                "view_mode": "tree",
                                'views': [(tree_id, 'tree')],
                                "res_model": "ditals.sector",
                                "domain": [('sector_id', '=', sect.id)],
                                "type": "ir.actions.act_window",
                                "target": "current",

                            }
class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    bom_id = fields.Many2one('mrp.bom', string='Bill of Material')
    product_template_id = fields.Many2one(related="product_id.product_tmpl_id",
                                          string="Template Id of Selected"
                                                 " Product")


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()
        if self.sale_line_id and self.sale_line_id.bom_id:
            values["bom_id"] = self.sale_line_id.bom_id
        return values


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def create_order_line(self):

        # self.env['mrp.bom'].create({
        #     'product_tmpl_id': kit.product_tmpl_id.id,
        #     'type': 'phantom',
        #     'bom_line_ids': [(0, 0, {
        #         'product_id': p.id,
        #         'product_qty': 1,
        #     }) for p in [compo01, compo02]]
        # })
        acc_all = self.env['product.product'].search([('is_accessory', '=', True)])
        for all in acc_all:
            qyt = 0
            for sec in self.sector_order_line:

                acc_obj = self.env['product.accessory'].search(
                    [('product_acc_id.name', '=', sec.product_id.name), ('accessory_name', '=', all.id)])
                if acc_obj:
                    for obj in acc_obj:
                        qyt += obj.accessory_uom_qty

            if qyt != 0:
                self.sale_accessory_ids.create({'accessory_name': all.id,
                                                'accessory_uom_qty': qyt,
                                                'sale_id': self.id,
                                                'product_uom': all.uom_id.id,
                                                })


        for sect_obj in self.sector_order_line:
            bill = self.env['mrp.bom'].create({'product_tmpl_id': sect_obj.product_template_id.id,
                                               'product_qty': sect_obj.product_area,
                                               # 'product_qty': sect_obj.product_number,
                                               })

            val=[]
            # bill= [(5, 0)]
            val.append({'product_id': sect_obj.product_id.id,
                        'product_qty': sect_obj.product_uom_qty,
                        'product_uom_id': sect_obj.product_uom.id,
                        'bom_id': bill.id,
                        })


            for supp in self.dimension_supplement_ids:
                if supp.sector_id == sect_obj:

                   val.append({'product_id': supp.supplement_name.id,
                         'product_qty': supp.purchase_uom_qty,
                         'product_uom_id': supp.product_uom.id,
                         'bom_id': bill.id,
                     })

            self.env['mrp.bom.line'].create(val)





            self.order_line.create({'product_id': sect_obj.final_product.id,
                                       'name': sect_obj.name,
                                       'bom_id': bill.id,
                                       'order_id': self.id,
                                       'product_number': sect_obj.product_number,
                                       'product_uom_qty': sect_obj.product_area,
                                   })



            self.count = 1


