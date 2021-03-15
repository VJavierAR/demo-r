# -*- coding: utf-8 -*-
from odoo import http

# class HrDocs(http.Controller):
#     @http.route('/hr_docs/hr_docs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_docs/hr_docs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_docs.listing', {
#             'root': '/hr_docs/hr_docs',
#             'objects': http.request.env['hr_docs.hr_docs'].search([]),
#         })

#     @http.route('/hr_docs/hr_docs/objects/<model("hr_docs.hr_docs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_docs.object', {
#             'object': obj
#         })