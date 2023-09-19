# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta

class PaymentInstallment(models.Model):
    _name = "payment.installment"
    _description = "Payment Installment"

    name = fields.Char(string="Installment Name",)
    line_install = fields.One2many('payment.installment.line', 'install_id', string="Install Line", index=True)

class PaymentInstallmentLine(models.Model):
    _name = "payment.installment.line"
    _description = "Payment Installment Line"

    name = fields.Char(string="Name",)


    payment_name = fields.Many2one('payment.installment.line.name',string = 'Payment Name')

    percentage = fields.Integer(string = 'Percentage %')
    apply_after = fields.Selection(
        [('in_contract', 'In Contracting'),('cut', 'Cut'), ('gathering', 'Gathering'), ('installation', 'Installation'), ('glass', 'Glass')],
        string='Apply After')
    install_id = fields.Many2one('payment.installment',string = 'Payment Installment')

class PaymentInstallmentLineName(models.Model):
    _name = "payment.installment.line.name"
    _description = "Payment Installment Name"

    name = fields.Char(string="Name",)




    
    

 
