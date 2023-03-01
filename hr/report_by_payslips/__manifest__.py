# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Report payslips',
    'version': '1.5',
    'category': 'Sale',
    'summary': 'Report describtion  all process for customer',
    'website': 'https://www.odoo.com/page/leaves',
    'description': """
Report describtion  all process for custome
""",
    'depends': ['hr_payroll_community', 'hr'],
    'data': [
  
        'wizard/by_payslip_wiz.xml',
        'views/report_payslip_templet.xml',
        'views/report_payslip.xml',
    ],
    'demo': [

    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
