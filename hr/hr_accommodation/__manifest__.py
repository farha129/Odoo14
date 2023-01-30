# -*- coding: utf-8 -*-

{
    'name': 'HR accommodation Management',
    'version': '14.0.1.0.0',
    'summary': 'Manage accommodation',
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
