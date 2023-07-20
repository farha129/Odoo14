# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018. Engineersoft LLC.
#    See LICENSE file for full copyright and licensing details.
#    License URL : <http://store.engineersoft.net/license.html/>
#
##############################################################################

{
    "name": "ES Report Payment Layout",
    "version": "1.0.3",
    "summary": 'Payment Report Layouts according to Mongolian law',
    'author': 'Engineersoft LLC',
    'support': 'oyunsuren@engineersoft.net',
    'website': 'http://engineersoft.net',
    'license': 'Other proprietary',
    'category': 'Accounting',
    "depends": ['base', 'account', 'account_check_printing', 'hr'],
    "data": [
        "data/paperformat_data.xml",
        "views/report_payment.xml",
        "views/report_payment_cash_receipt.xml",
        "views/report_payment_bank_receipt.xml",
        "views/res_config_settings_views.xml",
        "views/account_payment_views.xml",
    ],
    "auto_install": False,
    "installable": True,
    "images": ['static/description/banner.png'],
}
