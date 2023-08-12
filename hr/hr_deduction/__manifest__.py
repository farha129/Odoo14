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

{
    'name': 'Employee Deduction',
    'version': '14.0.1.0.0',
    'summary': """This module Allows Employee  deduction/penalty""",
    'description': """This module Allows Employee deduction/penalty""",
    'author': "",
    'company': '',
    'category': 'Human Resources',
    'depends': ['hr_payroll_community', 'hr_contract'],
    'data': [
        'views/hr_deduction.xml',
        'views/hr_employee.xml',
        'security/ir.model.access.csv',
        # 'data/cron.xml',
        'data/salary_rule.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
