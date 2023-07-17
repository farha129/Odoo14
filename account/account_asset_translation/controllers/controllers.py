# -*- coding: utf-8 -*-
# from odoo import http


# class AccountAssetTranslation(http.Controller):
#     @http.route('/account_asset_translation/account_asset_translation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_asset_translation/account_asset_translation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_asset_translation.listing', {
#             'root': '/account_asset_translation/account_asset_translation',
#             'objects': http.request.env['account_asset_translation.account_asset_translation'].search([]),
#         })

#     @http.route('/account_asset_translation/account_asset_translation/objects/<model("account_asset_translation.account_asset_translation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_asset_translation.object', {
#             'object': obj
#         })
