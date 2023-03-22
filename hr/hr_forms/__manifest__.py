# -*- coding: utf-8 -*-

{
    'name': 'HR forms',
    'version': '14.0.1.0.0',
    'summary': 'Manage Forms',
    'description': """
        Helps you to add forms  of your company.
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
        'views/hr_forms_seq.xml',
        'views/hr_forms.xml',
    ],
    'demo': [],
    'images':'' ,
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
