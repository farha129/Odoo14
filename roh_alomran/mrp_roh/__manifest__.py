# -*- coding: utf-8 -*-
{
    'name': "Manyfactioring Roh Alomrant",
    'description': """
    """,

    'author': "",
    'website': "",
    'category': 'sale',
    'version': '0.1',
    'depends': ['sale_mrp','sale_roh','mrp_analytic','project'],

    'data': [




        'security/ir.model.access.csv',
        'data/data_mrp.xml',
        'views/mrp_views.xml',
        'views/mrp_timer_static.xml',
        'views/mrp_task_views.xml',
        # 'views/config_mrp.xml',
        'views/overtime_mrp.xml',
        'views/installation_mrp.xml',

    ],
}

