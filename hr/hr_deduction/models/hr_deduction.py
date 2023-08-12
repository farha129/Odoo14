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
from odoo import models, fields, api


class HrDeduction(models.Model):
    _name = 'hr.deduction'
    _description = 'Deduction'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string = 'ref',readonly= True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    # late_minutes = fields.Integer(string="Late Minutes")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    date = fields.Date(string="Date")
    description = fields.Text(string = 'Description')
    amount = fields.Float(string="Amount")
    state = fields.Selection([('draft', 'Draft'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused'),
                              ('deducted', 'Deducted')], string="state", track_visibility='onchange',
                             default="draft")


    # current_user_boolean = fields.Boolean()
    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('hr.deduction') or '/'
        values['name'] = seq
        return super(HrDeduction, self.sudo()).create(values)


    def approve(self):
        self.state = 'approved'

    def reject(self):
        self.state = 'refused'
