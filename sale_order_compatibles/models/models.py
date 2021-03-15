# -*- coding: utf-8 -*-
import base64
from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError,RedirectWarning
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class crm(models.Model):
    _inherit='crm.lead'
    
    
    def crearSolicitud(self):
        view = self.env.ref('studio_customization.sale_order_form_8690a815-6188-42ab-9845-1c18a02ee045')
        return {
                'name': _('Orden'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': self.env.context,
                }

class sale_order_compatibles(models.Model):
	_name = 'sale_order_compatibles'
	_description = 'Detalle modelo temporal'
	saleOrder = fields.Many2one('sale.order')
	equipos = fields.Many2one('product.product', string = 'Equipos')
	cantidad = fields.Selection(selection = [('0', '0'),('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15')],string = 'Cantidad',default=1)
	estado = fields.Selection(selection = [('Nuevo', 'Nuevo'),('Usado', 'Usado')], default = 'Nuevo')
	componentes = fields.One2many('sale_order_compatibles_mini', 'saleOrderMini', string = 'Componentes')
	toner = fields.One2many('sale_order_compatibles_mini_toner', 'saleOrderMini', string = 'Toner')
	accesorios = fields.One2many('sale_order_compatibles_mini_acesorios', 'saleOrderMini', string = 'Accesorios')
	serie=fields.Many2one('stock.production.lot','Serie')
	domin=fields.Char()
	location=fields.Integer()
	tipo=fields.Char()
	precio=fields.Float(default=0.00)
	@api.onchange('equipos')
	def domi(self):
		datos=self.equipos.x_studio_toner_compatible.mapped('id')
		self.domin=str(datos)


class miniModelo(models.Model):
	_name = 'sale_order_compatibles_mini'
	_description = 'Detalle modelo temporal lines'
	idProducto = fields.Char(string = 'id Producto')
	producto = fields.Many2one('product.product')
	cantidad = fields.Integer(string = 'Cantidad')
	saleOrderMini=fields.Many2one('sale_order_compatibles')
	serie=fields.Many2one('stock.production.lot')
	precio=fields.Float(default=0.00)

	@api.onchange('idProducto')
	def domi(self):
		res={}
		if(self.idProducto and self.idProducto!='[]'):
			da=self.env['product.product'].browse(eval(self.idProducto)).filtered(lambda x:x.categ_id.id==6).mapped('id')
			res['domain']={'producto':[['id','in',da]]}
		return res


class miniModeloToner(models.Model):
	_name = 'sale_order_compatibles_mini_toner'
	_description = 'Detalle modelo temporal lines toner'
	idProducto = fields.Char(string = 'id Producto')
	producto = fields.Many2one('product.product')
	cantidad = fields.Integer(string = 'Cantidad')
	saleOrderMini=fields.Many2one('sale_order_compatibles')
	precio=fields.Float(default=0.00)
	tipo=fields.Char()
	serie=fields.Many2one('stock.production.lot')

	@api.onchange('idProducto')
	def domi(self):
		res={}
		if(self.idProducto and self.idProducto!='[]'):
			da=self.env['product.product'].browse(eval(self.idProducto)).filtered(lambda x:x.categ_id.id==5).mapped('id')
			res['domain']={'producto':[['id','in',da]]}
		return res


class miniModeloAccesorio(models.Model):
	_name = 'sale_order_compatibles_mini_acesorios'
	_description = 'Detalle modelo temporal line accesorios'
	idProducto = fields.Char(string = 'id Producto')
	producto = fields.Many2one('product.product')
	cantidad = fields.Integer(string = 'Cantidad')
	saleOrderMini=fields.Many2one('sale_order_compatibles')
	precio=fields.Float(default=0.00)
	tipo=fields.Char()
	serie=fields.Many2one('stock.production.lot')

	@api.onchange('idProducto')
	def domi(self):
		res={}
		if(self.idProducto and self.idProducto!='[]'):
			da=self.env['product.product'].browse(eval(self.idProducto)).filtered(lambda x:x.categ_id.id!=5 and x.categ_id.id!=7).mapped('id')
			res['domain']={'producto':[['id','in',da]]}
		return res

class sale_update(models.Model):
	_inherit = 'sale.order'
	compatiblesLineas = fields.One2many('sale_order_compatibles', 'saleOrder', string = 'nombre temp',copy=True)

	serieRetiro2=fields.Many2one('stock.production.lot','Serie retiro')
	tickets=fields.Many2many('helpdesk.ticket',widget='many2many_tags')
	state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Solicitud Enviada'),
        ('sale', 'Autorizada'),
        ('done', 'Locked'),
        ('assign', 'Asignada'),
        ('distribucion', 'Distribución'),
        ('entregado', 'Entregado'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
	def Reporte(self):
	    fecha=datetime.datetime.now().date()
	    sa=self.search([['x_studio_tipo_de_solicitud','in',('Demostración','Préstamo')],['state','in',('sale','assign')]])
	    pos=sa.filtered(lambda x:x.validity_date>fecha)
	    pos[0].write({'x_studio_arreglo':str(pos.mapped('id'))})
	    template_id2=self.env['mail.template'].search([('id','=',79)], limit=1)
	    mail=template_id2.generate_email(pos[0].id)
	    _logger.info(str(len(pos)))
	    pdf=self.env.ref('stock_picking_mass_action.sale_xlsx').sudo().render_xlsx(data=pos[0],docids=pos[0].id)[0]
	    reporte = base64.encodestring(pdf)
	    at=self.env['ir.attachment'].create({'name':'Reporte Demostración y prestamos','datas':reporte,'datas_fname':'Reporte Demostración y prestamos'})
	    mail['attachment_ids']=[(6,0,[at.id])]
	    self.env['mail.mail'].create(mail).send()
	    #mail.write({'attachment_ids':[(6,0,[at.id])]})
	    #mail.send()


	@api.onchange('partner_id')
	def dominioContactos(self):
		res={}
		for record in self:
			if(record.partner_id.id):
				hijos=self.env['res.partner'].search([['parent_id','=',record.partner_id.id]])
				hijosarr=hijos.mapped('id')
				nietos=self.env['res.partner'].search([['parent_id','in',hijosarr],['type','=','contact']]).mapped('id')
				hijosF=hijos.filtered(lambda x:x.type=='contact').mapped('id')
				final=nietos+hijosF
				res['domain']={'x_studio_field_RnhKr':[('id','in',final)]}
		return res
	@api.onchange('x_studio_direccin_de_entrega')
	def cambioLocalida(self):
		for record in self:
			if(record.x_studio_direccin_de_entrega.id):
				record['partner_shipping_id']=record.x_studio_direccin_de_entrega.id

	@api.onchange('serieRetiro2')
	def serieRetiro(self):
		for record in self:
			if(record.serieRetiro2.id):
				if(record.serieRetiro2.x_studio_localidad_2.id):
					uno=self.env['helpdesk.ticket'].search([['x_studio_equipo_por_nmero_de_serie','=',record.serieRetiro2.id]])
					dos=self.env['helpdesk.ticket'].search([['x_studio_equipo_por_nmero_de_serie_1.serie','=',record.serieRetiro2.id]])
					one=uno.filtered(lambda x:x.stage_id.id not in [3,4,18])
					two=dos.filtered(lambda x:x.stage_id.id not in [3,4,18])
					if(len(one)!=0 or len(two)!=0):
						tickets=one.mapped('id')+two.mapped('id')
						raise UserError(_('Existen los siguientes tickets abiertos :'+str(tickets)))
						#_logger.info(str(len(one))+str(len(two)))
					record['partner_id']=record.serieRetiro2.x_studio_localidad_2.parent_id.id
					record['partner_shipping_id']=record.serieRetiro2.x_studio_localidad_2.id
					record['x_studio_direccin_de_entrega']=record.serieRetiro2.x_studio_localidad_2.id
					record['compatiblesLineas']=[{'serie':record.serieRetiro2.id,'cantidad':1,'tipo':record.x_studio_tipo_de_solicitud,'equipos':record.serieRetiro2.product_id.id}]
					record['x_studio_field_69Boh']=record.serieRetiro2.servicio.id
					record['x_studio_field_LVAj5']=record.serieRetiro2.servicio.contrato.id
	def preparaSolicitudValidacion(self):
		if(len(self.compatiblesLineas)==0):
				raise UserError(_('No hay registros a procesar'))
		if('Renta global' in str(self.x_studio_field_69Boh.serviciosNombre) or 'Renta Global' in str(self.x_studio_field_69Boh.serviciosNombre)):
			wiz = self.env['sale.agregado'].create({'sale':self.id})
			view = self.env.ref('sale_order_compatibles.view_sale_agregados_form')
			return {
				'name': _('Agregado'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'sale.agregado',
				'views': [(view.id, 'form')],
				'view_id': view.id,
				'target': 'new',
				'res_id': wiz.id,
				'context': self.env.context,
					}
		else:
			self.preparaSolicitud()

	def preparaSolicitud(self):
		self.order_line.unlink()
		data=[]
		if(len(self.compatiblesLineas)>0):
			for e in self.compatiblesLineas:
				for ae in range(e.cantidad):
					if(e.cantidad!=0 and e.equipos.id!=False):
						d={'x_studio_field_9nQhR':e.serie.id,'x_studio_estado':e.estado,'x_studio_field_mqSKO':e.equipos.id,'product_id':e.equipos.id,'name':e.equipos.name,'product_uom_qty':1,'product_uom':e.equipos.uom_id.id,'price_unit':(e.precio/e.cantidad),'x_studio_id_relacion':e.id}
						self.order_line=[d]
				for e1 in e.componentes:
					if(e1.cantidad!=0 and e1.producto.id!=False):
						d={'x_studio_field_9nQhR':e1.serie.id,'x_studio_field_mqSKO':e1.producto.id,'product_id':e1.producto.id,'name':e1.producto.name,'product_uom_qty':e1.cantidad,'product_uom':e1.producto.uom_id.id,'price_unit':e1.precio,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
						self.order_line=[d]
				for e2 in e.toner:
					if(e2.cantidad!=0 and e2.producto.id!=False):
						d={'x_studio_field_9nQhR':e2.serie.id,'x_studio_field_mqSKO':e2.producto.id,'product_id':e2.producto.id,'name':e2.producto.name,'product_uom_qty':e2.cantidad,'product_uom':e2.producto.uom_id.id,'price_unit':e2.precio,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
						self.order_line=[d]
				for e3 in e.accesorios:
					if(e3.cantidad!=0 and e3.producto.id!=False):
						d={'x_studio_field_9nQhR':e3.serie.id,'x_studio_field_mqSKO':e3.producto.id,'product_id':e3.producto.id,'name':e3.producto.name,'product_uom_qty':e3.cantidad,'product_uom':e3.producto.uom_id.id,'price_unit':e3.precio,'x_studio_id_relacion':e.id,'x_studio_modelo':e.equipos.name}
						self.order_line=[d]
			self.write({'state':'sent'})
		if(self.x_studio_tipo_de_solicitud=="Venta" or self.x_studio_tipo_de_solicitud=="Venta directa"):
			template_id=self.env['mail.template'].search([('id','=',58)], limit=1)
			template_id.send_mail(self.id, force_send=True)
		if(self.x_studio_tipo_de_solicitud!="Venta" or self.x_studio_tipo_de_solicitud!="Venta directa"):
			if(len(self.compatiblesLineas)>0):
				template_id=self.env['mail.template'].search([('id','=',58)], limit=1)
				template_id.send_mail(self.id, force_send=True)

	def desbloquea(self):
		self.action_cancel()
		self.action_draft()
		picks=self.env['stock.picking'].search([['sale_child','=',self.id]])
		for pi in picks:
			if(pi.origin!=self.name):
				pi.write({'active':False})
			else:
				pi.unlink()

	def componentes(self):
		if(len(self.order_line)>0):
			for s in self.order_line:
				for ss in s.x_studio_field_9nQhR.x_studio_histrico_de_componentes:
					d={'x_studio_field_mqSKO':ss.x_studio_field_gKQ9k.id,'product_id':ss.x_studio_field_gKQ9k.id,'name':ss.x_studio_field_gKQ9k.name,'product_uom_qty':ss.x_studio_cantidad,'product_uom':ss.x_studio_field_gKQ9k.uom_id.id,'price_unit':0.00}
					self.order_line=[d]
	
	def action_confirm(self):
	    if self._get_forbidden_state_confirm() & set(self.mapped('state')):
	        raise UserError(_(
	            'It is not allowed to confirm an order in the following states: %s'
	        ) % (', '.join(self._get_forbidden_state_confirm())))

	    for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
	        order.message_subscribe([order.partner_id.id])
	    self.write({
	        'state': 'sale',
	        #'confirmation_date': fields.Datetime.now()
	    })
	    self._action_confirm()
	    if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
	        self.action_done()
	    self.saleLinesMove()
	    return True

	def saleLinesMove(self):
		picks=self.env['stock.picking'].search(['&',['sale_child','=',self.id],['state','!=','draft']])
		sal=self.order_line.sorted(key='id').mapped('id')
		cliente=self.partner_shipping_id
		for p in picks:
			i=0
			for pi in p.move_ids_without_package.sorted(key='id'):
				pi.write({'sale_line_id':sal[i]})
				if(p.picking_type_id.code=='outgoing' and 'REFACCION' not in p.sale_child.warehouse_id.name and p.partner_id.parent_id.id!=1):
					almacen=self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',cliente.id]])
					if(almacen.id!=False):
						pi.write({'location_dest_id':almacen.lot_stock_id.id})
						self.env['stock.move.line'].search([['move_id','=',pi.id]]).write({'location_dest_id':almacen.lot_stock_id.id})
				i=i+1

	def cambio(self):
		self.action_confirm()
		picks=self.env['stock.picking'].search([['sale_child','=',self.id]])
		almacen=self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',self.partner_shipping_id.id]])
		for pic in picks:
			ppp=pic.copy()
			ppp.write({'retiro':True})
			#ppp.order_line=[(5,0,0)]
			if('PICK' in ppp.name or 'SU' in ppp.name):
				ppp.write({'location_id':almacen.lot_stock_id.id})
				ppp.write({'location_dest_id':pic.picking_type_id.default_location_dest_id.id})
				i=0
				for e in self.compatiblesLineas:
					ppp.move_ids_without_package[i].write({'location_id':almacen.lot_stock_id.id,'location_dest_id':pic.picking_type_id.default_location_dest_id.id,'product_id':e.serie.product_id.id,'x_studio_serie_destino':e.serie.id})
					#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_id':almacen.lot_stock_id.id})
					#ppp.move_ids_without_package[i].write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
					i=i+1
			if('PACK' in ppp.name or 'TRA' in ppp.name):
				ppp.write({'location_id':ppp.picking_type_id.default_location_src_id.id})
				ppp.write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
				#ppp.move_ids_without_package.write({'location_id':ppp.picking_type_id.default_location_src_id.id})
				#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_id':ppp.picking_type_id.default_location_src_id.id})
				#ppp.move_ids_without_package.write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
				i=0
				for e in self.compatiblesLineas:
					ppp.move_ids_without_package[i].write({'location_id':ppp.picking_type_id.default_location_src_id.id,'location_dest_id':ppp.picking_type_id.default_location_dest_id.id,'product_id':e.serie.product_id.id,'x_studio_serie_destino':e.serie.id})
					#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_id':almacen.lot_stock_id.id})
					#ppp.move_ids_without_package[i].write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
					i=i+1
			
			if('OUT' in ppp.name):
				ppp.write({'location_dest_id':ppp.picking_type_id.warehouse_id.lot_stock_id.id})
				#ppp.move_ids_without_package.write({'location_dest_id':ppp.picking_type_id.warehouse_id.lot_stock_id.id})
				#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_dest_id':ppp.picking_type_id.warehouse_id.lot_stock_id.id})
				#ppp.move_ids_without_package.write({'location_id':ppp.picking_type_id.default_location_src_id.id})
				i=0
				for e in self.compatiblesLineas:
					ppp.move_ids_without_package[i].write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id,'product_id':e.serie.product_id.id,'x_studio_serie_destino':e.serie.id})
					#self.env['stock.move.line'].search([['picking_id','=',ppp.id]]).write({'location_id':almacen.lot_stock_id.id})
					#ppp.move_ids_without_package[i].write({'location_dest_id':ppp.picking_type_id.default_location_dest_id.id})
					i=i+1
			#ppp.action_confirm()
			#ppp.action_assign()
	def retiro(self):
		fecha=datetime.datetime.now()-datetime.timedelta(hours=-5)
		self.action_confirm()
		seriesR=self.compatiblesLineas.mapped('serie.id')
		seriesRR=self.env['stock.production.lot'].browse(seriesR)
		for s in seriesRR:
			self.env['cliente.h'].create({'localidad':self.partner_shipping_id.id,'solicitud':self.id,'contrato':self.x_studio_field_LVAj5.id,'servicio':self.x_studio_field_69Boh.id,'origen':self.partner_shipping_id.name,'destino':self.warehouse_id.name,'fecha':fecha,'serie':s.id})
		seriesRR.write({'servicio':False,'x_studio_cliente':1,'x_studio_localidad_2':26662})
		picks=self.env['stock.picking'].search([['sale_child','=',self.id]])
		almacen=self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',self.partner_shipping_id.id]])

		for pic in picks:
		  pic.write({'retiro':True})
		  if('PICK' in pic.name or 'SU' in pic.name):
		    pic.write({'location_id':almacen.lot_stock_id.id})
		    pic.write({'location_dest_id':pic.picking_type_id.default_location_dest_id.id})
		    pic.move_ids_without_package.write({'location_id':almacen.lot_stock_id.id})
		    self.env['stock.move.line'].search([['picking_id','=',pic.id]]).write({'location_id':almacen.lot_stock_id.id})
		    pic.move_ids_without_package.write({'location_dest_id':pic.picking_type_id.default_location_dest_id.id})
		  if('PACK' in pic.name or 'TRA' in pic.name):
		    pic.write({'location_id':pic.picking_type_id.default_location_src_id.id})
		    pic.write({'location_dest_id':pic.picking_type_id.default_location_dest_id.id})
		    pic.move_ids_without_package.write({'location_id':pic.picking_type_id.default_location_src_id.id})
		    self.env['stock.move.line'].search([['picking_id','=',pic.id]]).write({'location_id':pic.picking_type_id.default_location_src_id.id})
		    pic.move_ids_without_package.write({'location_dest_id':pic.picking_type_id.default_location_dest_id.id})
		  if('OUT' in pic.name):
		    pic.write({'location_dest_id':pic.picking_type_id.warehouse_id.lot_stock_id.id})
		    pic.move_ids_without_package.write({'location_dest_id':pic.picking_type_id.warehouse_id.lot_stock_id.id})
		    self.env['stock.move.line'].search([['picking_id','=',pic.id]]).write({'location_dest_id':pic.picking_type_id.warehouse_id.lot_stock_id.id})
		    pic.move_ids_without_package.write({'location_id':pic.picking_type_id.default_location_src_id.id})

	def autoriza(self):
		if(self.x_studio_tipo_de_solicitud in ["Venta","Venta directa","Arrendamiento","Backup","Demostración","Préstamo"]):
			s=self.order_line.mapped('product_id.uom_id.name')
			if('Unidad de servicio' in s):
				ti=self.env['helpdesk.ticket'].create({'x_studio_field_nO7Xg':self.id,'x_studio_tipo_de_vale':'Falla','partner_id':self.partner_id.id,'x_studio_empresas_relacionadas':self.partner_shipping_id.id,'team_id':9,'diagnosticos':[(0,0,{'estadoTicket':'Abierto','comentario':self.note})],'stage_id':89,'name':'Servicio tecnico '})
				self.write({'tickets':[(6,0,[ti.id])]})
			self.action_confirm()
		if(self.x_studio_tipo_de_solicitud == "Cambio"):
			self.cambio()
		if(self.x_studio_tipo_de_solicitud == "Retiro"):
			self.retiro()
	
	def print_quotation(self):
		return self.env.ref('studio_customization.presupuesto_pedido_6e389c86-9862-4c69-af3d-c7021b680bab').with_context(discard_logo_check=True).report_action(self)