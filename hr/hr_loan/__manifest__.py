# -*- coding: utf-8 -*-


###################################################################################
{
    'name': 'HR Loan Management',
    'version': '14.0.1.0.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
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
        'views/hr_loan_seq.xml',
        # 'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        'views/hr_payroll.xml',
        'views/hr_loan_config.xml',
        'views/hr_loan_acc.xml',
        'views/loan_report.xml',
    ],
    'demo': [],
    'images': '',
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
