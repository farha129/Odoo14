# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = "sale.order"

    install_payment  = fields.Many2one('payment.installment',string = 'Payment Method', required=True)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for install in self.install_payment.line_install:
            amount = self.amount_untaxed * install.percentage / 100
            descreption = install.payment_name.name

            test_payment_1 = self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': self.partner_id.id,
                'amount': amount,
                'description': descreption,
                'currency_id': self.company_id.currency_id.id,
                'sale_id': self.id,
                'install_id': install.id,

            })
        return res

    def action_get_payment(self):
        form_id = self.env.ref("account.view_account_payment_form").id
        tree_id = self.env.ref("account.view_account_payment_tree").id
        return {
            "name": _("Payment"),
            "view_mode": "tree,form",
            'views': [(tree_id, 'tree'),  (form_id, 'form'),
                      ],
            "res_model": "account.payment",
            "domain": [('sale_id', '=', self.id)],
            "type": "ir.actions.act_window",
            "target": "current",
        }





    

