# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Hrincentive(models.Model):
    _name = 'hr.incentive'
    _description = 'incentive Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Ref", default="/", readonly=True)
    descripton = fields.Text(string="Description", )
    date = fields.Date(string="Date Request", default=fields.Date.today(), readonly=True)
    type_selection = fields.Selection([
        ('one_emp', 'Certain Employee'),
        ('many_emp', 'Many Employee'),
        ('all_staff_dep', 'All Staff in Department'),
        ('all_staff', 'All Staff'),
    ], string="Staff Payments",  track_visibility='onchange', copy=False, required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee",)
    employee_ids = fields.Many2many('hr.employee', string="Employees",)



    department_id = fields.Many2one('hr.department',   store=True,
                                    string="Department")
    payment_date = fields.Date(string="Payment Start Date", required=True,)
    incentive_lines = fields.One2many('hr.incentive.line', 'incentive_id', string="incentive Line", index=True)
    emp_account_id = fields.Many2one('account.account', string="Incentive Account")
    treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    incentive_amount = fields.Float(string="Incentive Amount", required=True)
    total_amount = fields.Float(string="Total Amount", readonly=True, store=True,)


    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )
    #
    #

    @api.constrains('incentive_amount')
    def _check_amount(self):
        if self.incentive_amount <= 0.0 :
            raise ValidationError(_('Incentive Amount Must be Big Than Zeroo'))

    @api.model
    def create(self, vals):


        vals['name'] = self.env['ir.sequence'].get('hr.incentive.seq') or ' '
        res = super(Hrincentive, self).create(vals)
        return res

    @api.model
    def default_get(self, field_list):
        result = super(Hrincentive, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result



    def action_refuse(self):
        return self.write({'state': 'refuse'})


    def action_submit(self):
        self.compute_line()
        self.write({'state': 'waiting_approval_1'})


    def action_cancel(self):
        self.write({'state': 'cancel'})



    def action_approve(self):
        for data in self:
            for line in data.incentive_lines:
                contract_obj = self.env['hr.contract'].search([('employee_id', '=', line.employee_id.id),
                                                           ('state', '=', 'open')], limit=1)
            if not contract_obj:
                raise UserError(_('You must Define a Contract Running for All employee.'))

            else:
                self.write({'state': 'approve'})

    def compute_line(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for incentive in self:
            incentive.incentive_lines.unlink()

            date_start = datetime.strptime(str(incentive.payment_date), '%Y-%m-%d')
            amount = incentive.incentive_amount
            if incentive.type_selection == 'one_emp':
                self.env['hr.incentive.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': incentive.employee_id.id,
                    'incentive_id': incentive.id})
                self.total_amount = amount

            elif incentive.type_selection == 'many_emp':
                for emp in incentive.employee_ids:
                    self.env['hr.incentive.line'].create({
                        'date': date_start,
                        'amount': amount,
                        'employee_id': emp.id,
                        'incentive_id': incentive.id})
                    self.total_amount += amount


            elif incentive.type_selection == 'all_staff_dep':
                emp_obj = self.env['hr.employee'].search([('department_id', '=',incentive.department_id.id)])

                for emp in emp_obj:
                    self.env['hr.incentive.line'].create({
                        'date': date_start,
                        'amount': amount,
                        'employee_id': emp.id,
                        'incentive_id': incentive.id})
                    self.total_amount += amount


            else:
                emp_obj = self.env['hr.employee'].search([('active', '=','True')])

                for emp in emp_obj:
                    self.env['hr.incentive.line'].create({
                        'date': date_start,
                        'amount': amount,
                        'employee_id': emp.id,
                        'incentive_id': incentive.id})
                    self.total_amount += amount

        return True



    def unlink(self):
        for incentive in self:
            if incentive.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a incentive which is not in draft or cancelled state')
        return super(Hrincentive, self).unlink()



class InstallmentLine(models.Model):
    _name = "hr.incentive.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    paid = fields.Boolean(string="Paid")
    incentive_id = fields.Many2one('hr.incentive', string="incentive Ref.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_incentives(self):
        """This compute the incentive amount and total incentives count of an employee.
            """
        self.incentive_count = self.env['hr.incentive'].search_count([('employee_id', '=', self.id)])

    incentive_count = fields.Integer(string="incentive Count", compute='_compute_employee_incentives')


