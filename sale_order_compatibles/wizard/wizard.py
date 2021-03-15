from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import exceptions, _




class AgregadosOdisminucion(TransientModel):
    _name = 'sale.agregado'
    _description = 'Sale order agregado'
    sale=fields.Many2one('sale.order')
    monto=fields.Float()
    bolsa=fields.Float()
    #tipoSolicitud=fields.Selection(related='sale.x_studio_tipo_de_solicitud')
    periodo=fields.Date()
    #servicio=fields.Many2one(related='sale.x_studio_field_69Boh')


    def agregar(self):
    	if(self.sale.x_studio_tipo_de_solicitud=="Retiro"):
    		self.sale.x_studio_field_69Boh.write({'bolsaCambio':float(self.sale.x_studio_field_69Boh.rentaMensual)-self.bolsa,'montoCambio':float(self.sale.x_studio_field_69Boh.rentaMensual)-self.monto,'fechaAplicacion':self.periodo})
    		self.sale.preparaSolicitud()
    	else:
    		self.sale.x_studio_field_69Boh.write({'bolsaCambio':float(self.sale.x_studio_field_69Boh.rentaMensual)+self.bolsa,'montoCambio':float(self.sale.x_studio_field_69Boh.rentaMensual)+self.monto,'fechaAplicacion':self.periodo})
    		self.sale.preparaSolicitud()
