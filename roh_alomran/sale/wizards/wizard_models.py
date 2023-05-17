# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleReportWizard(models.TransientModel):
    _name = 'sale.report.wizard'
    _description = 'Sale Report Wizard'

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    customer = fields.Many2one('res.partner', string='Customer')
    sale_person = fields.Many2one('res.users', string='Sale Person')
    warehouse = fields.Many2one('stock.warehouse', string="Warehouse", required=True)
    type = fields.Selection(selection=[('direct', 'Direct Sale'), ('deferred', 'Deferred sale')],
                            string="Type", required=True)
    include_return = fields.Boolean(string="Include Return")

    @api.constrains('date_from', 'date_to')
    def _check_rule_date_from(self):
        if any(applicability for applicability in self
               if applicability.date_to and applicability.date_from
                  and applicability.date_to < applicability.date_from):
            raise ValidationError(_('The start date must be before the end date'))

    def print_sale_report(self):
        data = {
            'model': 'sale.order',
            'form': self.read()[0]
        }
        sales = self.env['sale.order'].search([('date_order', '<', self.date_to), ('date_order', '>', self.date_from),
                                               ('type', '=', self.type),
                                               ('warehouse_id.id', '=', self.warehouse.id)])
        if self.sale_person.id:
            sales = [sale for sale in sales if sale.user_id.id == self.sale_person.id]
        if self.customer.id:
            sales = [sale for sale in sales if sale.partner_id.id == self.customer.id]

        list = []
        list_report_vals = []

        report_vals = {
            'report_start_date': self.date_from,
            'report_end_date': self.date_to,
            'partner_id': self.customer.name,
            'sale_person': self.sale_person.name,
            'include_return': self.include_return,
        }
        list_report_vals.append(report_vals)
        for sale in sales:
            sale_return_name = ""
            sale_return_qty = ""
            returns = self.env['order.return'].search([('sale_id', '=', sale.id)])
            for r in returns:
                sum = 0
                for line in r.return_line:
                    sum += line.qty_return
                sale_return_name = r.name
                sale_return_qty = sum
            vals = {
                'name': sale.name,
                'date_order': sale.date_order,
                'partner_id': sale.partner_id.name,
                'sale_person': sale.user_id.name,
                'amount_untaxed': sale.amount_untaxed,
                'amount_tax': sale.amount_tax,
                'amount_total': sale.amount_total,
                'sale_return_name': sale_return_name,
                'sale_return_qty': sale_return_qty,
                'include_return': self.include_return,
            }
            list.append(vals)
        data['sales'] = list
        data['report_vals'] = list_report_vals
        return self.env.ref('sale_fadil.action_report_sales_report').report_action(self, data=data)

# sales = self.env['sale.order'].search(
#     [('date_order', '<', self.date_to), ('date_order', '>', self.date_from), ('partner_id.id', '=', self.customer.id),
#      ('user_id.id', '=', self.sale_person.id)])
# for sale in sales:
