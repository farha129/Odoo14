# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import date, datetime



class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    incentive_line_id = fields.Many2one('hr.incentive.line', string="incentive")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []
        ttyme = datetime.strptime(str(date_from), '%Y-%m-%d')

        # ttyme = datetime.fromtimestamp(time.mktime(datetime.strptime(date_from, "%Y-%m-%d")))
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (
        employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id
        
       # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines
        if contracts:
            input_line_ids = self.get_inputs(contracts, date_from, date_to)
            input_lines = self.input_line_ids.browse([])
            for r in input_line_ids:
                input_lines += input_lines.new(r)
            self.input_line_ids = input_lines
            print('input_line_idsinput_line_ids888888888888888888888888888888',input_line_ids)
            
        return

    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        inc_obj = self.env['hr.incentive'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
        print('9999999iiiiiiiiiiiiiiiiiiiii999999999999inc_obj',inc_obj)
        for incentive in inc_obj:
            if date_from <= incentive.incentive_lines.date <= date_to and not incentive.incentive_lines.paid:
                print('xxxxxxxxxxx',res)

                for result in res:
                    print('xxxxxxxxggggggggggggggggggggxxx', result)

                    if result.get('code') == 'INC':
                        result['amount'] = incentive.incentive_amount
                        result['incentive_line_id'] = incentive.id


        return res

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.incentive_line_id:
                line.incentive_line_id.paid = True
                line.incentive_line_id.incentive_id._compute_incentive_amount()
        return super(HrPayslip, self).action_payslip_done()
