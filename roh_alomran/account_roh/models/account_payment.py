# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta




class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.payment.register"
    description = fields.Char(string = 'Description' ,copy=False)

    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)

        res.update({
            'description': self.description,

        })
        return res

class AccountPayment(models.Model):
    _inherit = "account.payment"

    description = fields.Char(string = 'Description' ,copy=False)
    amount_arabic_word = fields.Char(string = 'Amount Arabic Word',compute= '_get_arabic_word')

    @api.depends('currency_id', 'amount')
    def _get_arabic_word(self):
        self.amount_arabic_word = self.currency_id.with_context(lang='ar_001').amount_to_text(
            self.amount) if self.currency_id else False


