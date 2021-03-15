# -*- coding: utf-8 -*-
from odoo import http

# class DcasDcas(http.Controller):
#     @http.route('/dcas_dcas/dcas_dcas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dcas_dcas/dcas_dcas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dcas_dcas.listing', {
#             'root': '/dcas_dcas/dcas_dcas',
#             'objects': http.request.env['dcas_dcas.dcas_dcas'].search([]),
#         })

#     @http.route('/dcas_dcas/dcas_dcas/objects/<model("dcas_dcas.dcas_dcas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dcas_dcas.object', {
#             'object': obj
#         })