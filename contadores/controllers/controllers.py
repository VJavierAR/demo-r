# -*- coding: utf-8 -*-
from odoo import http

# class Contadores(http.Controller):
#     @http.route('/contadores/contadores/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contadores/contadores/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contadores.listing', {
#             'root': '/contadores/contadores',
#             'objects': http.request.env['contadores.contadores'].search([]),
#         })

#     @http.route('/contadores/contadores/objects/<model("contadores.contadores"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contadores.object', {
#             'object': obj
#         })