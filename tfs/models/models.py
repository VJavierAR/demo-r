# -*- coding: utf-8 -*-
from collections import namedtuple
import json
import time
from datetime import date
import datetime
from itertools import groupby
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter
from odoo import exceptions
import logging, ast
_logger = logging.getLogger(__name__)

class tfs(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']    
    _name = 'tfs.tfs'
    _description='tfs'
    active=fields.Boolean(default=True)
    name = fields.Char()
    almacen = fields.Many2one('stock.warehouse', "Almacen",store='True')
    tipo = fields.Selection([('Cian', 'Cian'),('Magenta','Magenta'),('Amarillo','Amarillo'),('Negro','Negro')])
    usuario = fields.Many2one('res.partner')
    inventario = fields.One2many(comodel='stock.quant',related='almacen.lot_stock_id.quant_ids', string="Quants")
    cliente = fields.Many2one('res.partner', store=True,string='Cliente')
    localidad=fields.Many2one('res.partner',store='True',string='Localidad')
    serie=fields.Many2one('stock.production.lot',string='Numero de Serie',store='True',track_visibility='onchange')
    domi=fields.Integer()
    modelo=fields.Char(related='serie.product_id.name',string='Modelo')
    productoNegro=fields.Many2one('product.product',string='Toner Monocromatico')
    productoCian=fields.Many2one('product.product',string='Toner Cian')
    productoMagenta=fields.Many2one('product.product',string='Toner Magenta')
    productoAmarillo=fields.Many2one('product.product',string='Toner Amarillo')

    contadorMono=fields.Many2one('dcas.dcas',string='Anterior Monocromatico',store=True)
    contadorCian=fields.Many2one('dcas.dcas',string='Anterior Cian',store=True)
    contadorMagenta=fields.Many2one('dcas.dcas',string='Anterior Magenta',store=True)
    contadorAmarillo=fields.Many2one('dcas.dcas',string='Anterior Amarillo',store=True)
    
    contadorAnteriorMono=fields.Integer(related='contadorMono.contadorMono',string='Anterior Monocromatico')
    contadorAnteriorCian=fields.Integer(related='contadorCian.contadorColor',string='Anterior Cian')
    contadorAnteriorMagenta=fields.Integer(related='contadorMagenta.contadorColor',string='Anterior Magenta')
    contadorAnteriorAmarillo=fields.Integer(related='contadorAmarillo.contadorColor',string='Anterior Amarillo')

    porcentajeAnteriorNegro=fields.Integer(related='contadorMono.porcentajeNegro',string='Anterior Monocromatico',store=True)
    porcentajeAnteriorCian=fields.Integer(related='contadorCian.porcentajeCian',string='Anterior Cian',store=True)
    porcentajeAnteriorAmarillo=fields.Integer(related='contadorAmarillo.porcentajeAmarillo',string='Anterior Amarillo',store=True)
    porcentajeAnteriorMagenta=fields.Integer(related='contadorMagenta.porcentajeMagenta',string='Anterior Magenta',store=True)
    
    actualMonocromatico=fields.Integer(string='Contador Monocromatico')
    actualColor=fields.Integer(string='Contador Color')
    
    actualporcentajeNegro=fields.Integer(string='Actual Monocromatico')
    actualporcentajeAmarillo=fields.Integer(string='Actual Amarillo')
    actualporcentajeCian=fields.Integer(string='Actual Cian ')
    actualporcentajeMagenta=fields.Integer(string='Actual Magenta')
    
    evidencias=fields.One2many('tfs.evidencia',string='Evidencias',inverse_name='tfs_id')
    estado=fields.Selection([('borrador','Tfs autoriza'),('xValidar','Por Validar'),('Valido','Valido'),('Confirmado','Confirmado'),('Cancelado','Cancelado')],default='borrador', track_visibility='onchange')
    colorBN=fields.Selection(related='serie.product_id.x_studio_color_bn')
    arreglo=fields.Char()
    direccion=fields.Char(widget="html")
    nivelNegro=fields.Float('Nivel Negro')
    nivelAmarillo=fields.Float('Nivel Amarillo')
    nivelMagenta=fields.Float('Nivel Magenta')
    nivelCian=fields.Float('Nivel Cian')
    calle=fields.Char(related='localidad.street')
    NumeroInt=fields.Char(related='localidad.street_number')
    NumeroOut=fields.Char(related='localidad.street_number2')
    cp=fields.Char(related='localidad.zip')
    delegacion=fields.Char(related='localidad.city')
    estadoCi=fields.Char(related='localidad.state_id.name')
    contarFinal=fields.Many2one('dcas.dcas',string='Contador Creado')

    
    def confirm(self):
        for record in self:
            if(len(record.evidencias)==0):
                raise exceptions.UserError("No hay evidencias registradas")                
            if(len(record.inventario)>0):
                if(record.colorBN=="B/N"):
                    In=self.inventario.search([['product_id.name','=',self.productoNegro.name],['location_id','=',self.almacen.lot_stock_id.id]]).sorted(key='quantity',reverse=True)
                    if(len(In)>0 and In[0].quantity>0):
                        self.arreglo=str([In[0].id])
                        if(record.actualporcentajeNegro<60):
                            self.write({'estado':'xValidar'})
                            template_id=self.env['mail.template'].search([('id','=',59)], limit=1)
                            template_id.send_mail(self.id, force_send=True)
                        else:
                            self.write({'estado':'Valido'})
                            self.valida()
                    if(0>self.actualporcentajeNegro):
                       raise exceptions.UserError("Contador Monocromatico debe ser mayor al anterior.")
                    if(len(In)==0 and In[0].quantity==0):
                        self.arreglo=str([])
                        raise exceptions.UserError("No existen cantidades en el almacen para el producto " + self.productoNegro.name)
                else:
                    d=[]
                    i=0
                    suma=0
                    if(record.productoNegro):
                        In=self.inventario.search([['product_id.name','=',self.productoNegro.name],['location_id','=',self.almacen.lot_stock_id.id]]).sorted(key='quantity',reverse=True)
                        if(len(In)>0 and In[0].quantity>0):
                            d.append(In[0].id)
                            i=i+1
                            suma=suma+record.actualporcentajeNegro
                        if(0>self.actualporcentajeNegro):
                           raise exceptions.UserError("Contador Monocromatico debe ser mayor al anterior.")
                        if(len(In)==0 or In[0].quantity==0):
                            raise exceptions.UserError("No existen cantidades en el almacen para el producto " + self.productoNegro.name)
                    if(record.productoCian):
                        In=self.inventario.search([['product_id.name','=',self.productoCian.name],['location_id','=',self.almacen.lot_stock_id.id]]).sorted(key='quantity',reverse=True)
                        if(len(In)>0 and In[0].quantity>0):
                            d.append(In[0].id)
                            i=i+1
                            suma=suma+record.actualporcentajeCian
                        if(0>self.actualporcentajeCian):
                           raise exceptions.UserError("Contador Color debe ser mayor al anterior.")
                        if(len(In)==0 or In[0].quantity==0):
                            raise exceptions.UserError("No existen cantidades en el almacen para el producto " + self.productoCian.name)
                    if(record.productoMagenta):
                        In=self.inventario.search([['product_id.name','=',self.productoMagenta.name],['location_id','=',self.almacen.lot_stock_id.id]]).sorted(key='quantity',reverse=True)
                        if(len(In)>0 and In[0].quantity>0):
                            d.append(In[0].id)
                            i=i+1
                            suma=suma+record.actualporcentajeMagenta
                        if(0>self.actualporcentajeMagenta):
                           raise exceptions.UserError("Contador Color debe ser mayor al anterior.")
                        if(len(In)==0 or In[0].quantity==0):
                            raise exceptions.UserError("No existen cantidades en el almacen para el producto " + self.productoMagenta.name)
                    if(record.productoAmarillo):
                        In=self.inventario.search([['product_id.name','=',self.productoAmarillo.name],['location_id','=',self.almacen.lot_stock_id.id]]).sorted(key='quantity',reverse=True)
                        if(len(In)>0 and In[0].quantity>0):
                            d.append(In[0].id)
                            i=i+1
                            suma=suma+record.actualporcentajeAmarillo
                        if(0>self.actualporcentajeAmarillo):
                           raise exceptions.UserError("Contador Color debe ser mayor al anterior.")
                        if(len(In)==0 or In[0].quantity==0):
                            raise exceptions.UserError("No existen cantidades en el almacen para el producto " + self.productoAmarillo.name)
                    final=suma/i
                    self.arreglo=str(d)
                    if(final<60):
                        self.write({'estado':'xValidar'})
                        template_id=self.env['mail.template'].search([('id','=',59)], limit=1)
                        template_id.send_mail(self.id, force_send=True)                    
                    if(final>60):
                        self.write({'estado':'Valido'})
                        self.valida()
            else:
                    raise exceptions.UserError("No hay inventario en la ubicación selecionada")


    def reglas(self,almacen=[]):
        if(almacen==[]):
            almacenes=self.env['stock.warehouse'].search([['x_studio_mini','=',True]])
        if(almacen!=[]):
            almacenes=self.env['stock.warehouse'].browse(almacen)           
        i=0
        productos=[]
        pickOrigen=[]
        pickDestino=[]
        rule2=[]
        rule=[]
        ticket=None
        for al in almacenes:
            quants=self.env['stock.quant'].search([['location_id','=',al.lot_stock_id.id]])
            reglasabs=self.env['stock.warehouse.orderpoint'].search([['warehouse_id','=',al.id]])
            pickPosibles=self.env['stock.picking'].search(['&',['state','!=','done'],['location_dest_id','=',al.lot_stock_id.id]])
            if(len(pickPosibles)!=0):
                _logger.info("entre 1"+str(al.name))
                tt=pickPosibles.mapped('id')
                rule2=pickPosibles.mapped('reglas.id')
                _logger.info(str(tt))
                _logger.info(str(rule2))
                for re in reglasabs:
                    quant=quants.filtered(lambda x: x.product_id.id == re.product_id.id)
                    _logger.info(str(re.id not in rule2))
                    if(re.id not in rule2):
                        if(len(quant)==0):
                            _logger.info('quant')
                            datos1={'product_id' : re.product_id.id, 'product_uom_qty' : re.product_max_qty,'name':re.product_id.description,'product_uom':re.product_id.uom_id.id,'location_id':41911,'location_dest_id':re.location_id.id}
                            datos2={'product_id' : re.product_id.id, 'product_qty' : re.product_max_qty,'name':re.product_id.description,'product_uom':re.product_id.uom_id.id,'price_unit': 0 }
                            pickOrigen.append(datos1)
                            pickDestino.append(datos2)
                            rule.append(re.id)
                        if(len(quant)>0):
                            _logger.info('quant mayor')
                            _logger.info(str(quant.quantity)+'|||'+str(re.product_min_qty))
                            if(quant.quantity<=re.product_min_qty):
                                _logger.info('ot')
                                _logger.info(str(re.product_max_qty-quant.quantity))
                                if((re.product_max_qty-quant.quantity)>0):
                                    datos1={'product_id' : re.product_id.id, 'product_uom_qty' : re.product_max_qty-quant.quantity,'name':re.product_id.description,'product_uom':re.product_id.uom_id.id,'location_id':41911,'location_dest_id':re.location_id.id}
                                    datos2={'product_id' : re.product_id.id, 'product_qty' : re.product_max_qty-quant.quantity,'name':re.product_id.description,'product_uom':re.product_id.uom_id.id,'price_unit': 0}
                                    pickOrigen.append(datos1)
                                    pickDestino.append(datos2)
                                    rule.append(re.id)
            else:
                _logger.info("entre 2"+str(al.name))
                for re in reglasabs:
                    quant=quants.filtered(lambda x: x.product_id.id == re.product_id.id)
                    if(len(quant)==0):
                        datos1={'product_id' : re.product_id.id, 'product_uom_qty' : re.product_max_qty,'name':re.product_id.description,'product_uom':re.product_id.uom_id.id,'location_id':41911,'location_dest_id':re.location_id.id}
                        datos2={'product_id' : re.product_id.id, 'product_qty' : re.product_max_qty,'name':re.product_id.description,'product_uom':re.product_id.uom_id.id,'price_unit': 0}
                        pickOrigen.append(datos1)
                        pickDestino.append(datos2)
                        rule.append(re.id)
                    if(len(quant)>0):
                        if(quant.quantity<=re.product_min_qty):
                            if((re.product_max_qty-quant.quantity)>0):
                                datos1={'product_id' : re.product_id.id, 'product_uom_qty' : re.product_max_qty-quant.quantity,'name':re.product_id.description,'product_uom':re.product_id.uom_id.id,'location_id':41911,'location_dest_id':re.location_id.id}
                                datos2={'product_id' : re.product_id.id, 'product_qty' : re.product_max_qty-quant.quantity,'name':re.product_id.description,'product_uom':re.product_id.uom_id.id,'price_unit': 0}
                                pickOrigen.append(datos1)
                                pickDestino.append(datos2)
                                rule.append(re.id)
            if(len(pickOrigen)>0):
                c=al.x_studio_field_E0H1Z
                ticket=self.env['helpdesk.ticket'].create({'x_studio_tipo_de_vale':'Resurtido de Almacen','partner_id':c.id,'team_id':8})
                sale = self.env['sale.order'].create({'partner_id' : c.id, 'origin' : "Ticket: " + str(ticket.id), 'x_studio_tipo_de_solicitud' : 'Venta', 'partner_shipping_id' : c.id , 'warehouse_id' : 1 , 'team_id' : 1, 'x_studio_field_bxHgp': ticket.id})
                destino=self.env['stock.picking.type'].search([['name','=','Receipts'],['warehouse_id','=',al.id]])
                ticket.x_studio_field_nO7Xg=sale.id
                compra=self.env['purchase.order'].create({'picking_type_id':destino.id,'partner_id' : 1, 'origin' : "Ticket: " + str(ticket.id), 'warehouse_id' : al.id , 'date_planned': datetime.datetime.now(),'name':'MINI'})
                for ori in pickOrigen:
                    ticket.x_studio_productos=[(4,ori['product_id'])]
                    sl=self.env['sale.order.line'].create({'order_id' : sale.id,'product_id':ori['product_id'],'product_uom_qty':ori['product_uom_qty'], 'price_unit': 0})
                for des in pickDestino:
                    des['date_planned']=datetime.datetime.now()
                    des['order_id']=compra.id
                    self.env['purchase.order.line'].create(des)
                sale.action_confirm()
                sale.picking_ids.write({'mini':True})
                compra.button_confirm()
                datP=self.env['stock.picking'].search([['purchase_id','=',compra.id]])
                datP.write({'reglas':[(6,0,rule)]})
                datP.write({'location_id':8})
                compra.write({'active':False})
                datP.write({'x_studio_ticket':'Ticket de tóner: '+str(ticket.id),'x_studio_ticket_relacionado':ticket.id})
                datP.write({'origin':sale.name,'mini':True})
                datP.action_confirm()
                datP.action_assign()    
        return ticket

    
    def valida(self):
        dat=eval(self.arreglo)
        data={'serie':self.serie.id,'contadorMono':self.actualMonocromatico,'contadorColor':self.actualColor,'fuente':'tfs.tfs'}
        if(dat!=[]):
            quants=self.sudo().env['stock.quant'].browse(dat)
        for q in quants:
            wiz = self.env['quant.action'].create({'quant':q.id,'producto':q.product_id.id,'cantidad':q.quantity,'usuario':self.env.uid,'descripcion':'Cambio mini '+self.name,'cantidadReal':q.quantity-1})
            wiz.confirmar()
            q.sudo().write({'quantity':q.quantity-1})
            q.actualizaRegla()
        if(self.productoNegro):
            data['x_studio_contador_color_anterior']=self.contadorMono.contadorColor
            data['x_studio_contador_mono_anterior_1']=self.contadorAnteriorMono
            data['x_studio_toner_negro']=1
        if(self.productoMagenta):
            data['x_studio_contador_color_anterior']=self.contadorMagenta.contadorColor
            data['x_studio_contador_mono_anterior_1']=self.contadorMagenta.contadorMono
            data['x_studio_toner_magenta']=1
        if(self.productoAmarillo):
            data['x_studio_contador_color_anterior']=self.contadorAmarillo.contadorColor
            data['x_studio_contador_mono_anterior_1']=self.contadorAmarillo.contadorMono
            data['x_studio_toner_amarillo']=1
        if(self.productoCian):           
            data['x_studio_contador_color_anterior']=self.contadorCian.contadorColor
            data['x_studio_contador_mono_anterior_1']=self.contadorCian.contadorMono
            data['x_studio_toner_cian']=1
        c=self.env['dcas.dcas'].create(data)
        self.write({'contarFinal':c.id,'estado':'Confirmado'})


    
    def valida1(self):
        view = self.env.ref('tfs.view_tfs_ticket')
        wiz = self.env['tfs.ticket'].create({'tfs_ids': [(4, self.id)]})
        return {
        'name': _('Alerta'),
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'tfs.ticket',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'target': 'new',
        'res_id': wiz.id,
        'context': self.env.context,
            }
    
    @api.model
    def create(self, vals):
        validacion=False
        if (vals['productoNegro'] or vals['productoAmarillo'] or vals['productoCian'] or vals['productoMagenta']):
            validacion=True
        if(validacion):    
            vals['name'] = self.env['ir.sequence'].next_by_code('tfs')
            result = super(tfs, self).create(vals)
            return result
        if (validacion==False):
            raise exceptions.UserError("No hay ningun toner seleccionado")
    
    def canc(self):
        self.write({'estado':'Cancelado'})

    
    @api.onchange('actualMonocromatico')
    def _onchange_mono(self):
        for record in self:
            if(record.productoNegro):
                _logger.info(str(record.productoNegro.x_studio_rendimiento_toner))
                rendimientoMono=record.actualMonocromatico-record.contadorAnteriorMono
                porcentaje=(100*rendimientoMono)/record.productoNegro.x_studio_rendimiento_toner if record.productoNegro.x_studio_rendimiento_toner>0 else 1
                record['actualporcentajeNegro']=porcentaje
            

    @api.onchange('actualColor')
    def _onchange_color(self):
        if(self.productoCian):
            rendimientoMono=self.actualColor-self.contadorAnteriorCian
            porcentaje=(100*rendimientoMono)/self.productoCian.x_studio_rendimiento_toner if self.productoCian.x_studio_rendimiento_toner>0 else 1
            self.actualporcentajeCian=porcentaje
        if(self.productoAmarillo):
            rendimientoMono=self.actualColor-self.contadorAnteriorAmarillo
            porcentaje=(100*rendimientoMono)/self.productoAmarillo.x_studio_rendimiento_toner if self.productoAmarillo.x_studio_rendimiento_toner>0 else 1
            self.actualporcentajeAmarillo=porcentaje
        if(self.productoMagenta):
            rendimientoMono=self.actualColor-self.contadorAnteriorMagenta
            porcentaje=(100*rendimientoMono)/self.productoMagenta.x_studio_rendimiento_toner if self.productoMagenta.x_studio_rendimiento_toner>0 else 1
            self.actualporcentajeMagenta=porcentaje
    
    
    @api.onchange('serie')
    def ultimoContador(self):
        i=0
        res={}
        for record in self:
            if record.serie:
                if(record.serie.x_studio_mini==False):
                    raise exceptions.UserError("El No. de Serie"+ record.serie.name+"no corresponde a Mini Almacen" )
                if(record.serie.x_studio_localidad_2.id):
                    cliente = record.serie.x_studio_localidad_2.parent_id.id
                    localidad=record.serie.x_studio_localidad_2.id
                    record['cliente'] = cliente
                    record['localidad'] = localidad
                    lo=record.serie.x_studio_localidad_2
                    record['direccion']="<table><tr><td>Calle</td><td>"+str(lo.street)+"</td></tr><tr><td>No.Exterior</td><td>"+str(lo.street_number2)+"</td></tr><tr><td>No. Interior</td><td>"+str(lo.street_number)+"</td></tr><tr><td>Cp</td><td>"+str(lo.zip)+"</td></tr><tr><td>Estado</td><td>"+str(lo.state_id.name)+"</td></tr><tr><td>Delegación</td><td>"+str(lo.city)+"</td></tr></table>"
                    alm=self.env['stock.warehouse'].search([['x_studio_field_E0H1Z','=',localidad]]).lot_stock_id.x_studio_almacn_padre
                    record['almacen'] =alm.id
                    prod=alm.lot_stock_id.quant_ids.mapped('product_id.id')
                if(record.colorBN=="B/N"):
                    data=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.id in prod).mapped('id')
                    if(data==[]):
                        raise exceptions.UserError("Contactese con el administrador la serie sellecionada no esta asociada a un almacen" )
                    if(data!=[]):
                        res['domain'] = {'productoNegro': [('id', 'in', data)]}
                        dc=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_negro','=',1]]).sorted(key='create_date',reverse=True)
                        record['contadorMono'] =dc[0].id if(len(dc)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
                if(record.colorBN=="Color"):
                    negro=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.x_studio_color=='Negro' and x.id in prod).mapped('id')
                    cian=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.x_studio_color=='Cian' and x.id in prod).mapped('id')
                    amarillo=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.x_studio_color=='Amarillo' and x.id in prod).mapped('id')
                    magenta=record.serie.product_id.x_studio_toner_compatible.filtered(lambda x: 'Toner' in x.categ_id.name and x.x_studio_color=='Magenta' and x.id in prod).mapped('id')
                    data=negro+cian+amarillo+magenta
                    if(data==[]):
                        raise exceptions.UserError("Contactese con el administrador la serie sellecionada no esta asociada a un almacen" )
                    if(data!=[]):
                        res['domain'] = {'productoNegro': [('id', 'in', negro)],'productoCian': [('id', 'in', cian)],'productoAmarillo': [('id', 'in', amarillo)],'productoMagenta': [('id', 'in', magenta)]}
                        dc=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_negro','=',1]]).sorted(key='create_date',reverse=True)
                        dc1=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_amarillo','=',1]]).sorted(key='create_date',reverse=True)
                        dc2=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_cian','=',1]]).sorted(key='create_date',reverse=True)
                        dc3=self.env['dcas.dcas'].search([['serie','=',record.serie.id],['fuente','=','tfs.tfs'],['x_studio_toner_magenta','=',1]]).sorted(key='create_date',reverse=True)
                        record['contadorMono'] =dc[0].id if(len(dc)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
                        record['contadorAmarillo'] =dc1[0].id if(len(dc1)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
                        record['contadorCian'] =dc2[0].id if(len(dc2)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
                        record['contadorMagenta'] =dc3[0].id if(len(dc3)>0) else self.env['dcas.dcas'].search([['serie','=',record.serie.id]]).sorted(key='create_date',reverse=True)[0].id
        return res
        
class evidencias(models.Model):
    _name='tfs.evidencia'
    _description='tfs evidencia'
    name=fields.Char(string='Descripcion')
    evidencia=fields.Binary(string='Archivo')
    tfs_id=fields.Many2one('tfs.tfs')

    
class notificacion(models.Model):
    _name='tfs.notificacion.ticket'
    _description='tfs notificacion'
    name=fields.Char(string='Descripcion')
    tickets=fields.Many2many('helpdesk.ticket')

class detonacionMini(models.Model):
    _name='mini.detonacion'
    _description='detonacion Mini Almacen'
    almacen=fields.Many2one('stock.warehouse')
    ticket=fields.Many2one('helpdesk.ticket')
    
    def detona(self):
        t=self.env['tfs.tfs'].reglas(self.almacen.id)
        if(t):
            self.write({'ticket':t.id})
            n=self.env['tfs.notificacion.ticket'].create({'name':'resurtido','tickets':[(6,0,[t.id])]})
            m=self.env['mail.template'].browse(60)
            m.send_mail(n.id, force_send=True)

