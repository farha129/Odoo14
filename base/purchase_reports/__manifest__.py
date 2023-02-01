# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'purchase Reports',
    'version': '1.5',
    'category': 'purchase',
    'summary': 'Report describtion  all process for customer',
    'website': '',
    'description': """
Report describtion  all process for Purchase order
""",
    'depends': ['purchase', 'hr','product','stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/by_vendor_wiz.xml',
        'views/report_purchase_templet.xml',
        'views/report_purchase.xml',
        # 'wizard/by_quantity_wiz.xml',
        # 'views/report_purchase_quantity_templet.xml',

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
