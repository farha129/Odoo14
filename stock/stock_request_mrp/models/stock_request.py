
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _name = "stock.request"
    _description = "Stock Request"

    name = fields.Char()
    warehouse_id = fields.Many2one('stock.warehouse',string = 'Warehouse')
    location_from = fields.Many2one('stock.location', "From", related=False )
    location_to = fields.Many2one('stock.location', "To", related=False )
    request_line_ids = fields.One2many('stock.request.line','request_id',string ='Request Line')
    production_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Orders",
        readonly=True,
        copy=False,
    )


    def create_transfer(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        mrp_brw = self.env['mrp.production'].browse(active_id)
        stock_picking = (
            self.env["stock.picking"].create(
                {

                    'picking_type_id': self.warehouse_id.int_type_id.id,
                    # 'partner_id': self.customer_id.id,
                    'stock_request_id': self.id,
                    'origin': mrp_brw.name,
                    'location_dest_id': self.location_to.id,
                    'location_id': self.location_from.id,
                }
            )
        )
        for rec in self.request_line_ids:
            stock_move = self.env["stock.move"].create(
                {
                    "name": "Test Move",
                    "product_id": rec.product_id.id,
                    "product_uom_qty": rec.product_uom_qty,
                    "product_uom": rec.product_id.uom_id.id,
                    "picking_id": stock_picking.id,
                    'picking_type_id': self.warehouse_id.int_type_id.id,
                    'stock_request_id': self.id,
                    "state": "draft",
                    "location_dest_id":  self.location_to.id,
                    "location_id":  self.location_from.id,
                }
            )

    # production_count = fields.Integer(
    #     string="Manufacturing Orders count",
    #     compute="_compute_production_ids",
    #     readonly=True,
    # )

    # @api.depends("production_ids")
    # def _compute_production_ids(self):
    #     for request in self:
    #         request.production_count = len(request.production_id)
    #
    #
    #
    # def action_view_mrp_production(self):
    #     action = self.env["ir.actions.act_window"]._for_xml_id(
    #         "mrp.mrp_production_action"
    #     )
    #     productions = self.mapped("production_ids")
    #     if len(productions) > 1:
    #         action["domain"] = [("id", "in", productions.ids)]
    #     elif productions:
    #         action["views"] = [
    #             (self.env.ref("mrp.mrp_production_form_view").id, "form")
    #         ]
    #         action["res_id"] = productions.id
    #     return action
    #

class StockRequestLine(models.Model):
    _name = "stock.request.line"
    _description = "Stock Request Line"

    name = fields.Char(string='Description', required=False)
    request_id = fields.Many2one('stock.request',string = 'stock request')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', )
    product_uom_qty = fields.Float(string='Quantity', digits='Accessory Unit of Measure', default=1.0)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        value = []
        self.ensure_one()
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.name = self.product_id.name

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_request_id = fields.Many2one("stock.request", string="Stock Request", readonly=True)

class StockMove(models.Model):
    _inherit = 'stock.move'

    stock_request_id = fields.Many2one("stock.request.line", string="Stock Request", readonly=True)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def get_transaction_stock(self):
        tree_id = self.env.ref("stock.vpicktree").id
        form_id = self.env.ref("stock.view_picking_form").id
        for production in self:
                stock_obj = self.env['stock.picking'].search([('origin' ,'=', production.name)])
                print('uiiiiiiiiiiiiiiiitttttttttttttttttttttttttttttttttt')
                if stock_obj:
                    return {
                        "name": _("Stock"),
                        "view_mode": "tree",
                        'views': [(tree_id , 'tree')],
                        "res_model": "stock.picking",
                        "domain": [('origin', '=', production.name)],
                        "type": "ir.actions.act_window",
                        "target": "current",

                    }

