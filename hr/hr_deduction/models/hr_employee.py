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

from odoo import models, fields, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    deduction_count = fields.Integer(string="Deduction", compute="get_deduction_count")

    def action_to_open_deduction_records(self):
        domain = [
            ('employee_id', '=', self.id),
        ]
        return {
            'name': _('Employee Deduction'),
            'domain': domain,
            'res_model': 'hr.deduction',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'limit': 80,
        }

    def get_deduction_count(self):
        self.deduction_count = self.env['hr.deduction'].search_count([('employee_id', '=', self.id)])


class HrEmployees(models.Model):
    _inherit = 'hr.employee.public'

    deduction_count = fields.Integer(string="Deduction", compute="get_deduction_count")

    def action_to_open_deduction_records(self):
        domain = [
            ('employee_id', '=', self.id),
        ]
        return {
            'name': _('Employee Deduction'),
            'domain': domain,
            'res_model': 'hr.deduction',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'limit': 80,
        }

    def get_deduction_count(self):
        self.deduction_count = self.env['hr.deduction'].search_count([('employee_id', '=', self.id)])
