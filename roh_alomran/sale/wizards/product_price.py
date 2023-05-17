from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ProductPrice(models.Model):
    _name = 'product.price'
    _description = 'Update Product Sales Price'

    update_type = fields.Selection(selection=[('product', 'Products'),
                                              ('category', 'Category'), ],
                                   string="Update Type", required=False, default='category')
    product_ids = fields.Many2many('product.template', string="Products", required=False)
    categ_ids = fields.Many2many("product.category", string="Product Category", )
    percentage = fields.Float('Percentage')
    shipment_ids = fields.Many2many("shipping.process", string="Shipment Exception", )

    def change_product_price(self):
        product_list = []
        new_product_list = []
        list_price = 0.0
        new_list_price = 0.0
        if self.percentage <= 0.0:
            raise ValidationError(_("Percentage should be larger than zero!"))
        if self.shipment_ids:
            for rec in self.shipment_ids:
                for line in rec.shipment_line_ids:
                    product_list.append(line.product_id.id)
        if self.update_type == 'product':
            prod_obj = self.env['product.product'].search(
                [('id', 'in', self.product_ids.ids), ('id', 'not in', product_list)])
        else:
            prod_obj = self.env['product.product'].search(
                [('id', 'not in', product_list), '|', ('categ_id', 'in', self.categ_ids.ids),
                 ('categ_id', 'child_of', self.categ_ids.ids)])
        for pro in prod_obj:
            new_product_list.append(pro)
        for price in new_product_list:
            list_price = (price.list_price * self.percentage) / 100
            new_list_price = price.list_price + list_price
            prod_value = {'list_price': new_list_price}
            price.write(prod_value)
            return {
                'name': _('Products'),
                'view_mode': 'form',
                'res_model': 'product.template',
                'type': 'ir.actions.act_window_close',
                'res_id': price.id,
            }
