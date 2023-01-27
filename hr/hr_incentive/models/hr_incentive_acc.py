# -*- coding: utf-8 -*-
import time
from odoo import models,fields, api,_
from odoo.exceptions import UserError


class HrincentiveAcc(models.Model):
    _inherit = 'hr.incentive'

    move_id = fields.Many2one('account.move', string="Accont Move")

    def action_approve(self):
        """This create account move for request.
            """
        incentive_approve = self.env['ir.config_parameter'].sudo().get_param('account.incentive_approve')
        count = 0
        for data in self:
            for line in data.incentive_lines:
                contract_obj = self.env['hr.contract'].search([('employee_id', '=', line.employee_id.id),
                                                               ('state', '=', 'open')], limit=1)
                if not contract_obj:
                    count += 1
        if count > 0:
            raise UserError(_('You must Define a contract for all employee.'))

        if not self.incentive_lines:
            raise UserError(_('You must compute installment before Approved.'))
        if incentive_approve:
            self.write({'state': 'waiting_approval_2'})
        else:
            if not self.emp_account_id or not self.treasury_account_id or not self.journal_id:
                raise UserError(_('You must enter employee account & Treasury account and journal to approve.'))
            if not self.incentive_lines:
                raise UserError(_('You must compute incentive Request before Approved.'))
            timenow = time.strftime('%Y-%m-%d')
            for incentive in self:
                amount = incentive.incentive_amount
                incentive_name = incentive.employee_id.name
                reference = incentive.name
                journal_id = incentive.journal_id.id
                debit_account_id = incentive.treasury_account_id.id
                credit_account_id = incentive.emp_account_id.id
                debit_vals = {
                    'name': incentive_name,
                    'account_id': debit_account_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'incentive_id': incentive.id,
                }
                credit_vals = {
                    'name': incentive_name,
                    'account_id': credit_account_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'incentive_id': incentive.id,

                }

                vals = {
                    # 'name': 'incentive For' + ' ' + incentive_name,
                    'narration': incentive_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'date': timenow,
                    # 'move_type': 'in_receipt',
                    'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                }
                move = self.env['account.move'].create(vals)
                move.post()

                self.move_id = move.id


            self.write({'state': 'approve'})
        return True


    def action_double_approve(self):
        """This create account move for request in case of double approval.
            """
        if not self.emp_account_id or not self.treasury_account_id or not self.journal_id:
            raise UserError(_('You must enter employee account & Treasury account and journal to approve.'))

        timenow = time.strftime('%Y-%m-%d')
        for incentive in self:
            amount = incentive.incentive_amount
            incentive_name = incentive.employee_id.name
            reference = incentive.name
            journal_id = incentive.journal_id.id
            debit_account_id = incentive.treasury_account_id.id
            credit_account_id = incentive.emp_account_id.id
            debit_vals = {
                'name': incentive_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'incentive_id': incentive.id,
            }
            credit_vals = {
                'name': incentive_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'incentive_id': incentive.id,
            }
            vals = {
                'narration': incentive_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                 
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            self.move_id = move.id

            move.post()
        self.write({'state': 'approve'})
        return True


class HrincentiveLineAcc(models.Model):
    _inherit = "hr.incentive.line"


    def action_paid_amount(self):
        """This create the account move line for payment of each installment.
            """
        timenow = time.strftime('%Y-%m-%d')
        for line in self:
            if line.incentive_id.state != 'approve':
                raise UserError(_('incentive Request must be approved'))
            amount = line.amount
            incentive_name = line.employee_id.name
            reference = line.incentive_id.name
            journal_id = line.incentive_id.journal_id.id
            debit_account_id = line.incentive_id.emp_account_id.id
            credit_account_id = line.incentive_id.treasury_account_id.id
            debit_vals = {
                'name': incentive_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,

            }
            credit_vals = {
                'name': incentive_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                # 'exclude_from_invoice_tab': True,
                # 'account_internal_type': 'payable',

            }
            vals = {

                'narration': incentive_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.post()
        return True


class HrPayslipAcc(models.Model):
    _inherit = 'hr.payslip'


    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.incentive_line_id:
                line.incentive_line_id.action_paid_amount()
        return super(HrPayslipAcc, self).action_payslip_done()

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    incentive_id = fields.Many2one('hr.incentive', string="incentive")

# class AccountMove(models.Model):
#     _inherit = 'account.move'
#     invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,default=fields.Date.today(),
#                                states={'draft': [('readonly', False)]})
#
#
#









