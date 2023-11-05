# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Request MRPj",
    "summary": "Manufacturing request for stock",
    "version": "15.0.1.3.0",
    "license": "LGPL-3",


    "category": "Warehouse Management",
    "depends": ["stock", "mrp"],
    "data": [
        "security/ir.model.access.csv",
        # "views/stock_request_views.xml",
        # "views/stock_request_order_views.xml",
        # "views/mrp_production_views.xml",
        "views/stock_request.xml",
    ],
    "installable": True,
    "auto_install": True,
}
