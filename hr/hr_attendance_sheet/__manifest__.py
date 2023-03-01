# -*- coding: utf-8 -*-
{
    'name': "HR Mangment Attendance Sheet And Policies",

    'summary': """Managing  Attendance Sheets for Employees
        """,
    'description': """
        Employees Attendance Sheet Management   
    """,
    'author': "",
    'website': "",
    'price': 99,


    'category': 'hr',
    'version': '14.001',
    'images': ['static/description/bannar.jpg'],

    'depends': ['base',
                'hr',
                'hr_holidays',
                'hr_attendance',
                'hr_holidays_attendance',
                'hr_payroll_community',
                ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/change_att_data_view.xml',
        'wizard/payment_wizard.xml',
        'views/hr_attendance_sheet_view.xml',
        'views/hr_attendance_policy_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_holidays_view.xml',
        'views/hr_payroll.xml',
        'views/payslips_report.xml',
        'views/payslips_pdf.xml',
        'wizard/payslips_wizard.xml',
        'data/data.xml',
    ],

    'license': 'OPL-1',
    'demo': [
        'demo/demo.xml',
    ],
}
