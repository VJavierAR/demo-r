# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.http import Response 
import logging, ast
import datetime, time
import pytz
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)


class Helpdesk_Controller(http.Controller):
    @http.route('/helpdesk_update/validar_solicitud_de_refacciones/<int:ticket_id>', auth='public')
    def validar_solicitud_de_refacciones(self, ticket_id,**kw):
    	_logger.info('3312: validar_solicitud_de_refacciones()')
    	_logger.info('3312: llego a petición validar_solicitud_de_refacciones(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
    	ticket_id = request.env['helpdesk.ticket'].search([['id', '=', ticket_id]])
    	uido = request.env.context.get('uid')
    	_logger.info('3312: usuiaro sesion' + str(uido))
    	ticket_id.x_studio_field_nO7Xg.action_confirm()
    	ticket_id.optimiza_lineas()
    	_logger.info('3312: regrese de optimiza_lineas(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
    	respuesta = """
    				<div class='row'>
    					<div class='col-sm-12'>
    						<p>
    							Hola, esto fue lo que resulto: """ + str(ticket_id.x_studio_field_nO7Xg.name) + """
    						</p>
    					</div>
    				</div>
    				"""
    	"""
    	view = self.env.ref('studio_customization.helpdesk_ticket_tree_cbc67a2e-f57c-498e-b7db-f39a654cb173')
    	return {
    				#'name': _(mensajeTitulo),
    				'type': 'ir.actions.act_window',
    				'view_type': 'tree',
    				'view_mode': 'tree',
    				'res_model': 'helpdesk.ticket',
    				'views': [(view.id, 'form')],
    				'view_id': view.id,
    				'target': 'current',
    			}
    	"""
    	"""
    	_logger.info('3312: creando mensaje de validación exitosa(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
    	mensajeTitulo = 'Creación y validación de refacción!!!'
    	mensajeCuerpo = 'Se creo y valido la solicitud ' + str(ticket_id.x_studio_field_nO7Xg.name) + ' para el ticket ' + str(ticket_id.id) + '.'
    	wiz = request.env['helpdesk.alerta'].sudo()
    	wiz.create({'mensaje': mensajeCuerpo})
    	view = request.env.ref('helpdesk_update.view_helpdesk_alerta')
    	_logger.info('3312: view: ' + str(view))
    	_logger.info('3312: view: ' + str(view.id))
    	return {
    				'name': _(mensajeTitulo),
    				'type': 'ir.actions.act_window',
    				'view_type': 'form',
    				'view_mode': 'form',
    				'res_model': 'helpdesk.alerta',
    				'views': [(view.id, 'form')],
    				'view_id': view.id,
    				'target': 'new',
    				'res_id': wiz.id,
    				}
    	"""

    	
    	#return Response(status = 200)
    	regresa = ticket_id.alerta()
    	_logger.info('3312: regresa: ' + str(regresa))
    	wizid = regresa.wizid
    	viewid = regresa.viewid
    	_logger.info('3312: wizid: ' + str(wizid))
    	_logger.info('3312: viewid: ' + str(viewid))
    	mensajeTitulo = 'Creación y validación de refacción!!!'
    	return {
    				'name': _(mensajeTitulo),
    				'type': 'ir.actions.act_window',
    				'view_type': 'form',
    				'view_mode': 'form',
    				'res_model': 'helpdesk.alerta',
    				#'views': [(viewid, 'form')],
    				'view_id': viewid,
    				'target': 'new',
    				'res_id': self.id,
    			}
    	



    	#return respuesta


    @http.route('/mesaDeAyuda/tecnicos', auth='public', website=True)
    def vistaTecnicos(self, **kw):
        _logger.info('Helpdesk_Controller.vistaTecnicos()')
        tickets = request.env['helpdesk.ticket'].sudo().search([])
        #return request.render('')
        return  request.render('helpdesk_update.vista_tecnicos', {'tickets': tickets})

# class Requisicion(http.Controller):
# #     @http.route('/requisicion/requisicion/', auth='public')
# #     def index(self, **kw):
# #         return "Hello, world"

#     @http.route('/requisicion/requisicion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('requisicion.listing', {
#             'root': '/requisicion/requisicion',
#             'objects': http.request.env['requisicion.requisicion'].search([]),
#         })

    # @http.route('/requisicion/requisicion/objects/<model("requisicion.requisicion"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('requisicion.object', {
    #         'object': obj
    #     })