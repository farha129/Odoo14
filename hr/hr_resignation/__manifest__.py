# -*- coding: utf-8 -*-
###################################################################################

{
    'name': 'HR Resignation',
    'version': '14.0.1.0.0',
    'summary': 'Mangment the resignation process of the employee',
    'live_test_url': '',
    'author': '',
    'company': '',
    'website': '',
    'depends': ['hr', 'hr_employee_updation', 'mail'],
    'category': 'Generic Modules/Human Resources',
    'maintainer': '',
    'demo': ['data/demo_data.xml'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/resign_employee.xml',
        'views/hr_employee.xml',
        'views/resignation_view.xml',
        'views/approved_resignation.xml',
        'views/resignation_sequence.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': '',
    'license': '',
}

