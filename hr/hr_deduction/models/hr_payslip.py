# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Ijaz Ahammed (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

import babel
from odoo import models, fields, api, tools, _
from datetime import date, datetime



class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    deduction_ids = fields.Many2many('hr.deduction')

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
        return

    # @api.model
    # def get_inputs(self, contracts, date_from, date_to):
    #     """
    #     function used for writing late check-in record in payslip
    #     input tree.
    #
    #     """
    #     res = super(PayslipDeduction, self).get_inputs(contracts, date_to, date_from)
    #     deduction = self.env.ref('hr_deduction.hr_deduction_id')
    #     contract = self.contract_id
    #     deduction_ids = self.env['hr.deduction'].search([('employee_id', '=', self.employee_id.id),
    #                                                          ('date', '<=', self.date_to),
    #                                                          ('date', '>=', self.date_from),
    #                                                          ('state', '=', 'approved'),
    #                                                          ])
    #     amount = deduction.mapped('amount')
    #     cash_amount = sum(amount)
    #     if deduction_ids:
    #         self.deduction_ids = deduction_ids
    #         input_data = {
    #             'name': deduction.name,
    #             'code': deduction.code,
    #             'amount': cash_amount,
    #             'contract_id': contract.id,
    #         }
    #         res.append(input_data)
    #     return res
    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        deduction_obj = self.env['hr.deduction'].search(['&', ('employee_id', '=', emp_id.id),('state', '=','approved'),('date', '<=', self.date_to),('date', '>=', self.date_from)])
        print('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh',deduction_obj)
        amount = deduction_obj.mapped('amount')
        cash_amount = sum(amount)
        # for ded in deduction_obj:
        print('mmmmmmmmmmmmmmmmmm',res)
        for result in res:
            print('mmmmmmmmmiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            if result.get('code') == 'DE':
                # result['name'] = ded.name
                result['amount'] = cash_amount
                # result['contract_id'] = contract_ids.id
                # result['loan_line_id'] = ded.id
                print('kkkkkkkkkkkkkkkkk')
        return res


    def action_payslip_done(self):
        """
        function used for marking deducted Late check-in
        request.

        """
        for recd in self.late_check_in_ids:
            recd.state = 'deducted'
        return super(PayslipDeduction, self).action_payslip_done()
