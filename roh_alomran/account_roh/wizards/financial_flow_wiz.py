# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FinancialFlowkWizard(models.TransientModel):
    _name = "financial.flow.wizard"
    _description = 'Financial Flow Wizard'

    date_from = fields.Datetime('Start Date')
    date_to = fields.Datetime('End Date')
    customer_id = fields.Many2one('res.partner',string='Customer')
    report_type = fields.Selection(
        [('statement', 'Customer Statement'), ('report_finan_follow', 'Financial Flow')],
        string='Report Type', required=True, default='report_finan_follow')

    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
		'ids': self.ids,
		'model': self._name,
		'form': data,
 
		}
        
        return self.env.ref('account_roh.report_financial_flow_ids').report_action(self, data=datas)

