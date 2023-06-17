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
