# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta



class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'
    report_header_english = fields.Text(related='company_id.report_header_english', readonly=False)
    street = fields.Char(related='company_id.street', readonly=False)
    city = fields.Char(related='company_id.city', readonly=False)
    street2 = fields.Char(related='company_id.street2', readonly=False)
    company_registry = fields.Char(related='company_id.company_registry', readonly=False)

class ResCompany(models.Model):
    _inherit = "res.company"
    report_header_english = fields.Text(string='Company Tagline English', help="Appears by default on the top right corner of your printed documents (report header).")
