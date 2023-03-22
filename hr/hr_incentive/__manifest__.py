# -*- coding: utf-8 -*-

{
    'name': 'HR Incentive Management',
    'version': '14.0.1.0.0',
    'summary': 'Manage Incentive',
    'description': """
        Helps you to manage Incentive of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "",
    'company': '',
    'maintainer': '',
     'website': "",
    'depends': [
        'base', 'hr', 'account','hr_payroll_community'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_incentive_seq.xml',
        'data/salary_rule_incentive.xml',
        'views/hr_incentive.xml',
        'views/hr_payroll.xml',
        'views/hr_incentive_config.xml',
        'views/hr_incentive_acc.xml',
        'views/incentive_report.xml',
    ],
    'demo': [],
    'images': '',
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
