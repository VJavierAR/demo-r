# -*- coding: utf-8 -*-
from odoo import http

# class Contactos(http.Controller):
#     @http.route('/contactos/contactos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contactos/contactos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contactos.listing', {
#             'root': '/contactos/contactos',
#             'objects': http.request.env['contactos.contactos'].search([]),
#         })

#     @http.route('/contactos/contactos/objects/<model("contactos.contactos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contactos.object', {
#             'object': obj
#         })