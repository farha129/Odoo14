# -*- coding: utf-8 -*-
#################################################################################


{
    'name': "Employee Task Performance Report",
    'author': '',
    'category': 'Human Resources',
    'summary': """Employee Performance""",
    'license': '',
    'website': '',
    'description': """
""",
    'version': '1.0',
    'depends': ['base','hr','project','hr_timesheet'],
    'data': [
             'security/ir.model.access.csv',
             'views/employee_view.xml',
             'data/performance_data.xml',
             'data/stage_view.xml',
             'report/employee_report.xml',
             'report/employee_template_report.xml'
             ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
