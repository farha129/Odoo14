# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Reports',
    'version': '1.5',
    'category': 'Sale',
    'summary': 'Report describtion  all process for customer',
    'website': 'https://www.odoo.com/page/leaves',
    'description': """
Report describtion  all process for custome
""",
    'depends': ['sale', 'hr','product','stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/by_customer_wiz.xml',
        'views/report_sale_templet.xml',
        'views/report_sale.xml',
        'wizard/by_quantity_wiz.xml',
        'views/report_sale_quantity_templet.xml',

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
