
{
    'name': "Set Timer for Task",
    'version': '13.0.0.4',
    'author': 'Banibro IT Solutions Pvt Ltd.',
    'company': 'Banibro IT Solutions Pvt Ltd.',
    'website': 'https://banibro.com/erp-software-company-in-chennai/',
    'summary': """Task Timer with Start and Stop""",
    'description': """You may track time sheets for projects automatically with the help of this module.""",
    'category': 'Project',
    'depends': ['base', 'project', 'hr_timesheet'],
    'data': [
        'views/project_task_timer_view.xml',
        'views/project_timer_static.xml',
    ],
    'images': ['static/description/banner.png',
               'static/description/icon.png',],
    'license': 'AGPL-3',
    'email': "support@banibro.com",
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
