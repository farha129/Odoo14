# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Anusha P P (<https://www.cybrosys.com>)
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
    'name': 'HR accommodation Management',
    'version': '14.0.1.0.0',
    'summary': 'Manage accommodation Requests',
    'description': """
        Helps you to manage accommodation Requests of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "",
    'company': '',
    'maintainer': '',
     'website': "",
    'depends': [
        'base', 'hr', 'account','hr_payroll_community','hr_employee_custom',
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/hr_accommodation_seq.xml',
        'data/accommodation_cron.xml',
        'views/hr_accommodation.xml',
        # 'views/hr_accommodation_config.xml',
        'views/accommodation_report.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
