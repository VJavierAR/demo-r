from odoo import fields, api
from odoo.models import TransientModel
import logging, ast
import datetime, time
import pytz
import base64
import json

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import exceptions, _


listaTipoDeVale = [
                        ('Falla','Falla'),
                        ('Incidencia','Incidencia'),
                        ('Reeincidencia','Reeincidencia'),
                        ('Pregunta','Pregunta'),
                        ('Requerimiento','Requerimiento'),
                        ('Solicitud de refacción','Solicitud de refacción'),
                        ('Conectividad','Conectividad'),
                        ('Reincidencias','Reincidencias'),
                        ('Instalación','Instalación'),
                        ('Mantenimiento Preventivo','Mantenimiento Preventivo'),
                        ('IMAC','IMAC'),
                        ('Proyecto','Proyecto'),
                        ('Retiro de equipo','Retiro de equipo'),
                        ('Cambio','Cambio'),
                        ('Servicio de Software','Servicio de Software'),
                        ('Resurtido de Almacen','Resurtido de Almacen'),
                        ('Supervisión','Supervisión'),
                        ('Demostración','Demostración'),
                        ('Toma de lectura','Toma de lectura')
                    ]



class HelpDeskComentario(TransientModel):
    _name = 'helpdesk.comentario'
    _description = 'HelpDesk Comentario'
    check = fields.Boolean(string='Mostrar en reporte',default=False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    diagnostico_id = fields.One2many('helpdesk.diagnostico', 'ticketRelacion', string = 'Diagnostico', compute='_compute_diagnosticos')
    estado = fields.Char('Estado', compute = "_compute_estadoTicket")
    comentario = fields.Text('Comentario')
    evidencia = fields.Many2many('ir.attachment', string="Evidencias")
    ultimaEvidencia = fields.Boolean(string = '¿Última evidencia?', store=True, default=False)
    editarZona = fields.Boolean(string = 'Editar zona', store=True, default=False)
    zona = fields.Selection([('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')], string = 'Zona', store = True)


    def creaComentario(self):
      if self.ultimaEvidencia and (self.ticket_id.stage_id.id == 18 or self.ticket_id.stage_id.id == 4):
            mensajeTitulo = 'No es posible cambiar a resuelto.'
            mensajeCuerpo = 'Se intento cambiar al estado Resuelto al seleccionar la casilla última evidencia, pero no se logro realizar el cambio ya que el ticket debe de estar en un estado distinto a Cerrado o Cancelado. Estado actual: ' + str(self.ticket_id.stage_id.name)
            wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                        'context': self.env.context,
                    }
      if self.ultimaEvidencia:
          if self.evidencia:
            comentario_generico = 'Se cambio al estado Resuelto, acción realizada por ' + str(self.env.user.name) + '. \n'
            if self.comentario:
                comentario_generico = comentario_generico + 'Comentario: ' + self.comentario
            self.ticket_id.sudo().write({
                'stage_id': 3,
                'resuelto_el': datetime.datetime.now() #pytz.utc.localize(datetime.datetime.now(), is_dst=None).astimezone(pytz.timezone('America/Mexico_City'))
                #, 'team_id': 9
            })

            idDiagnostico = self.env['helpdesk.diagnostico'].sudo().with_env(self.env(user=self.env.user.id)).create({'ticketRelacion': self.ticket_id.id
                                                ,'comentario': comentario_generico
                                                ,'estadoTicket': self.ticket_id.stage_id.name
                                                ,'evidencia': [(6,0,self.evidencia.ids)]
                                                ,'mostrarComentario': self.check,
                                                'creadoPorSistema': False,
                                                'write_uid':  self.env.user.name,
                                                'create_uid': self.env.user.name
                                                })
            #idDiagnostico.write({
            #                    'write_uid': self.env.user.name,
            #                    'create_uid': self.env.user.id
            #                })
            if self.editarZona:
                self.ticket_id.write({'x_studio_zona': self.zona
                                    , 'x_studio_field_6furK': self.zona
                                    })
            #if self.ticket_id.env.user.has_group('studio_customization.grupo_de_tecnicos_fi_6cce8af2-f2d0-4449-b629-906fb2c16636') and self.evidencia:
            #    self.ticket_id.write({'stage_id': 3})
            self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
            mess = 'Diagnostico / Comentario añadido al ticket "' + str(self.ticket_id.id) + '" de forma exitosa. \n\nComentario agregado: ' + str(self.comentario) + '. \n\nGenerado en el estado: ' + self.ticket_id.stage_id.name
            wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mess})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
            return {
                'name': _('Diagnostico / Comentario exitoso !!!'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.alerta',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }
          else:
            raise exceptions.ValidationError('Favor de agregar una o mas evidencias antes de pasar a resuelto el ticket.')
            
      else:
        mensajeNoCambioAResuelto = ''
        if self.ultimaEvidencia:
            mensajeNoCambioAResuelto = '\n\nNota:Se intento cambiar al estado Resuelto al seleccionar la casilla última evidencia, pero no se logro realizar el cambio ya que el ticket debe de estar en el estado Asignado, Atención o Refacción entregada.'
        idDiagnostico = self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.ticket_id.id
                                                ,'comentario': self.comentario
                                                ,'estadoTicket': self.ticket_id.stage_id.name
                                                ,'evidencia': [(6,0,self.evidencia.ids)]
                                                ,'mostrarComentario': self.check,
                                                'creadoPorSistema': False,
                                                'write_uid':  self.env.user.name,
                                                'create_uid': self.env.user.name
                                                })
        #idDiagnostico.write({
        #                        'write_uid': self.env.user.name,
        #                        'create_uid': self.env.user.id
        #                    })
        if self.editarZona:
            self.ticket_id.write({'x_studio_zona': self.zona
                                , 'x_studio_field_6furK': self.zona
                                })
        #if self.ticket_id.env.user.has_group('studio_customization.grupo_de_tecnicos_fi_6cce8af2-f2d0-4449-b629-906fb2c16636') and self.evidencia:
        #    self.ticket_id.write({'stage_id': 3})
        self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
        self.ticket_id.datos_ticket_2()
        mess = 'Diagnostico / Comentario añadido al ticket "' + str(self.ticket_id.id) + '" de forma exitosa. \n\nComentario agregado: ' + str(self.comentario) + '. \n\nGenerado en el estado: ' + self.ticket_id.stage_id.name + mensajeNoCambioAResuelto
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mess})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        return {
            'name': _('Diagnostico / Comentario exitoso !!!'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.alerta',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def _compute_estadoTicket(self):
        self.estado = self.ticket_id.stage_id.name

    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids




class HelpDeskNoValidarConComentario(TransientModel):
    _name = 'helpdesk.comentario.no.validar'
    _description = 'HelpDesk No Validar Con Comentario'
    check = fields.Boolean(string = 'Mostrar en reporte', default = False)
    ticket_id = fields.Many2one("helpdesk.ticket")
    diagnostico_id = fields.One2many('helpdesk.diagnostico', 'ticketRelacion', string = 'Diagnostico', compute = '_compute_diagnosticos')
    estado = fields.Char('Estado', compute = "_compute_estadoTicket")
    comentario = fields.Text('Comentario')
    evidencia = fields.Many2many('ir.attachment', string = "Evidencias")
    productosACambiar = fields.Many2many('product.product', string = "Productos", compute = '_compute_productos')
    solicitud = fields.Many2one('sale.order', strinf = 'solicitud de refacción', compute = '_compute_solicitud')
    activarCompatibilidad = fields.Boolean(string = 'Activar compatibilidad', default = False)
    anadirComentario = fields.Boolean(string = 'Añadir comentario', default = False, store = True)
    serieTexto = fields.Text('Serie', compute = '_compute_serie_text')
    idProductoEnSerie = fields.Integer('id Producto En Serie', compute = '_compute_serie_producto_id')
    listaDeCantidaes = fields.Text('Lista de cantidaes', store = True)

    def _compute_solicitud(self):
        self.solicitud = self.ticket_id.x_studio_field_nO7Xg.id

    def _compute_serie_producto_id(self):
        self.idProductoEnSerie = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].product_id.id

    def _compute_serie_text(self):
        self.serieTexto = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name

    def _compute_productos(self):
        self.productosACambiar = [(6, 0, self.ticket_id.x_studio_productos.ids)]
        #self.write({'productosACambiar': [(6, 0, self.ticket_id.x_studio_productos.ids)]})
        

    @api.onchange('activarCompatibilidad')
    def productos_filtro(self):

        f = []
        f.append(self.idProductoEnSerie)
        
        _logger.info("res f: " + str(f))
        res = {}             
        g = str(f)
        #g = self.ticket_id.x_studio_equipo_por_nmero_de_serie[-1].product_id.id
        #26848
        if self.activarCompatibilidad:
            _logger.info("res g: " + str(g))
            if g !='False':
                list = ast.literal_eval(g)        
                idf = self.ticket_id.team_id.id
                tam = len(list)
                if idf == 8 or idf == 13 :  
                   res['domain']={'productosACambiar':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
                if idf == 9:
                   res['domain']={'productosACambiar':[('categ_id', '=', 7),('x_studio_toner_compatible.id','=',list[0])]}
                if idf != 9 and idf != 8:
                   res['domain']={'productosACambiar':[('categ_id', '!=', 5),('x_studio_toner_compatible.id','=',list[0])]}
                #if idf 55:
                #   _logger.info("Cotizacion xD" + g)
                #   res['domain'] = {'x_studio_productos':[('x_studio_toner_compatible.id', '=', list[0]),('x_studio_toner_compatible.property_stock_inventory.id', '=', 121),('x_studio_toner_compatible.id property_stock_inventory.id', '=', 121)] }
                #   _logger.info("res"+str(res))
        else:
            res['domain']={'productosACambiar':[('categ_id', '=', 7)]}
        _logger.info("res dominio productos wizard: " + str(res))
        return res

    @api.onchange('productosACambiar')
    def cambiaCantidad(self):
        #_logger.info('res cantidad pedida: ' + str(self.productosACambiar[-1].x_studio_cantidad_pedida))
        for record in self:
            lista = []
            self.listaDeCantidaes = ''
            if self.productosACambiar:
                for producto in self.productosACambiar:
                    #_logger.info("res producto.x_studio_cantidad_pedida: " + str(producto.x_studio_cantidad_pedida))
                    #lista.append(producto.x_studio_cantidad_pedida)
                    #_logger.info("res lista: " + str(lista))
                    if self.listaDeCantidaes != '':
                        self.listaDeCantidaes = str(self.listaDeCantidaes) + "," + str(producto.x_studio_cantidad_pedida)
                        #self.sudo().write({'listaDeCantidaes': str(self.listaDeCantidaes) + "," + str(producto.x_studio_cantidad_pedida)})
                    else:
                        self.listaDeCantidaes = str(producto.x_studio_cantidad_pedida)
                        #self.sudo().write({'listaDeCantidaes': str(producto.x_studio_cantidad_pedida)})
            #_logger.info("res lista: " + str(lista))
            #for cantidad in lista:
            #    record.listaDeCantidaes = str(cantidad) + ","
            #_logger.info("res listaDeCantidaes: " + str(record.listaDeCantidaes))

        

    #
    def noValidarConComentario(self):
      #_logger.info("res self.ticket_id.x_studio_field_nO7Xg.id: " + str(self.ticket_id.x_studio_field_nO7Xg.id))
      #_logger.info("res self.ticket_id.x_studio_field_nO7Xg.state: " + str(self.ticket_id.x_studio_field_nO7Xg.state))
      if self.ticket_id.x_studio_field_nO7Xg.id != False and self.ticket_id.x_studio_field_nO7Xg.state != 'sale':
        #_logger.info("res entre: if self.ticket_id.x_studio_field_nO7Xg.id != False and self.ticket_id.x_studio_field_nO7Xg.state == 'sale': ")
        i = 0
        #_logger.info("res listaDeCantidaes ya lista: " + str(self.listaDeCantidaes))
        lista = str(self.listaDeCantidaes).split(",")
        #_logger.info("res lista: " +str(lista))
        #_logger.info("res len(self.productosACambiar): " + str(len(self.productosACambiar)))
        self.env.cr.execute("delete from sale_order_line where order_id = " + str(self.ticket_id.x_studio_field_nO7Xg.id) +";")
        for producto in self.productosACambiar:
            #_logger.info("res lista[i]: " + str(lista[i]))
            #_logger.info("res producto.x_studio_cantidad_pedida: " + str(producto.x_studio_cantidad_pedida))
            datosr = {
                'order_id' : self.ticket_id.x_studio_field_nO7Xg.id,
                'product_id' : producto.id,
                'product_uom_qty' :  float(lista[i]), #producto.x_studio_cantidad_pedida,
                'x_studio_field_9nQhR': self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id
            }
            if (self.ticket_id.team_id.id == 10 or self.ticket_id.team_id.id == 11):
                datosr['route_id'] = 22548
            self.env['sale.order.line'].create(datosr)
            self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(self.ticket_id.x_studio_field_nO7Xg.id) + ";")

            self.sudo().ticket_id.x_studio_productos = [(1, producto.id, {'x_studio_cantidad_pedida': float(lista[i])})]

            i += 1
            #_logger.info("res datosr: " + str(datosr))

        if len(self.productosACambiar.ids) > len(self.ticket_id.x_studio_productos.ids):
            self.sudo().ticket_id.write({'x_studio_productos': [(6, 0, self.productosACambiar.ids)]})
            """
            i = 0
            for producto in self.productosACambiar:
                if int(self.productosACambiar.ids[i]) != self.ticket_id.x_studio_productos.ids[i]:
                    self.sudo().ticket_id.x_studio_productos = [(0, 0, {
                                                                    'order_id': producto.order_id.id,
                                                                    'product_id': producto.product_id.id,
                                                                    'product_uom_qty': float(lista[i]),
                                                                    'x_studio_field_9nQhR': producto.x_studio_field_9nQhR.id,
                                                                    'name': producto.name,
                                                                    'price_unit': producto.price_unit,
                                                                    'product_uom': producto.product_uom,
                                                                    'tax_id': [(6, 0, [1])]
                                                                    }
                                                                )]
                i += 1
            """
      #_logger.info("res ids productos: " + str(self.productosACambiar.ids))
      #_logger.info("res ids productos: " + str(self.productosACambiar[-1].x_studio_cantidad_pedida))
      #self.ticket_id.x_studio_productos = [(6, 0, self.productosACambiar.ids)]
      #self.sudo().ticket_id.write({'x_studio_productos': [(5,0,0)]})
      #self.sudo().ticket_id.write({'x_studio_productos': [(6, 0, self.productosACambiar.ids)]})
      #self.sudo().ticket_id.x_studio_productos = [(6, 0, self.productosACambiar.ids)]
      #self.sudo().ticket_id.write({'x_studio_productos': [(5,0,0),(6, 0, self.productosACambiar.ids)]})
      #self.ticket_id.x_studio_productos = [(5,0,0),(6, 0, self.productosACambiar.ids)]

      if self.anadirComentario:
        #if self.ticket_id.stage_id.name == 'Resuelto' or self.ticket_id.stage_id.name == 'Abierto' or self.ticket_id.stage_id.name == 'Asignado' or self.ticket_id.stage_id.name == 'Atención' and self.ticket_id.estadoCerrado == False:
        self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.ticket_id.id
                                                ,'comentario': self.comentario
                                                ,'estadoTicket': self.ticket_id.stage_id.name
                                                ,'evidencia': [(6,0,self.evidencia.ids)]
                                                ,'mostrarComentario': self.check,
                                                'creadoPorSistema': False
                                                })
        self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
        mess = 'Ticket "' + str(self.ticket_id.id) + '" no validado y Diagnostico / Comentario añadido al ticket "' + str(self.ticket_id.id) + '" de forma exitosa. \n\nComentario agregado: ' + str(self.comentario) + '.'
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mess})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        return {
            'name': _('Ticket cerrado !!!'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.alerta',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def _compute_estadoTicket(self):
        self.estado = self.ticket_id.stage_id.name

    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids




class HelpDeskCerrarConComentario(TransientModel):
    _name = 'helpdesk.comentario.cerrar'
    _description = 'HelpDesk Cerrar Con Comentario'
    check = fields.Boolean(string = 'Mostrar en reporte', default = False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    diagnostico_id = fields.One2many('helpdesk.diagnostico', 'ticketRelacion', string = 'Diagnostico', compute = '_compute_diagnosticos')
    estado = fields.Char('Estado previo a cerrar el ticket', compute = "_compute_estadoTicket")
    comentario = fields.Text('Comentario')
    evidencia = fields.Many2many('ir.attachment', string = "Evidencias")

    def cerrarTicketConComentario(self):
      ultimaEvidenciaTec = []
      if self.ticket_id.x_studio_tipo_de_vale == 'Instalación':
        self.ticket_id.write({
            'instalado_el': datetime.datetime.now()
        })
        self.ticket_id.x_studio_equipo_por_nmero_de_serie.write({
            'instalado_el': datetime.datetime.now()
        })
      if self.ticket_id.diagnosticos:
        ultimaEvidenciaTec = self.ticket_id.diagnosticos[-1].evidencia.ids
        if self.evidencia:
          ultimaEvidenciaTec += self.evidencia.ids
      if self.ticket_id.stage_id.name == 'Distribución' or self.ticket_id.stage_id.name == 'En Ruta' or self.ticket_id.stage_id.name == 'Resuelto' or self.ticket_id.stage_id.name == 'Abierto' or self.ticket_id.stage_id.name == 'Asignado' or self.ticket_id.stage_id.name == 'Atención' or self.ticket_id.stage_id.name == 'Listo para entregar' and self.ticket_id.estadoCerrado == False:
        comentario_generico = 'Se cambio al estado Cerrado, acción realizada por ' + str(self.env.user.name) + '. \n'
        if self.comentario:
            comentario_generico = comentario_generico + 'Comentario: ' + self.comentario
        self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.ticket_id.id
                                                ,'comentario': comentario_generico
                                                #,'estadoTicket': self.ticket_id.stage_id.name
                                                ,'estadoTicket': 'Cerrado'
                                                ,'evidencia': [(6,0,ultimaEvidenciaTec)]
                                                ,'mostrarComentario': self.check,
                                                'creadoPorSistema': False
                                                })
        self.ticket_id.write({
            'stage_id': 18,
            'estadoResueltoPorDocTecnico': True,
            'estadoAtencion': True,
            'cerrado_el': datetime.datetime.now()
        })
        self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
        self.ticket_id.datos_ticket_2()
        mess = 'Ticket "' + str(self.ticket_id.id) + '" cerrado y último Diagnostico / Comentario añadido al ticket "' + str(self.ticket_id.id) + '" de forma exitosa. \n\nComentario agregado: ' + str(self.comentario) + '.'
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mess})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        return {
            'name': _('Ticket cerrado !!!'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.alerta',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def _compute_estadoTicket(self):
        self.estado = self.ticket_id.stage_id.name

    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids





class HelpDeskCancelarConComentario(TransientModel):
    _name = 'helpdesk.comentario.cancelar'
    _description = 'HelpDesk Cancelar Con Comentario'
    check = fields.Boolean(string = 'Mostrar en reporte', default = False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    diagnostico_id = fields.One2many('helpdesk.diagnostico', 'ticketRelacion', string = 'Diagnostico', compute = '_compute_diagnosticos')
    estado = fields.Char('Estado previo a cerrar el ticket', compute = "_compute_estadoTicket")
    comentario = fields.Text('Comentario')
    evidencia = fields.Many2many('ir.attachment', string = "Evidencias")

    def cancelarTicketConComentario(self):
      #if self.ticket_id.stage_id.name == 'Resuelto' or self.ticket_id.stage_id.name == 'Abierto' or self.ticket_id.stage_id.name == 'Asignado' or self.ticket_id.stage_id.name == 'Atención' and self.ticket_id.estadoCerrado == False:
      if self.ticket_id.x_studio_field_nO7Xg:
        self.ticket_id.x_studio_field_nO7Xg.action_cancel()
      self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.ticket_id.id
                                              ,'comentario': self.comentario
                                              ,'estadoTicket': self.ticket_id.stage_id.name
                                              ,'evidencia': [(6,0,self.evidencia.ids)]
                                              ,'mostrarComentario': self.check,
                                              'creadoPorSistema': False
                                              })
      self.ticket_id.write({'stage_id': 4
                          , 'estadoResueltoPorDocTecnico': True
                          , 'estadoAtencion': True
                          })
      self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
      self.ticket_id.datos_ticket_2()
      mess = 'Ticket "' + str(self.ticket_id.id) + '" cancelado y último Diagnostico / Comentario añadido al ticket "' + str(self.ticket_id.id) + '" de forma exitosa. \n\nComentario agregado: ' + str(self.comentario) + '.'
      wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mess})
      view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
      return {
          'name': _('Ticket cancelado !!!'),
          'type': 'ir.actions.act_window',
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'helpdesk.alerta',
          'views': [(view.id, 'form')],
          'view_id': view.id,
          'target': 'new',
          'res_id': wiz.id,
          'context': self.env.context,
      }

    def _compute_estadoTicket(self):
        self.estado = self.ticket_id.stage_id.name

    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids




class HelpDeskDetalleSerie(TransientModel):
    _name = 'helpdesk.detalle.serie'
    _description = 'HelpDesk Detalle Serie'
    ticket_id = fields.Many2one("helpdesk.ticket")
    #lecturas = fields.One2many('dcas.dcas', 'serie', string = 'Lecturas', compute='_compute_lecturas')
    toner = fields.One2many('dcas.dcas', 'serie', string = 'Tóner', compute='_compute_toner')
    historicoDeComponentes = fields.One2many('x_studio_historico_de_componentes', 'x_studio_field_MH4DO', string = 'Historico de Componentes', compute='_compute_historico_de_componentes')
    movimientos = fields.One2many('stock.move.line', 'lot_id', string = 'Movimientos', compute='_compute_movimientos')
    serie = fields.Text(string = "Serie", compute = '_compute_serie_nombre')

    def _compute_serie_nombre(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.serie = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name
    """
    def _compute_lecturas(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.lecturas = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_field_PYss4.ids
    """
    def _compute_toner(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.toner = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_toner_1.ids

    def _compute_historico_de_componentes(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.historicoDeComponentes = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_histrico_de_componentes.ids

    def _compute_movimientos(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.movimientos = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].clientes.ids

    
    html = fields.Text(string = 'Tickets', compute = 'gener_tabla_tickets')

    
    def gener_tabla_tickets(self):
      serie_name = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name #self.mapped('name')[0]
      serie_id = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id #self.mapped('id')[0]
      #_logger.info('serie_name: ' + str(serie_name) + ' serie_id: ' + str(serie_id))
      if serie_id:
        query = 'select "helpdesk_ticket_id" from helpdesk_ticket_stock_production_lot_rel where "stock_production_lot_id" = ' + str(serie_id)
        self.env.cr.execute(query)
        resultadoQuery = self.env.cr.fetchall()
        #_logger.info('resultadoQuery: ' + str(resultadoQuery))
        dominio_tickets_odoo = [('serie', '=', serie_id), ('fuente', '=', 'helpdesk.ticket'), ('x_studio_tickett', '!=', False)]
        tickets_toner = self.env['dcas.dcas'].search(dominio_tickets_odoo) #.x_studio_tickett
        #_logger.info('tickets_toner: ' + str(tickets_toner))
        lista_tickets = []
        for id_ticket in resultadoQuery:
          lista_tickets.append(id_ticket[0])
        for id_ticket in tickets_toner:
          lista_tickets.append(id_ticket.x_studio_tickett)
        #_logger.info('lista_tickets: ' + str(lista_tickets))
        dominio_tickets_odoo = [('id', 'in', lista_tickets), ('active', '=', True)]
        tickets_odoo = self.env['helpdesk.ticket'].search(dominio_tickets_odoo)
        #_logger.info('tickets_odoo: ' + str(tickets_odoo))

        #tickets techra
        #dominio_tickets_techra = [(serie_name, 'in', 'numeroDeSerieTechra')]
        tickets_techra = self.env['helpdesk.ticket.techra'].search([('numeroDeSerieTechra', 'ilike', serie_name)])
        #tickets_techra = tickets_techra.filtered(lambda x: serie_name in x.numeroDeSerieTechra )
        #_logger.info('tickets_techra: ' + str(tickets_techra))

        

        filas = """"""
        for ticket in tickets_techra:
            data_ticke = {}

            contadores = ''
            if ticket.series:
                numero_de_serie = ''
                for serie in ticket.series:
                    numero_de_serie = serie.serie.name
                    if serie.x_studio_color_o_bn == 'Color':
                        contadores = contadores + 'Serie: ' + numero_de_serie + '</br>Equipo B/N o Color: ' + str(serie.x_studio_color_o_bn) + '</br>Contador B/N anterior: ' + str(serie.x_studio_contador_mono_anterior_1) + '</br>Contador B/N actual: ' + str(serie.contadorMono) + '</br>Contador Color anterior: ' + str(serie.x_studio_contador_color_anterior) + '</br>Contador Color actual: ' + str(serie.contadorColor) + '</br>'
                    if serie.x_studio_color_o_bn == 'B/N':
                        contadores = contadores + 'Serie: ' + numero_de_serie + '</br>Equipo B/N o Color: ' + str(serie.x_studio_color_o_bn) + '</br>Contador B/N anterior: ' + str(serie.x_studio_contador_mono_anterior_1) + '</br>Contador B/N actual: ' + str(serie.contadorMono) + '</br>'

            if ticket.diagnosticos:
                diagnosticos_ticket = []
                for registro in ticket.diagnosticos:
                    info = {
                        "create_date": str(registro.fechaDiagnosticoTechra),
                        "estadoTicket": str(registro.estadoTicket),
                        "comentario": str(registro.comentario),
                        "encargado": str(registro.create_uid.name)
                    }
                    diagnosticos_ticket.append(info)
                data_ticke["diagnosticos"] = diagnosticos_ticket

            filas = filas + """
                            \n<tr>
                                <td></td>
                                <td>""" + str(ticket.numTicketDeTechra) + """</td>
                                <td>""" + str(ticket.creado_el) + """</td>
                                <td>""" + str(ticket.numeroDeSerieTechra) + """</td>
                                <td>""" + str(ticket.cliente_text) + """</td>
                                <td>""" + str(ticket.areaDeAtencionTechra) + """</td>
                                <td>""" + str(ticket.zona_de_domicilio) + """</td>
                                <td>""" + str(ticket.localidad_text) + """</td>
                                <td>""" + str(ticket.descripcionDelReporteTechra) + """</td>
                                <td>""" + str(ticket.estadoTicketTechra) + """</td>

                                <td>""" + str(contadores) + """</td>
                                
                                <td>""" + str(ticket.ultima_nota) + """</td>
                                <td>""" + str(ticket.fecha_ultima_nota) + """</td>
                                <td>""" + str(json.dumps(data_ticke)) + """</td>
                              </tr>
                          """
        for ticket in tickets_odoo:
            ultimo_diagnostico_fecha = ''
            data_ticke = {}
            if ticket.diagnosticos:
                diagnosticos_ticket = []
                for registro in ticket.diagnosticos:
                    if not registro.creadoPorSistema and registro.comentario != False:
                        ultimo_diagnostico_fecha = str(registro.create_date)
                    info = {
                        "create_date": str(registro.create_date),
                        "estadoTicket": str(registro.estadoTicket),
                        "comentario": str(registro.comentario),
                        "encargado": str(registro.create_uid.name)
                    }
                    diagnosticos_ticket.append(info)
                data_ticke["diagnosticos"] = diagnosticos_ticket

            if ticket.x_studio_tipo_de_vale != 'Requerimiento':
                filas = filas + """
                                    \n<tr>
                                        <td></td>
                                        <td><a href='https://gnsys-corp.odoo.com/web#id=""" + str(ticket.id) + """&model=helpdesk.ticket&view_type=form&menu_id=406' target='_blank'>""" + str(ticket.id) + """</a></td>
                                        <td>""" + str(ticket.create_date) + """</td>
                                        <td>""" + str(ticket.serie_y_modelo) + """</td>
                                        <td>""" + str(ticket.partner_id.name) + """</td>
                                        <td>""" + str(ticket.team_id.name) + """</td>
                                        <td>""" + str(ticket.x_studio_field_6furK) + """</td>
                                        <td>""" + str(ticket.direccionLocalidadText) + """</td>
                                        <td>""" + str(ticket.primerDiagnosticoUsuario) + """</td>
                                        <td>""" + str(ticket.stage_id.name) + """</td>
                                        <td>""" + str(ticket.contadores_anteriores) + """</td>
                                        <td>""" + str(ticket.x_studio_ultima_nota) + """</td>
                                        <td>""" + str(ultimo_diagnostico_fecha) + """</td>
                                        <td>""" + str(json.dumps(data_ticke)) + """</td>
                                    </tr>
                                """ 
            else:
                contadores = ''
                series_toner = ticket.mapped('x_studio_equipo_por_nmero_de_serie_1')
                #_logger.info('x_studio_equipo_por_nmero_de_serie_1: ' + str(series_toner))
                if series_toner:
                    for serie in series_toner:
                        numero_de_serie = serie.serie.name
                        if serie.x_studio_color_o_bn == 'Color':
                            #contadores = contadores + 'Serie: ' + numero_de_serie + 'Equipo B/N o Color: ' + str(serie.x_studio_color_o_bn) + '</br>Contador B/N anterior: ' + str(serie.x_studio_contador_mono_anterior_1) + '</br>Contador B/N actual: ' + str(serie.contadorMono) + '</br>Contador Color anterior: ' + str(serie.x_studio_contador_color_anterior) + '</br>Contador Color actual: ' + str(serie.contadorColor) + '</br>'
                            contadores = contadores + 'Serie: ' + numero_de_serie + '</br>Equipo B/N o Color: ' + str(serie.x_studio_color_o_bn) + '</br>Contador B/N actual: ' + str(serie.contadorMono) + '</br>Contador Color actual: ' + str(serie.contadorColor) + '</br>'
                        if serie.x_studio_color_o_bn == 'B/N':
                            contadores = contadores + 'Serie: ' + numero_de_serie + '</br>Equipo B/N o Color: ' + str(serie.x_studio_color_o_bn) + '</br>Contador B/N actual: ' + str(serie.contadorMono) + '</br>'


                filas = filas + """
                                    \n<tr>
                                        <td></td>
                                        <td><a href='https://gnsys-corp.odoo.com/web#id=""" + str(ticket.id) + """&model=helpdesk.ticket&view_type=form&menu_id=406' target='_blank'>""" + str(ticket.id) + """</a></td>
                                        <td>""" + str(ticket.create_date) + """</td>
                                        <td>""" + str(ticket.serie_y_modelo) + """</td>
                                        <td>""" + str(ticket.partner_id.name) + """</td>
                                        <td>""" + str(ticket.team_id.name) + """</td>
                                        <td>""" + str(ticket.x_studio_field_6furK) + """</td>
                                        <td>""" + str(ticket.direccionLocalidadText) + """</td>
                                        <td>""" + str(ticket.primerDiagnosticoUsuario) + """</td>
                                        <td>""" + str(ticket.stage_id.name) + """</td>
                                        <td>""" + str(contadores) + """</td>
                                        <td>""" + str(ticket.x_studio_ultima_nota) + """</td>
                                        <td>""" + str(ultimo_diagnostico_fecha) + """</td>
                                        <td>""" + str(json.dumps(data_ticke)) + """</td>
                                    </tr>
                                """ 


        #<th style="width:10%;">Contador B/N</th>
        #<th style="width:10%;">Contador color</th>

        tabla_3 = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .modal-dialog {
                        max-width: 90% !important;
                    }

                </style>
            </head>
            <body>
                <div class='row'>
                    <div class='col-sm-12'>
                        <table id="table_id" class="table table-striped table-bordered" style="width:100%">
                            <thead>
                                <tr>
                                    <th></th>
                                    <th>Ticket</th>
                                    <th>Fecha</th>
                                    <th>No. Serie</th>
                                    <th>Cliente</th>
                                    <th>Área de atención</th>
                                    <th>Zona</th>
                                    <th>Ubicación</th>
                                    <th>Falla</th>
                                    <th>último estatus ticket</th>
                                    <th>Contadores</th>
                                    <th>última Nota</th>
                                    <th>Fecha nota</th>
                                    <th>DatosTicket</th>
                                </tr>
                            </thead>
                            <tbody>
                                """ + filas + """
                            </tbody>
                            <tfoot>
                                <tr>
                                    <th></th>
                                    <th>Ticket</th>
                                    <th>Fecha</th>
                                    <th>No. Serie</th>
                                    <th>Cliente</th>
                                    <th>Área de atención</th>
                                    <th>Zona</th>
                                    <th>Ubicación</th>
                                    <th>Falla</th>
                                    <th>último estatus ticket</th>
                                    <th>Contadores</th>
                                    <th>última Nota</th>
                                    <th>Fecha nota</th>
                                    <th>DatosTicket</th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>

                <script>
                    
                    var table_id = 1
                    var hasOwnProperty = Object.prototype.hasOwnProperty;

                    function isEmpty(obj) {

                        // null and undefined are "empty"
                        if (obj == null) return true;

                        // Assume if it has a length property with a non-zero value
                        // that that property is correct.
                        if (obj.length > 0)    return false;
                        if (obj.length === 0)  return true;

                        // If it isn't an object at this point
                        // it is empty, but it can't be anything *but* empty
                        // Is it empty?  Depends on your application.
                        if (typeof obj !== "object") return true;

                        // Otherwise, does it have any properties of its own?
                        // Note that this doesn't handle
                        // toString and valueOf enumeration bugs in IE < 9
                        for (var key in obj) {
                            if (hasOwnProperty.call(obj, key)) return false;
                        }

                        return true;
                    }

                    function format ( d, id ) {
                        var data_ticket = JSON.parse( d.DatosTicket );
                        //console.log(data_ticket)
                        var diagnosticos = data_ticket.diagnosticos

                        var filas = ""

                        for (i = 0; i < diagnosticos.length; i++) {
                            filas += "<tr> <td>" + diagnosticos[i].create_date + "</td> <td>" + diagnosticos[i].estadoTicket + "</td> <td>" + diagnosticos[i].comentario + "</td> <td>" + diagnosticos[i].encargado + "</td> </tr>"
                        }
                        
                        var tabla = "<table id='table_diagnostico_" + id + "' class='table table-striped table-bordered' style='width:100%'> <thead> <tr> <th>Creado_el</th><th>Estado_de_ticket</th><th>Diagnostico</th><th>Encargado</th> </tr> </thead> <tbody> " + filas + " </tbody> <tfoot> <tr> <th>Creado_el</th><th>Estado_de_ticket</th><th>Diagnostico</th><th>Encargado</th> </tr> </tfoot> </table> "
                        
                        return tabla;
                    }

                    $(document).ready( function () {
                        //console.log("cargabndo todo")
                        var table = $('#table_id').DataTable( {
                            dom: 'Bfrtip',
                            lengthMenu: [
                                [ 10, 25, 50, -1 ],
                                [ '10 filas', '25 filas', '50 filas', 'Todas las filas' ]
                            ],
                            buttons: [
                                'pageLength',
                                'copyHtml5',
                                'excelHtml5',
                                'csvHtml5',
                                'pdfHtml5'
                            ],
                            "language": {
                                "lengthMenu": "Mostrar _MENU_ registros por página",
                                "zeroRecords": "Sin registros - perdón =(",
                                "info": "Página _PAGE_ de _PAGES_",
                                "infoEmpty": "No hay registros disponibles",
                                "infoFiltered": "(Filtrado de _MAX_ registros)",
                                "search": "Buscar",
                                "Previous": "Anterior",
                                "Next": "Siguiente"
                            },
                            "scrollX": true,
                            scrollY: '50vh',
                            scrollCollapse: true,
                            "columnDefs": [
                                {
                                    "targets": [ 13 ],
                                    "visible": false,
                                    "searchable": true
                                }
                            ],
                            "columns": [
                                {
                                    "class":          "details-control",
                                    "orderable":      false,
                                    "data":           null,
                                    "defaultContent": '<i class="fa fa-info-circle" aria-hidden="false"> </ i>'
                                },
                                { "data": "Ticket" },
                                { "data": "Fecha" },
                                { "data": "No. Serie" },
                                { "data": "Cliente" },
                                { "data": "Área de atención" },
                                { "data": "Zona" },
                                { "data": "Ubicación" },
                                { "data": "Falla" },
                                { "data": "último estatus ticket" },
                                { "data": "Contadores" },
                                { "data": "última Nota" },
                                { "data": "Fecha nota" },
                                { "data": "DatosTicket" }
                            ],
                            "order": [[2, 'desc']],
                            colReorder: true
                        } );

                        //console.log("cargo primera tabla de tickets")
                        var detailRows = [];

                        $('#table_id tbody').on( 'click', 'tr td.details-control', function () {
                            var tr = $(this).closest('tr');
                            var row = table.row( tr );
                            var idx = $.inArray( tr.attr('id'), detailRows );
                            
                            var data_ticket_c = JSON.parse( row.data().DatosTicket );
                            //console.log(isEmpty(data_ticket_c))
                            if ( !isEmpty( data_ticket_c ) ) {

                                if ( row.child.isShown() ) {
                                    tr.removeClass( 'details' );
                                    row.child.hide();
                         
                                    // Remove from the 'open' array
                                    detailRows.splice( idx, 1 );

                                } else {
                                    tr.addClass( 'details' );
                                    row.child( format( row.data(), table_id ) ).show();
                                    

                                    //table_diagnostico
                                    //var table_diagnostico = $('table.display').DataTable( {
                                    //var table_diagnostico = row.child.DataTable( {
                                    var table_diagnostico = $('#table_diagnostico_' + table_id).DataTable( {
                                        dom: 'Bfrtip',
                                        lengthMenu: [
                                            [ 10, 25, 50, -1 ],
                                            [ '10 filas', '25 filas', '50 filas', 'Todas las filas' ]
                                        ],
                                        buttons: [
                                            'pageLength',
                                            'copyHtml5',
                                            'excelHtml5',
                                            'csvHtml5',
                                            'pdfHtml5'
                                        ],
                                        "language": {
                                            "lengthMenu": "Mostrar _MENU_ registros por página",
                                            "zeroRecords": "Sin registros - perdón =(",
                                            "info": "Página _PAGE_ de _PAGES_",
                                            "infoEmpty": "No hay registros disponibles",
                                            "infoFiltered": "(Filtrado de _MAX_ registros)",
                                            "search": "Buscar",
                                            "Previous": "Anterior",
                                            "Next": "Siguiente"
                                        },
                                        "columns": [
                                            { "data": "Creado_el" },
                                            { "data": "Estado_de_ticket" },
                                            { "data": "Diagnostico" },
                                            { "data": "Encargado" }
                                        ],
                                        "order": [[0, 'asc']],
                                        colReorder: true
                                    } );


                                    table_id += 1


                                    // Add to the 'open' array
                                    if ( idx === -1 ) {
                                        detailRows.push( tr.attr('id') );
                                    }
                                }
                            } else {
                                alert("No se cuentan con diagnosticos en el ticket seleccionado")
                            }
                        } );
                        

                    } );

                </script>

            </body>
            </html>
        """        

        self.html = tabla_3

class HelpDeskAlerta(TransientModel):
    _name = 'helpdesk.alerta'
    _description = 'HelpDesk Alerta'
    
    ticket_id = fields.Many2one("helpdesk.ticket")
    mensaje = fields.Text('Mensaje')

    
    def cerrar(self):
        return {
                    "type": "set_scrollTop",
                }
    

class HelpDeskAlertaNumeroDeSerie(TransientModel):
    _name = 'helpdesk.alerta.series'
    _description = 'HelpDesk Alerta para series existentes'
    
    ticket_id = fields.Many2one("helpdesk.ticket")
    ticket_id_existente = fields.Integer(string = 'Ticket existente', default = 0)
    mensaje = fields.Text('Mensaje')

    def abrirTicket(self):
        """
        name = 'Ticket'
        res_model = 'helpdesk.ticket' 
        view_name = 'helpdesk.helpdesk_ticket_view_form'
        view = self.env.ref(view_name)
        return {
                'name': _('Ticket'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.ticket',
                #'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'current',
                'res_id': self.ticket_id.id,
                'nodestroy': True
                }
        """
        return {
                "type": "ir.actions.act_url",
                "url": "https://gnsys-corp.odoo.com/web#id= " + str(self.ticket_id_existente) + " &action=400&active_id=9&model=helpdesk.ticket&view_type=form&menu_id=406",
                "target": "new",
                }

    def abrirTicketCreado(self):
        return {
                "type": "ir.actions.act_url",
                "url": "https://gnsys-corp.odoo.com/web#id= " + str(self.ticket_id.id) + " &action=400&active_id=9&model=helpdesk.ticket&view_type=form&menu_id=406",
                "target": "new",
                }

    def action_refresh(self):
        # apply the logic here
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            #'type': 'ir.actions.close_wizard_refresh_view'
            #'type': 'ir.actions.act_view_reload'
        }

class HelpDeskContacto(TransientModel):
    _name = 'helpdesk.contacto'
    _description = 'HelpDesk Contacto'
    ticket_id = fields.Many2one("helpdesk.ticket")
    
    idLocalidadAyuda = fields.Integer(
                                        string = 'idLocalidadAyuda',
                                        compute = '_compute_idLocalidadAyuda'
                                    )

    contactos = fields.Many2one("res.partner", 
        string="Contactos disponibles", 
        domain = "['&',('parent_id.id', '=', idLocalidadAyuda),('type', '=', 'contact')]"
    )

    editarContacto_check = fields.Boolean(
        string = 'Editar contacto',
        default = False
    )

    tipoDeDireccion = fields.Selection([('contact','Contacto')
                                        ,('invoice','Dirección de facturación')
                                        ,('delivery','Dirección de envío')
                                        ,('other','Otra dirección')
                                        ,('private','Dirección Privada')]
                                        , default='contact', string = "Tipo de dirección", store=True)
    subtipo = fields.Selection([('Contacto comercial','Contacto comercial')
                                ,('Contacto sistemas','Contacto sistemas')
                                ,('Contacto para pagos','Contacto parra pagos')
                                ,('Contacto para compras','Contacto para compras')
                                ,('Representante legal','Representante legal')
                                ,('Contacto de localidad','Contacto de localidad')
                                ,('private','Dirección Privada')]
                                , string = "Subtipo", default = 'Contacto de localidad', store=True)
    nombreDelContacto = fields.Char(string='Nombre de contacto')
    titulo = fields.Many2one('res.partner.title', store=True, string='Titulo')
    puestoDeTrabajo = fields.Char(string='Puesto de trabajo')
    correoElectronico = fields.Char(string='Correo electrónico')
    telefono = fields.Char(string='Teléfono')
    movil = fields.Char(string='Móvil')
    notas = fields.Text(string="Notas")

    direccionNombreCalle = fields.Char(string='Nombre de la calle')
    direccionNumeroExterior = fields.Char(string='Número exterior')
    direccionNumeroInterior = fields.Char(string='Número interior')
    direccionColonia = fields.Char(string='Colonia')
    direccionLocalidad = fields.Char(string='Localidad')
    direccionCiudad = fields.Char(string='Ciudad', default='Ciudad de México')
    direccionCodigoPostal = fields.Char(string='Código postal')
    direccionPais = fields.Many2one('res.country', store=True, string='País', default='156')
    direccionEstado = fields.Many2one('res.country.state', store=True, string='Estado', domain="[('country_id', '=?', direccionPais)]")
    
    direccionZona = fields.Selection([
        ('SUR','SUR'),
        ('NORTE','NORTE'),
        ('PONIENTE','PONIENTE'),
        ('ORIENTE','ORIENTE'),
        ('CENTRO','CENTRO'),
        ('DISTRIBUIDOR','DISTRIBUIDOR'),
        ('MONTERREY','MONTERREY'),
        ('CUERNAVACA','CUERNAVACA'),
        ('GUADALAJARA','GUADALAJARA'),
        ('QUERETARO','QUERETARO'),
        ('CANCUN','CANCUN'),
        ('VERACRUZ','VERACRUZ'),
        ('PUEBLA','PUEBLA'),
        ('TOLUCA','TOLUCA'),
        ('LEON','LEON'),
        ('COMODIN','COMODIN'),
        ('VILLAHERMOSA','VILLAHERMOSA'),
        ('MERIDA','MERIDA'),
        ('ALTAMIRA','ALTAMIRA'),
        ('COMODIN','COMODIN'),
        ('DF00','DF00'),
        ('SAN LP','SAN LP'),
        ('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),
        ('Foraneo Norte','Foraneo Norte'),
        ('Foraneo Sur','Foraneo Sur')], string = 'Zona')

    @api.depends('ticket_id')
    def _compute_idLocalidadAyuda(self):
        if self.ticket_id.x_studio_empresas_relacionadas:
            self.idLocalidadAyuda = self.ticket_id.x_studio_empresas_relacionadas.id

    @api.onchange('contactos')
    def actualiza_informacion_contacto(self):
        if self.contactos:
            self.nombreDelContacto = self.contactos.name
            self.correoElectronico = self.contactos.email
            self.telefono = self.contactos.phone
            self.movil = self.contactos.mobile
            self.notas = self.contactos.comment
        else:
            self.nombreDelContacto = ''
            self.correoElectronico = ''
            self.telefono = ''
            self.movil = ''
            self.notas = ''

    
    def agregarContactoALocalidad(self):
        mensajeTitulo = ''
        mensajeCuerpo = ''
        if self.ticket_id.x_studio_empresas_relacionadas.id != 0:
            contactoId = 0
            titulo = ''
            if len(self.titulo) == 0:
                titulo = ''
            else:
                titulo = self.titulo.id
            if self.tipoDeDireccion == "contact" and self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.ticket_id.x_studio_empresas_relacionadas.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                })
                contactoId = contacto.id
            elif self.tipoDeDireccion == "delivery" and self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.ticket_id.x_studio_empresas_relacionadas.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                  
                                                                 , 'street_name' : self.direccionNombreCalle
                                                                 , 'street_number' : self.direccionNumeroExterior
                                                                 , 'street_number2' : self.direccionNumeroInterior
                                                                 , 'l10n_mx_edi_colony' : self.direccionColonia
                                                                 , 'l10n_mx_edi_locality' : self.direccionLocalidad
                                                                 , 'city' : self.direccionCiudad
                                                                 , 'state_id' : self.direccionEstado.id
                                                                 , 'zip' : self.direccionCodigoPostal
                                                                 , 'country_id' : self.direccionPais.id
                                                                  
                                                                 , 'x_studio_field_SqU5B' : self.direccionZona
                                                                })
                contactoId = contacto.id
            #elif self.tipoDeDireccion != "delivery" or self.tipoDeDireccion != "contact":
            elif self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.ticket_id.x_studio_empresas_relacionadas.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                  
                                                                 , 'street_name' : self.direccionNombreCalle
                                                                 , 'street_number' : self.direccionNumeroExterior
                                                                 , 'street_number2' : self.direccionNumeroInterior
                                                                 , 'l10n_mx_edi_colony' : self.direccionColonia
                                                                 , 'l10n_mx_edi_locality' : self.direccionLocalidad
                                                                 , 'city' : self.direccionCiudad
                                                                 , 'state_id' : self.direccionEstado.id
                                                                 , 'zip' : self.direccionCodigoPostal
                                                                 , 'country_id' : self.direccionPais.id
                                                                })
                contactoId = contacto.id
            else:
                mensajeTitulo = "Contacto sin nombre"
                mensajeCuerpo = "No es posible añadir un contacto sin nombre. Favor de indicar el nombre primero."
                #raise exceptions.except_orm(_(errorContactoSinNombre), _(mensajeContactoSinNombre))
            #self.env.cr.commit()
            if contactoId > 0:
                mensajeTitulo = "Contacto agregado." 
                mensajeCuerpo = "Contacto " + str(self.nombreDelContacto) + " agregado a la localidad " + str(self.ticket_id.x_studio_empresas_relacionadas.name)
                self.ticket_id.localidadContacto=contactoId
                #raise exceptions.except_orm(_(errorContactoGenerado), _(mensajeContactoGenerado))
            else:
                mensajeTitulo = "Contacto no agregado"
                mensajeCuerpo = "Contacto no agregado. Favor de verificar la información ingresada."
                #raise exceptions.except_orm(_(errorContactoNoGenerado), _(mensajeContactoNoGenerado))
        else:
            mensajeTitulo = "Contacto sin localidad"
            mensajeCuerpo = "No es posible añadir un contacto sin primero indicar la localidad. Favor de indicar la localidad primero."
            #raise exceptions.except_orm(_(errorContactoSinLocalidad), _(mensajeContactoSinLocalidad))
        
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                'context': self.env.context
        }



    def editarContacto(self):
        if self.contactos:
            vals = {
                'name': self.nombreDelContacto,
                'email': self.correoElectronico,
                'phone': self.telefono,
                'mobile': self.movil,
                'comment': self.notas
            }
            mensajeTitulo = 'Contacto actualizado'
            mensajeCuerpo = 'Se actuaizo el contacto ' + str(self.nombreDelContacto) + ' con los siguientes datos:\n\nNombre: ' + str(self.nombreDelContacto) + '\nCorreo electrónico: ' + str(self.correoElectronico) + '\nTeléfono: ' + str(self.telefono) + '\nMóvil: ' + str(self.movil) + '\nNotas: ' + str(self.notas)
            self.contactos.write(vals)
            self.env['helpdesk.diagnostico'].sudo().with_env(self.env(user=self.env.user.id)).create({
                'ticketRelacion': self.ticket_id.id,
                'comentario': mensajeCuerpo + '\n\nActualización realizada por: ' + str(self.env.user.name),
                'estadoTicket': self.ticket_id.stage_id.name,
                'mostrarComentario': False,
                'creadoPorSistema': True,
                'write_uid':  self.env.user.name,
                'create_uid': self.env.user.name
            })
            wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                    'context': self.env.context
            }
        else:
            raise exceptions.ValidationError('Favor de seleccionar el contacto que será editado.')

    def archivarContacto(self):
        if self.contactos:
            vals = {
                'active': False
            }
            self.contactos.write(vals)
            mensajeTitulo = 'Contacto archivado'
            mensajeCuerpo = 'Se archivo el contacto ' + str(self.nombreDelContacto) + ' que contaba con los siguientes datos:\n\nNombre: ' + str(self.nombreDelContacto) + '\nCorreo electrónico: ' + str(self.correoElectronico) + '\nTeléfono: ' + str(self.telefono) + '\nMóvil: ' + str(self.movil) + '\nNotas: ' + str(self.notas)
            self.env['helpdesk.diagnostico'].sudo().with_env(self.env(user=self.env.user.id)).create({
                'ticketRelacion': self.ticket_id.id,
                'comentario': mensajeCuerpo + '\n\nActualización realizada por: ' + str(self.env.user.name),
                'estadoTicket': self.ticket_id.stage_id.name,
                'mostrarComentario': False,
                'creadoPorSistema': True,
                'write_uid':  self.env.user.name,
                'create_uid': self.env.user.name
            })
            wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                    'context': self.env.context
            }
        else:
            raise exceptions.ValidationError('Favor de seleccionar el contacto que será archivado.')





class helpdesk_contadores(TransientModel):
    _name = 'helpdesk.contadores'
    _description = 'HelpDesk Contadores'
    check = fields.Boolean(string='Solicitar tóner B/N', default=False,)
    ticket_id = fields.Many2one("helpdesk.ticket")
    
    contadorBNMesa = fields.Integer(string='Contador B/N Mesa', compute="_compute_contadorBNMesa")
    contadorBNActual = fields.Integer(string='Contador B/N Actual', default = 0)
    contadorColorMesa = fields.Integer(string='Contador Color Mesa', compute = '_compute_actualizaContadorColorMesa')
    contadorColorActual = fields.Integer(string='Contador Color Actual', default = 0)
    negroProcentaje = fields.Integer(string='% Negro')
    bnColor = fields.Text(string='Color o BN', compute = '_compute_actualizaColor')
    textoInformativo = fields.Text(string = ' ', default = ' ', store = True, compute = '_compute_textoInformativo')

    # 
    @api.depends('contadorBNActual', 'contadorColorActual')
    def _compute_textoInformativo(self):
      for record in self:
        if record.bnColor == "B/N":
          if record.contadorBNActual != 0 or record.contadorBNActual != False:
            record.textoInformativo = """
                                      <div class='alert alert-warning' role='alert'>
                                        <h4 class="alert-heading">Advertencia!!!</h4>

                                        <p>El contador capturado negro será: <strong>""" + str(record.contadorBNActual) + """</strong></p>
                                        <br/>
                                        <p>La diferencia con el contador actual es de: <strong>""" + str(record.contadorBNActual - record.contadorBNMesa) + """</strong></p>

                                        
                                      </div>
                                      
                                    """
          else:
            record.textoInformativo = """ """
        else:
          if (record.contadorBNActual != 0 or record.contadorBNActual != False) and (record.contadorColorActual != 0 or record.contadorColorActual != False):
            record.textoInformativo = """
                                      <div class='alert alert-warning' role='alert'>
                                        <h4 class="alert-heading">Advertencia!!!</h4>

                                        <p>El contador capturado negro será: <strong>""" + str(record.contadorBNActual) + """</strong></p>
                                        <br/>
                                        <p>La diferencia con el contador negro actual es de: <strong>""" + str(record.contadorBNActual - record.contadorBNMesa) + """</strong></p>
                                        <br/>
                                        <p>El contador color capturado será: <strong>""" + str(record.contadorColorActual) + """</strong></p>
                                        <br/>
                                        <p>La diferencia con el contador color actual es de: <strong>""" + str(record.contadorColorActual - record.contadorColorMesa) + """</strong></p>

                                        
                                      </div>
                                      
                                    """

          elif record.contadorBNActual != 0 or record.contadorBNActual != False:
            record.textoInformativo = """
                                      <div class='alert alert-warning' role='alert'>
                                        <h4 class="alert-heading">Advertencia!!!</h4>

                                        <p>El contador capturado negro será: <strong>""" + str(record.contadorBNActual) + """</strong></p>
                                        <br/>
                                        <p>La diferencia con el contador negro actual es de: <strong>""" + str(record.contadorBNActual - record.contadorBNMesa) + """</strong></p>

                                        
                                      </div>
                                      
                                    """
          elif record.contadorColorActual != 0 or record.contadorColorActual != False:
            record.textoInformativo = """
                                      <div class='alert alert-warning' role='alert'>
                                        <h4 class="alert-heading">Advertencia!!!</h4>

                                        <p>El contador color capturado será: <strong>""" + str(record.contadorColorActual) + """</strong></p>
                                        <br/>
                                        <p>La diferencia con el contador color actual es de: <strong>""" + str(record.contadorColorActual - record.contadorColorMesa) + """</strong></p>

                                        
                                      </div>
                                      
                                    """
          else:
            record.textoInformativo = """ """

    
    @api.depends('ticket_id')
    def _compute_contadorBNMesa(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
            dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
            _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

            if ultimo_contador_techra and ultimo_contador_odoo:
                if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                    self.contadorBNMesa = int(ultimo_contador_techra.contadorMono)
                    #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'Color':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_techra.contadorColor)
                    #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'B/N':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono)
                else:
                    self.contadorBNMesa = int(ultimo_contador_odoo.contadorMono)
                    #if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'Color':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_odoo.contadorColor)
                    #if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'B/N':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono)
            elif ultimo_contador_techra and not ultimo_contador_odoo:
                self.contadorBNMesa = int(ultimo_contador_techra.contadorMono)
                #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'Color':
                #        return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_techra.contadorColor)
                #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'B/N':
                #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono)
            elif ultimo_contador_odoo and not ultimo_contador_techra:
                self.contadorBNMesa = int(ultimo_contador_odoo.contadorMono)
                #if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'Color':
                #        return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_odoo.contadorColor)
                #if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'B/N':
                #    return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono)
            #else:
            #    return 'Equipo sin contador'


            """
            fuente = 'stock.production.lot'
            ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
            if ultimoDcaStockProductionLot:
                self.contadorBNMesa = int(ultimoDcaStockProductionLot.contadorMono)
                self.contadorColorMesa = int(ultimoDcaStockProductionLot.contadorColor)
                self.bnColor = ultimoDcaStockProductionLot.x_studio_color_o_bn
            """

    def _compute_actualizaColor(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
            dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
            _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

            if ultimo_contador_techra and ultimo_contador_odoo:
                if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                    self.bnColor = ultimo_contador_techra.x_studio_color_o_bn
                    #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'Color':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_techra.contadorColor)
                    #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'B/N':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono)
                else:
                    self.bnColor = ultimo_contador_odoo.x_studio_color_o_bn
                    #if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'Color':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_odoo.contadorColor)
                    #if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'B/N':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono)
            elif ultimo_contador_techra and not ultimo_contador_odoo:
                self.bnColor = ultimo_contador_techra.x_studio_color_o_bn
                #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'Color':
                #        return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_techra.contadorColor)
                #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'B/N':
                #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono)
            elif ultimo_contador_odoo and not ultimo_contador_techra:
                self.bnColor = ultimo_contador_odoo.x_studio_color_o_bn

            """
            fuente = 'stock.production.lot'
            ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
            if ultimoDcaStockProductionLot:
                self.bnColor = ultimoDcaStockProductionLot.x_studio_color_o_bn
            """

    def _compute_actualizaContadorColorMesa(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
            dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
            _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

            if ultimo_contador_techra and ultimo_contador_odoo:
                if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                    self.contadorColorMesa = int(ultimo_contador_techra.contadorColor)
                    #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'Color':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_techra.contadorColor)
                    #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'B/N':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono)
                else:
                    self.contadorColorMesa = int(ultimo_contador_odoo.contadorColor)
                    #if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'Color':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_odoo.contadorColor)
                    #if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'B/N':
                    #    return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono)
            elif ultimo_contador_techra and not ultimo_contador_odoo:
                self.contadorColorMesa = int(ultimo_contador_techra.contadorColor)
                #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'Color':
                #        return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_techra.contadorColor)
                #if str(ultimo_contador_techra.x_studio_color_o_bn) == 'B/N':
                #    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono)
            elif ultimo_contador_odoo and not ultimo_contador_techra:
                self.contadorColorMesa = int(ultimo_contador_odoo.contadorColor)

            """
            fuente = 'stock.production.lot'
            ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
            if ultimoDcaStockProductionLot:
                self.contadorColorMesa = int(ultimoDcaStockProductionLot.contadorColor)
                self.bnColor = ultimoDcaStockProductionLot.x_studio_color_o_bn
            """
    
    def modificarContadores(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            fuente = 'stock.production.lot'
            #ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)                             
            q = 'stock.production.lot'
            if self.bnColor == 'B/N':
                if int(self.contadorBNActual) >= int(self.contadorBNMesa):
                    negrot = self.contadorBNMesa
                    #colort = c.x_studio_contador_color_mesa
                    rr = self.env['dcas.dcas'].create({
                                                        'serie' : self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id, 
                                                        'contadorMono' : self.contadorBNActual,
                                                        'x_studio_tickett':self.ticket_id.id,
                                                        'x_studio_contador_mono_anterior_1':negrot,
                                                        'fuente': fuente
                                                    })                 
                    self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.ticket_id.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario': 'Contador BN anterior: ' + str(negrot) + '\nContador BN capturado: ' + str(self.contadorBNActual), 'creadoPorSistema': True })
                    
                    self.ticket_id.write({'contadores_anteriores': 'Equipo B/N o Color: ' + str(self.bnColor) + '</br>Contador B/N: ' + str(self.contadorBNActual)
                                        , 'x_studio_contador_bn': int(negrot)
                                        , 'x_studio_contador_bn_a_capturar': int(self.contadorBNActual)
                                        , 'x_studio_contador_color': 0
                                        , 'x_studio_contador_color_a_capturar': 0
                                        })
                    self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
                    self.ticket_id.datos_ticket_2()
                    mensajeTitulo = "Contador capturado!!!"
                    mensajeCuerpo = "Se capturo el contador."
                    wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                    view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                            'context': self.env.context,
                            }
                else:
                    raise exceptions.ValidationError("Contador Monocromatico Menor")                                   
            if self.bnColor != 'B/N':
                if int(self.contadorColorActual) >= int(self.contadorColorMesa) and int(self.contadorBNActual) >= int(self.contadorBNMesa):
                    negrot = self.contadorBNMesa
                    colort = self.contadorColorMesa
                    rr=self.env['dcas.dcas'].create({
                                                        'serie': self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id,
                                                        'contadorMono': self.contadorBNActual,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorColor': self.contadorColorActual,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'fuente': fuente
                                                  })
                    self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.ticket_id.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario': 'Contador BN anterior: ' + str(negrot) + '\nContador BN capturado: ' + str(self.contadorBNActual) + '\nContador color anterior: ' + str(colort) + '\nContador color capturado: ' + str(self.contadorColorActual), 'creadoPorSistema': True})
                    self.ticket_id.write({'contadores_anteriores': 'Equipo B/N o Color: ' + str(self.bnColor) + '</br>Contador B/N: ' + str(self.contadorBNActual) + '</br>Contador Color: ' + str(self.contadorColorActual)
                                        , 'x_studio_contador_bn': int(negrot)
                                        , 'x_studio_contador_bn_a_capturar': int(self.contadorBNActual)
                                        , 'x_studio_contador_color': int(colort)
                                        , 'x_studio_contador_color_a_capturar': int(self.contadorColorActual)
                                        })
                    self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
                    self.ticket_id.datos_ticket_2()
                    mensajeTitulo = "Contador capturado!!!"
                    mensajeCuerpo = "Se capturo el contador."
                    wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                    view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                            'context': self.env.context,
                            }
                else:
                    raise exceptions.ValidationError("Error al capturar contador, el contador capturado debe ser mayor.")






class helpdesk_crearconserie(TransientModel):
    _name = 'helpdesk.crearconserie'
    _description = 'HelpDesk crear ticket desde la serie'

    serie = fields.Many2many('stock.production.lot', string = 'Serie', store = True)
    clienteRelacion = fields.Many2one('res.partner', string = 'Cliente', default=False, store = True)
    localidadRelacion = fields.Many2one('res.partner', string = 'Localidad', store = True)
    contactoInterno = fields.Many2one('res.partner', string = 'Contacto interno', default=False, store = True)

    idContactoInterno = fields.Text(string = 'idContactoInterno', store=True, default=0)
    cliente = fields.Text(string = 'Cliente', store = True)
    idCliente = fields.Text(string = 'idCliente', store=True, default=0)
    localidad = fields.Text(string = 'Localidad', store = True)
    zonaLocalidad = fields.Selection([('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur'),('CHIHUAHUA','CHIHUAHUA')], string = 'Zona', store = True)
    idLocaliidad = fields.Text(string = 'idLocaliidad', store=True, default=0)
    nombreContactoLocalidad = fields.Text(string = 'Contacto de localidad', store = True)
    telefonoContactoLocalidad = fields.Text(string = 'Teléfono de contacto', store = True)
    movilContactoLocalidad = fields.Text(string = 'Movil de contacto', store = True)
    correoContactoLocalidad = fields.Text(string = 'Correo electronico de contacto', store = True)

    direccionCalleNombre = fields.Text(string = 'Calle', store = True)
    direccionNumeroExterior = fields.Text(string = 'Número exterior', store = True)
    direccionNumeroInterior = fields.Text(string = 'Número interior', store = True)
    direccionColonia = fields.Text(string = 'Colonia', store = True)
    direccionLocalidad = fields.Text(string = 'Localidad', store = True)
    direccionCiudad = fields.Text(string = 'Ciudad', store = True)
    direccionEstado = fields.Text(string = 'Estado', store = True)
    direccionCodigoPostal = fields.Text(string = 'Código postal', store = True)

    ticket_id_existente = fields.Integer(string = 'Ticket existente', default = 0, store = True)
    textoTicketExistente = fields.Text(string = ' ', store = True)
    textoClienteMoroso = fields.Text(string = ' ', store = True)
    textoDistribuidor = fields.Text(string = ' ', store = True)
    textoSinServicio = fields.Text(string = ' ', store = True)

    esProspecto = fields.Boolean(string = '¿Es ticket de cliente prospecto?', default = False)
    clienteProspectoText = fields.Text(string = 'Nombre del cliente prospecto')
    comentarioClienteProspecto = fields.Text(string = 'Comentario cliente prospecto')

    estatus = fields.Selection([('No disponible','No disponible'),('Moroso','Moroso'),('Al corriente','Al corriente')], string = 'Estatus', store = True, default = 'No disponible')

    tipoDeReporte = fields.Selection(listaTipoDeVale, string = 'Tipo de reporte', store = True)

    def abrirTicket(self):
        return {
                "type": "ir.actions.act_url",
                "url": "https://gnsys-corp.odoo.com/web#id= " + str(self.ticket_id_existente) + " &action=400&active_id=9&model=helpdesk.ticket&view_type=form&menu_id=406",
                "target": "new",
                }

    @api.onchange('contactoInterno')
    def actualiza_datos_contacto_interno(self):
        if not self.contactoInterno:
            self.nombreContactoLocalidad = ''
            self.telefonoContactoLocalidad = ''
            self.movilContactoLocalidad = ''
            self.correoContactoLocalidad = ''
        else:
            self.nombreContactoLocalidad = self.contactoInterno.name
            self.telefonoContactoLocalidad = self.contactoInterno.phone
            self.movilContactoLocalidad = self.contactoInterno.mobile
            self.correoContactoLocalidad = self.contactoInterno.email

    @api.onchange('clienteRelacion', 'localidadRelacion')
    def actualiza_dominio_en_numeros_de_serie(self):
        #for record in self:
        if self.clienteRelacion.id or self.localidadRelacion.id:
            _logger.info("Entre porque existe: " + str(self.clienteRelacion) + ' loc: ' + str(self.localidadRelacion))
            zero = 0
            dominio = []
            dominioT = []
            
            #for record in self:
            id_cliente = self.clienteRelacion.id
            #id_cliente = record.x_studio_id_cliente
            id_localidad = self.localidadRelacion.id

            self.idCliente = id_cliente
            self.idLocaliidad = id_localidad

            if id_cliente != zero:
              #raise Warning('entro1')
              dominio = ['&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_cliente.id', '=', id_cliente)]
              #dominioT = ['&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]  
              
            else:
              #raise Warning('entro2')
              dominio = [('x_studio_categoria_de_producto_3.name','=','Equipo')]
              #dominioT = [('serie.x_studio_categoria_de_producto_3.name','=','Equipo')]
              
            if id_cliente != zero and id_localidad != zero:
              #raise Warning('entro3')
              dominio = ['&', '&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_cliente.id', '=', id_cliente),('x_studio_localidad_2.id','=',id_localidad)]
              #dominioT = ['&', '&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente),('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id','=',id_localidad)]

            if id_localidad == zero and id_cliente != zero:
              #raise Warning('entro4')
              dominio = ['&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_cliente.id', '=', id_cliente)]
              #dominioT = ['&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_cliente.id', '=', id_cliente)]

            if id_cliente == zero and id_localidad == zero:
              #raise Warning('entro5')
              dominio = [('x_studio_categoria_de_producto_3.name', '=', 'Equipo')]
              #dominio = [('serie.x_studio_categoria_de_producto_3.name', '=', 'Equipo')]
              
            action = {'domain':{'serie': dominio}}
            
            return action
        else:
          _logger.info("Entre porque no existe: " + str(self.clienteRelacion) + ' loc: ' + str(self.localidadRelacion))
          dominio = [('x_studio_categoria_de_producto_3.name', '=', 'Equipo')]
          action = {'domain':{'serie': dominio}}
          return action

    

    @api.onchange('localidadRelacion')
    def cambia_localidad(self):
      if self.localidadRelacion:
        self.cliente = self.clienteRelacion.name
        self.localidad = self.localidadRelacion.name
        self.zonaLocalidad = self.localidadRelacion.x_studio_field_SqU5B

        loc = self.localidadRelacion.id
        #idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_subtipo', '=', 'Contacto de localidad']], order='create_date desc', limit=1)
        idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_ultimo_contacto', '=', True]], order='create_date desc', limit=1)
        if idLoc:
            self.nombreContactoLocalidad = idLoc[0].name
            self.telefonoContactoLocalidad = idLoc[0].phone
            self.movilContactoLocalidad = idLoc[0].mobile
            self.correoContactoLocalidad = idLoc[0].email

        else:
            self.nombreContactoLocalidad = ''
            self.telefonoContactoLocalidad = ''
            self.movilContactoLocalidad = ''
            self.correoContactoLocalidad = ''

        self.direccionCalleNombre = self.localidadRelacion.street_name
        self.direccionNumeroExterior = self.localidadRelacion.street_number
        self.direccionNumeroInterior = self.localidadRelacion.street_number2
        self.direccionColonia = self.localidadRelacion.l10n_mx_edi_colony
        self.direccionLocalidad = self.localidadRelacion.l10n_mx_edi_locality
        self.direccionCiudad = self.localidadRelacion.city
        self.direccionEstado = self.localidadRelacion.state_id.name
        self.direccionCodigoPostal = self.localidadRelacion.zip
        if self.clienteRelacion:
            if self.localidadRelacion.x_studio_distribuidor or self.clienteRelacion.x_studio_distribuidor:
                textoHtml = []
                textoHtml.append("<h2>Es distribuidor, favor de verificar la dirección del cliente para evitar problemas de visitas erroneas.</h2>")
                self.textoDistribuidor = ''.join(textoHtml)
        else:
            if self.localidadRelacion.x_studio_distribuidor:
                textoHtml = []
                textoHtml.append("<h2>Es distribuidor, favor de verificar la dirección del cliente para evitar problemas de visitas erroneas.</h2>")
                self.textoDistribuidor = ''.join(textoHtml)
      else:
        self.serie = ''

        self.cliente = ''
        self.localidad = ''
        self.zonaLocalidad = ''
        self.idLocaliidad = ''

        self.nombreContactoLocalidad = ''
        self.telefonoContactoLocalidad = ''
        self.movilContactoLocalidad = ''
        self.correoContactoLocalidad = ''

        self.direccionCalleNombre = ''
        self.direccionNumeroExterior = ''
        self.direccionNumeroInterior = ''
        self.direccionColonia = ''
        self.direccionLocalidad = ''
        self.direccionCiudad = ''
        self.direccionEstado = ''
        self.direccionCodigoPostal = ''

        self.textoDistribuidor = ''
  
        
    @api.onchange('clienteRelacion')
    def cambia_cliente(self):
        if not self.clienteRelacion:
            self.localidadRelacion = ''
            self.serie = ''

            self.cliente = ''
            self.localidad = ''
            self.zonaLocalidad = ''
            self.idLocaliidad = ''

            self.nombreContactoLocalidad = ''
            self.telefonoContactoLocalidad = ''
            self.movilContactoLocalidad = ''
            self.correoContactoLocalidad = ''

            self.direccionCalleNombre = ''
            self.direccionNumeroExterior = ''
            self.direccionNumeroInterior = ''
            self.direccionColonia = ''
            self.direccionLocalidad = ''
            self.direccionCiudad = ''
            self.direccionEstado = ''
            self.direccionCodigoPostal = ''

            self.estatus = 'No disponible'

            self.textoDistribuidor = ''
        else:
            if self.clienteRelacion.x_studio_moroso:
                self.estatus = 'Moroso'
                textoHtml = []
                #textoHtml.append("<br/>")
                #textoHtml.append("<br/>")
                textoHtml.append("<h2>El cliente es moroso.</h2>")
                self.textoClienteMoroso = ''.join(textoHtml)
            else:
                self.estatus = 'Al corriente'
                self.textoClienteMoroso = ''
            if self.localidadRelacion:
                if self.clienteRelacion.x_studio_distribuidor or self.localidadRelacion.x_studio_distribuidor:
                    textoHtml = []
                    textoHtml.append("<h2>Es distribuidor, favor de verificar la dirección del cliente para evitar problemas de visitas erroneas.</h2>")
                    self.textoDistribuidor = ''.join(textoHtml)
            else:
                if self.clienteRelacion.x_studio_distribuidor:
                    textoHtml = []
                    textoHtml.append("<h2>Es distribuidor, favor de verificar la dirección del cliente para evitar problemas de visitas erroneas.</h2>")
                    self.textoDistribuidor = ''.join(textoHtml)

            #if self.clienteRelacion.name == 'GN SYS CORPORATIVO SA DE CV':


    
    
    @api.onchange('serie')
    def cambia_serie(self):
        if self.serie:
            _my_object = self.env['helpdesk.crearconserie']
            if len(self.serie) > 1:
                mensajeTitulo = "Alerta!!!"
                mensajeCuerpo = "No puede capturar más de una serie."
                raise exceptions.Warning(mensajeCuerpo)
            else:
                query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(self.serie[0].id) + " limit 1;"
                _logger.info("test query: " + str(query))
                #query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!=" + str(ticket.x_studio_id_ticket) + "  and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(self.serie[0].id) + " limit 1;"
                self.env.cr.execute(query)
                informacion = self.env.cr.fetchall()
                _logger.info("test informacion: " + str(informacion))
                
                textoHtmlSinServico = []
                noTieneServicio = False
                mensajeCuerpo = 'No se puede crear un ticket de un equipo sin servicio.\nLos equipos que no tienen servicio son:\n'
                
                for equipo in self.serie:
                  if not equipo.servicio and str(equipo.x_studio_ultma_ubicacin) != "GN SYS CORPORATIVO S.A. DE C.V., TALLER":
                    mensajeCuerpo = mensajeCuerpo + '\nEquipo: ' + str(equipo.product_id.name) + ' Serie: ' + str(equipo.name) + ''
                    noTieneServicio = True
                    self.serie = ''
                    mensajeTitulo = "Alerta!!!"
                    warning = {'title': _(mensajeTitulo)
                            , 'message': _(mensajeCuerpo),
                    }
                    return {'warning': warning}

                  if equipo.x_studio_venta and not equipo.servicio:
                    mensajeCuerpo = 'No se puede crear un ticket de un equipo de tipo venta directa.\nLos equipos en venta directa son:\n'
                    mensajeCuerpo = mensajeCuerpo + '\nEquipo: ' + str(equipo.product_id.name) + ' Serie: ' + str(equipo.name) + ''
                    noTieneServicio = True
                    self.serie = ''
                    mensajeTitulo = "Alerta!!!"
                    warning = {'title': _(mensajeTitulo)
                            , 'message': _(mensajeCuerpo),
                    }
                    return {'warning': warning}
                
                if noTieneServicio:
                  textoHtmlSinServico.append(mensajeCuerpo)
                  self.textoSinServicio = ''.join(textoHtmlSinServico)
                else:
                  self.textoSinServicio = ''

                if len(informacion) > 0:
                  textoHtml2 = """ 
                                <!-- Button trigger modal -->
                                <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModalCenter">
                                  Launch demo modal
                                </button>

                                <!-- Modal -->
                                <div class="modal fade" id="alertaSerieExistenteModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
                                  <div class="modal-dialog modal-dialog-centered" role="document">
                                    <div class="modal-content">
                                      <div class="modal-header">
                                        <h5 class="modal-title" id="exampleModalLongTitle">Aviso!!!</h5>
                                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                          <span aria-hidden="true">&times;</span>
                                        </button>
                                      </div>
                                      <div class="modal-body">
                                        <div class="row">
                                          <div class="col-sm-12">
                                            <h3>Esta serie ya tiene un ticket en proceso.</h3>
                                            <h4>El ticket en proceso es: <b id='numTicketProceso'></b></h4>
                                          </div>
                                        </div>
                                      </div>
                                      <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                                        <button id="btnTicketExistente" type="button" class="btn btn-primary">Abrir ticket existente</button>
                                      </div>
                                    </div>
                                  </div>
                                </div>

                                <script> 
                                  $( document ).ready(function() {
                                    $("field[name='ticket_id_existente']").change(function() {
                                      if (this.val() != 0) {
                                        $("#alertaSerieExistenteModal").modal("show");
                                        $("#numTicketProceso").val(this.val())
                                      } else {
                                        $("#alertaSerieExistenteModal").modal("hide");
                                      }
                                    });
                                    $("#btnTicketExistente").on('click', function() {
                                      var idTicketExistente = $("field[name='ticket_id_existente']").val();
                                      var url = "https://gnsys-corp.odoo.com/web#id= " + idTicketExistente + " &action=400&active_id=9&model=helpdesk.ticket&view_type=form&menu_id=406";
                                      window.open(url);
                                    });
                                  });

                                </script>
                                """
                  textoHtml = []
                  textoHtml.append("<br/>")
                  textoHtml.append("<br/>")
                  textoHtml.append("<h1>Esta serie ya tiene un ticket en proceso.</h1>")
                  textoHtml.append("<br/>")
                  textoHtml.append("<br/>")
                  textoHtml.append("<h3 class='text-center'>El ticket en proceso es: " + str(informacion[0][0]) + "</h3>")
                  if self.clienteRelacion.x_studio_moroso:
                    textoHtmlMoroso = []
                    textoHtmlMoroso.append("<h2>El cliente es moroso.</h2>")
                    self.textoClienteMoroso = ''.join(textoHtmlMoroso)
                  else:
                    self.textoClienteMoroso = ''
                  #textoHtml.append("<script> function test() { alert('Hola') }</script>")
                  self.textoTicketExistente =  ''.join(textoHtml)
                  #self.textoTicketExistente = textoHtml2
                  self.ticket_id_existente = int(informacion[0][0])
                else:
                  self.ticket_id_existente = 0
                  self.textoTicketExistente = ''
                #_logger.info("test serie: " + str(self.serie))
                #_logger.info("test serie: " + str(self.serie[0]))
                #_logger.info("test serie: " + str(self.serie[0].x_studio_move_line))
                #self.serie.reverse()
                #listaMovimientos = []
                #for movimiento in self.serie[0].x_studio_move_line:
                #    listaMovimeintos.append(movimiento.id)
                #listaMovimeintos.reverse()
                #_logger.info("test serie reverse: " + str(self.serie[0].x_studio_move_line))

                #if self.serie[0].x_studio_move_line:
                if self.serie[0].x_studio_localidad_2 and self.serie[0].x_studio_cliente:
                    #moveLineOrdenado = self.serie[0].x_studio_move_line.sorted(key="date", reverse=True)
                    moveLineOrdenado = self.serie[0].x_studio_cliente
                    loc = self.serie[0].x_studio_localidad_2
                    #_logger.info("test dato: " + str(moveLineOrdenado[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id))
                    #_logger.info("test dato: " + str(moveLineOrdenado[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.name))
                    _logger.info("test loc: " + str(loc))
                    _logger.info("test loc.street_name: " + str(loc.street_name))
                    _logger.info("test moveLineOrdenado: " + str(moveLineOrdenado))
                    self.cliente = moveLineOrdenado.name
                    self.idCliente = moveLineOrdenado.id
                    self.clienteRelacion = moveLineOrdenado.id
                    self.localidad = loc.name
                    self.zonaLocalidad = loc.x_studio_field_SqU5B
                    self.idLocaliidad = loc.id
                    self.localidadRelacion = loc.id

                    self.direccionCalleNombre = loc.street_name
                    self.direccionNumeroExterior = loc.street_number
                    self.direccionNumeroInterior = loc.street_number2
                    self.direccionColonia = loc.l10n_mx_edi_colony
                    self.direccionLocalidad = loc.l10n_mx_edi_locality
                    self.direccionCiudad = loc.city
                    self.direccionEstado = loc.state_id.name
                    self.direccionCodigoPostal = loc.zip
                    #self.direccion = self.serie[0].x_studio_move_line[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.

                    _my_object.write({'idCliente' : moveLineOrdenado.id
                                    ,'idLocaliidad': loc.id
                                    })
                    #loc = moveLineOrdenado[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                    
                    
                    #idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_subtipo', '=', 'Contacto de localidad']], order='create_date desc', limit=1)
                    idLoc = self.env['res.partner'].search([['parent_id', '=', loc.id],['x_studio_ultimo_contacto', '=', True]], order='create_date desc', limit=1)
                    
                    if idLoc:
                        self.nombreContactoLocalidad = idLoc[0].name
                        self.telefonoContactoLocalidad = idLoc[0].phone
                        self.movilContactoLocalidad = idLoc[0].mobile
                        self.correoContactoLocalidad = idLoc[0].email

                    else:
                        self.nombreContactoLocalidad = ''
                        self.telefonoContactoLocalidad = ''
                        self.movilContactoLocalidad = ''
                        self.correoContactoLocalidad = ''
                    

                    
                else:
                    mensajeTitulo = "Alerta!!!"
                    mensajeCuerpo = "La serie seleccionada no cuenta con una ubicación y/o cliente."
                    warning = {'title': _(mensajeTitulo)
                            , 'message': _(mensajeCuerpo),
                    }
                    return {'warning': warning}
        else:

            self.ticket_id_existente = 0
            self.textoTicketExistente = ''
            self.textoSinServicio = ''

            self.cliente = ''
            self.localidad = ''
            self.zonaLocalidad = ''
            self.idLocaliidad = ''

            self.clienteRelacion = ''
            self.localidadRelacion = ''

            self.nombreContactoLocalidad = ''
            self.telefonoContactoLocalidad = ''
            self.movilContactoLocalidad = ''
            self.correoContactoLocalidad = ''

            self.direccionCalleNombre = ''
            self.direccionNumeroExterior = ''
            self.direccionNumeroInterior = ''
            self.direccionColonia = ''
            self.direccionLocalidad = ''
            self.direccionCiudad = ''
            self.direccionEstado = ''
            self.direccionCodigoPostal = ''

    def crearTicket(self):
        equipoDeUsuario = 9
        """
        equiposRelacionados = self.env['helpdesk_team_res_users_rel'].search([['res_users_id', '=', self.env.user.id]]).helpdesk_team_id
        _logger.info('3312 equiposRelacionados: ' + str(equiposRelacionados) )
        
        if equiposRelacionados:
            equipoDeUsuario = equiposRelacionados[0]
        """
        #for equipoRelacionado in equiposRelacionados:
        #    if equipoRelacionado == 

        if self.esProspecto:
            ticket = self.env['helpdesk.ticket'].create({
                                                            'stage_id': 89,
                                                            'team_id': equipoDeUsuario,
                                                            'esProspecto': True,
                                                            'clienteProspectoText': self.clienteProspectoText,
                                                            'comentarioClienteProspecto': self.comentarioClienteProspecto,
                                                            'x_studio_tipo_de_vale': self.tipoDeReporte
                                                })
            mensajeTitulo = "Ticket generado!!!"
            #mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' sin número de serie para cliente " + self.cliente + " con localidad " + self.localidad + "\n\n"
            mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' para " + self.clienteProspectoText + ". \nTicket de cliente prospecto\n\n"
            wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'mensaje': mensajeCuerpo})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta_series')
            return {
                      'name': _(mensajeTitulo),
                      'type': 'ir.actions.act_window',
                      'view_type': 'form',
                      'view_mode': 'form',
                      'res_model': 'helpdesk.alerta.series',
                      'views': [(view.id, 'form')],
                      'view_id': view.id,
                      'target': 'new',
                      'res_id': wiz.id,
                      'context': self.env.context,
            }

        if self.serie:
            loc = self.localidadRelacion.id
            idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_ultimo_contacto', '=', True]], order='create_date desc', limit=1)
            messageTemp = ''
            ticket = self.env['helpdesk.ticket'].create({'stage_id': 89 
                                                ,'x_studio_equipo_por_nmero_de_serie': [(6,0,self.serie.ids)]
                                                ,'partner_id': int(self.idCliente)
                                                ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                                                ,'team_id': equipoDeUsuario
                                                ,'x_studio_field_6furK': self.zonaLocalidad,
                                                'x_studio_tipo_de_vale': self.tipoDeReporte,
                                                'localidadContacto': idLoc.id if idLoc else False
                                                })
            if self.zonaLocalidad:
                ticket.write({'partner_id': int(self.idCliente)
                            ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                            ,'team_id': equipoDeUsuario
                            ,'x_studio_field_6furK': self.zonaLocalidad
                            })
            else:
                ticket.write({'partner_id': int(self.idCliente)
                            ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                            ,'team_id': equipoDeUsuario
                            })
            if self.contactoInterno:
                query = "update helpdesk_ticket set \"contactoInterno\" = " + str(self.contactoInterno.id) + " where id = " + str(ticket.id) + ";"
                self.env.cr.execute(query)
                self.env.cr.commit()
            if self.idCliente:
                query = "update helpdesk_ticket set \"partner_id\" = " + str(self.idCliente) + ", \"x_studio_empresas_relacionadas\" =" + str(self.idLocaliidad) + " where id = " + str(ticket.id) + ";"
                self.env.cr.execute(query)
                self.env.cr.commit()
            else:
                mensajeTitulo = 'No existe un cliente asociado a la serie!!!'
                mensajeCuerpo = 'No se logro encontrar el cliente que esta asociado a la serie "' + str(self.serie) + '", favor de notificar al administrador.'
                #wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
                view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                        'context': self.env.context,
                        }
            ticket._compute_datosCliente()
            ticket.actualiza_serie_texto()
            query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!=" + str(ticket.x_studio_id_ticket) + "  and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(ticket.x_studio_equipo_por_nmero_de_serie[0].id) + " limit 1;"
            self.env.cr.execute(query)                        
            informacion = self.env.cr.fetchall()
            wiz = ''
            mensajeTitulo = "Ticket generado!!!"
            if len(informacion) > 0:
                mensajeCuerpo = ('Se creo un ticket que esta en proceso con la serie "' + self.serie.name + '" seleccionada. \n Ticket existente: ' + str(informacion[0][0]) + '\n ')
                wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'ticket_id_existente': informacion[0][0], 'mensaje': mensajeCuerpo})
            else:
                mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' con el número de serie " + self.serie.name + "\n\n"
                wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'mensaje': mensajeCuerpo})
            
            #wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'mensaje': mensajeCuerpo})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta_series')
            return {
                    'name': _(mensajeTitulo),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'helpdesk.alerta.series',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                    }
        elif self.clienteRelacion.id and self.localidadRelacion.id:
          query = "select helpdesk_team_id from helpdesk_team_res_users_rel where res_users_id = " + str(self.env.user.id) + ";"
          self.env.cr.execute(query)
          resultadoQuery = self.env.cr.fetchall()
          puedoCrearSinSerie = False
          for resultado in resultadoQuery:
            if resultado[0] == 9:
                puedoCrearSinSerie = True
                break
          loc = self.localidadRelacion.id
          idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_ultimo_contacto', '=', True]], order='create_date desc', limit=1)
          if puedoCrearSinSerie:
              #equiposRelacionados = self.env['helpdesk_team_res_users_rel'].search([['res_users_id', '=', self.env.user.id]]).helpdesk_team_id
              _logger.info('3312 equiposRelacionados resultadoQuery: ' + str(resultadoQuery) )

              messageTemp = ''
              ticket = self.env['helpdesk.ticket'].create({'stage_id': 89 
                                                  #,'x_studio_equipo_por_nmero_de_serie': [(6,0,self.serie.ids)]
                                                  ,'partner_id': int(self.idCliente)
                                                  ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                                                  ,'team_id': equipoDeUsuario
                                                  ,'x_studio_field_6furK': self.zonaLocalidad,
                                                    'x_studio_tipo_de_vale': self.tipoDeReporte,
                                                    'localidadContacto': idLoc.id if idLoc else False
                                                  })
              ticket.write({'partner_id': int(self.idCliente)
                          ,'x_studio_empresas_relacionadas': int(self.idLocaliidad)
                          ,'team_id': equipoDeUsuario
                          ,'x_studio_field_6furK': self.zonaLocalidad
                          })
              if self.contactoInterno:
                    query = "update helpdesk_ticket set \"contactoInterno\" = " + str(self.contactoInterno.id) + " where id = " + str(ticket.id) + ";"
                    self.env.cr.execute(query)
                    self.env.cr.commit()
              #query = "update helpdesk_ticket set \"partner_id\" = " + str(self.idCliente) + ", \"x_studio_empresas_relacionadas\" =" + str(self.idLocaliidad) + " where id = " + str(ticket.id) + ";"
              #self.env.cr.execute(query)
              #self.env.cr.commit()
              ticket._compute_datosCliente()
              ticket.actualiza_serie_texto()
              #query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!=" + str(ticket.x_studio_id_ticket) + "  and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(ticket.x_studio_equipo_por_nmero_de_serie[0].id) + " limit 1;"            
              #self.env.cr.execute(query)                        
              #informacion = self.env.cr.fetchall()
              wiz = ''
              mensajeTitulo = "Ticket generado!!!"
              #mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' sin número de serie para cliente " + self.cliente + " con localidad " + self.localidad + "\n\n"
              mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' sin número de serie. \n\n"
              wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': ticket.id, 'mensaje': mensajeCuerpo})
              view = self.env.ref('helpdesk_update.view_helpdesk_alerta_series')
              return {
                      'name': _(mensajeTitulo),
                      'type': 'ir.actions.act_window',
                      'view_type': 'form',
                      'view_mode': 'form',
                      'res_model': 'helpdesk.alerta.series',
                      'views': [(view.id, 'form')],
                      'view_id': view.id,
                      'target': 'new',
                      'res_id': wiz.id,
                      'context': self.env.context,
                      }
          else:
            mensajeTitulo = 'No se puede generar ticket sin serie!!!'
            mensajeCuerpo = 'El usuario no es de mesa de Servicio y no tiene los permisos para crear un ticket sin serie.'
            #wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
            wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                    'context': self.env.context,
                    }




class HelpDeskReincidencia(TransientModel):
    _name = 'helpdesk.reincidencia'
    _description = 'HelpDesk Reincidencia'
    
    ticket_id = fields.Many2one("helpdesk.ticket")
    motivo = fields.Text(string = 'Motivo de reincidencia')


    def crearTicket(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
          ticket = self.env['helpdesk.ticket'].create({'stage_id': 89 
                                                      ,'x_studio_equipo_por_nmero_de_serie': [(6,0,self.ticket_id.x_studio_equipo_por_nmero_de_serie.ids)]
                                                      ,'partner_id': int(self.ticket_id.partner_id.id)
                                                      ,'x_studio_empresas_relacionadas': int(self.ticket_id.x_studio_empresas_relacionadas.id)
                                                      ,'team_id': 9
                                                      ,'x_studio_field_6furK': self.ticket_id.x_studio_field_6furK
                                                      ,'esReincidencia': True
                                                      ,'ticketDeReincidencia': "<a href='https://gnsys-corp.odoo.com/web#id=" + str(self.ticket_id.id) + "&action=1137&model=helpdesk.ticket&view_type=form&menu_id=406' target='_blank'>" + str(self.ticket_id.id) + "</a>"
                                                      ,'user_id': self.env.user.id
                                                      ,'contactoInterno' : self.contactoInterno.id
                                                      })
          ticket.write({'partner_id': int(self.ticket_id.partner_id.id)
                      ,'x_studio_empresas_relacionadas': int(self.ticket_id.x_studio_empresas_relacionadas.id)
                      ,'team_id': 9
                      ,'x_studio_field_6furK': self.ticket_id.x_studio_field_6furK
                      ,'esReincidencia': True
                      ,'ticketDeReincidencia': "<a href='https://gnsys-corp.odoo.com/web#id=" + str(self.ticket_id.id) + "&action=1137&model=helpdesk.ticket&view_type=form&menu_id=406' target='_blank'>" + str(self.ticket_id.id) + "</a>"
                      })
          if self.contactoInterno:
            ticket.write({'contactoInterno' : self.contactoInterno.id})
          query = "update helpdesk_ticket set \"partner_id\" = " + str(self.ticket_id.partner_id.id) + ", \"x_studio_empresas_relacionadas\" =" + str(self.ticket_id.x_studio_empresas_relacionadas.id) + ", \"contactoInterno\" = " + str(self.contactoInterno.id) + " where id = " + str(ticket.id) + ";"
          self.env.cr.execute(query)
          self.env.cr.commit()
          ticket._compute_datosCliente()

          self.env['helpdesk.diagnostico'].create({'ticketRelacion': ticket.id
                                                  ,'comentario': 'Ticket creado por reincidencia. Número de ticket relacionado: ' + str(self.ticket_id.id) + ' Motivo: ' + self.motivo
                                                  ,'estadoTicket': ticket.stage_id.name
                                                  #,'evidencia': [(6,0,self.evidencia.ids)]
                                                  ,'mostrarComentario': True,
                                                  'creadoPorSistema': True
                                                  })

          ticket.obten_ulimo_diagnostico_fecha_usuario()
          mensajeTitulo = "Ticket generado!!!"
          mensajeCuerpo = 'Ticket ' + str(ticket.id) + ' generado por reinsidencia'
          wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
          
          view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                  'context': self.env.context,
                  }
        else:
          ticket = self.env['helpdesk.ticket'].create({'stage_id': 89 
                                                        #,'x_studio_equipo_por_nmero_de_serie': [(6,0,self.ticket_id.x_studio_equipo_por_nmero_de_serie.ids)]
                                                        ,'partner_id': int(self.ticket_id.partner_id.id)
                                                        ,'x_studio_empresas_relacionadas': int(self.ticket_id.x_studio_empresas_relacionadas.id)
                                                        ,'team_id': 9
                                                        ,'x_studio_field_6furK': self.ticket_id.x_studio_field_6furK
                                                        ,'esReincidencia': True
                                                        ,'ticketDeReincidencia': "<a href='https://gnsys-corp.odoo.com/web#id=" + str(self.ticket_id.id) + "&action=1137&model=helpdesk.ticket&view_type=form&menu_id=406' target='_blank'>" + str(self.ticket_id.id) + "</a>"
                                                        ,'user_id': self.env.user.id
                                                        ,'contactoInterno' : self.contactoInterno.id
                                                        })
          ticket.write({'partner_id': int(self.ticket_id.partner_id.id)
                      ,'x_studio_empresas_relacionadas': int(self.ticket_id.x_studio_empresas_relacionadas.id)
                      ,'team_id': 9
                      ,'x_studio_field_6furK': self.ticket_id.x_studio_field_6furK
                      ,'esReincidencia': True
                      ,'ticketDeReincidencia': "<a href='https://gnsys-corp.odoo.com/web#id=" + str(self.ticket_id.id) + "&action=1137&model=helpdesk.ticket&view_type=form&menu_id=406' target='_blank'>" + str(self.ticket_id.id) + "</a>"
                      })
          if self.contactoInterno:
            ticket.write({'contactoInterno' : self.contactoInterno.id})
          query = "update helpdesk_ticket set \"partner_id\" = " + str(self.ticket_id.partner_id.id) + ", \"x_studio_empresas_relacionadas\" =" + str(self.ticket_id.x_studio_empresas_relacionadas.id) + ", \"contactoInterno\" = " + str(self.contactoInterno.id) + " where id = " + str(ticket.id) + ";"
          self.env.cr.execute(query)
          self.env.cr.commit()
          ticket._compute_datosCliente()

          self.env['helpdesk.diagnostico'].create({'ticketRelacion': ticket.id
                                                  ,'comentario': 'Ticket creado por reincidencia. Número de ticket relacionado: ' + str(self.ticket_id.id) + ' Motivo: ' + self.motivo
                                                  ,'estadoTicket': ticket.stage_id.name
                                                  #,'evidencia': [(6,0,self.evidencia.ids)]
                                                  ,'mostrarComentario': True,
                                                  'creadoPorSistema': True
                                                  })
          ticket.obten_ulimo_diagnostico_fecha_usuario()

          mensajeTitulo = "Ticket generado!!!"
          mensajeCuerpo = 'Ticket ' + str(ticket.id) + ' generado por reinsidencia'
          wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
          
          view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                  'context': self.env.context,
                  }
        






class ActivarTicketCanceladoTonerMassAction(TransientModel):
    _name = 'helpdesk.activar.cancelado.toner'
    _description = 'Activar tickets que fueron cancelados'
    
    def _default_ticket_ids(self):
        return self.env['helpdesk.ticket'].browse(
            self.env.context.get('active_ids'))

    ticket_ids = fields.Many2many(
        string = 'Tickets',
        comodel_name = "helpdesk.ticket",
        default = lambda self: self._default_ticket_ids(),
        help = "",
    )


    def cambioActivo(self):
        idsTicketsList = []
        for ticket in self.ticket_ids:
            if ticket.x_studio_field_nO7Xg:
                mensajeTitulo = 'No es posible volver a activar tickets!!!'
                mensajeCuerpo = 'No es posible activar tickets debido a que ya cuentan con una solicitud generada.'
                wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
                view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                        'context': self.env.context,
                        }

            estadoAntes = str(ticket.stage_id.name)
            if ticket.estadoCancelado:
                ticket.write({'stage_id': 1})
                query = "update helpdesk_ticket set stage_id = 1 where id = " + str(ticket.x_studio_id_ticket) + ";"
                ss = self.env.cr.execute(query)

                #Activando contadores
                contadores = self.env['dcas.dcas'].search([['x_studio_tickett', '=', str(ticket.id)]])
                _logger.info('Contadores: ' + str(contadores))
                #contadores.unlink()
                for contador in contadores:
                    contador.active = True

                idsTicketsList.append(ticket.id)
                #Cancelando el pedido de venta
                #self.estadoCancelado = True
                #pedidoDeVentaACancelar = self.x_studio_field_nO7Xg
                #if pedidoDeVentaACancelar:
                #    regresa = self.env['stock.picking'].search([['sale_id', '=', int(pedidoDeVentaACancelar.id)], ['state', '=', 'done']])
                #    if len(regresa) == 0:
                #        pedidoDeVentaACancelar.action_cancel()
                
                

        mensajeTitulo = 'Tickets activados!!!'
        mensajeCuerpo = 'Seactivaron los tickets seleccionados. \nTickets activados: ' + str(idsTicketsList)
        wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                'context': self.env.context,
                }



class CerrarTicketsMassAction(TransientModel):
    _name = 'helpdesk.cerrar.tickets.mesa'
    _description = 'Cierra los tickets alv'
    
    def _default_ticket_ids(self):
        return self.env['helpdesk.ticket'].browse(
            self.env.context.get('active_ids'))

    ticket_ids = fields.Many2many(
        string = 'Tickets',
        comodel_name = "helpdesk.ticket",
        default = lambda self: self._default_ticket_ids(),
        help = "",
    )

    def confirmarCerrados(self):
        _logger.info("CerrarTickets.confirmar()")

        for ticket in self.ticket_ids:
            ticket.write({'stage_id': 18})
            self.env['helpdesk.diagnostico'].create({
                                                        'ticketRelacion': ticket.id,
                                                        'estadoTicket': ticket.stage_id.name,
                                                        'write_uid':  self.env.user.name,
                                                        'comentario': 'Cierre de ticket que esta cerrado en techra.' ,
                                                        'creadoPorSistema': True
                                                    })
            ticket.obten_ulimo_diagnostico_fecha_usuario()




class CancelarSolTonerMassAction(TransientModel):
    _name = 'helpdesk.cancelar.tickets.toner'
    _description = 'Crear y validad solicitudes de toner'
    
    def _default_ticket_ids(self):
        return self.env['helpdesk.ticket'].browse(
            self.env.context.get('active_ids'))

    ticket_ids = fields.Many2many(
        string = 'Tickets',
        comodel_name = "helpdesk.ticket",
        default = lambda self: self._default_ticket_ids(),
        help = "",
    )

    def confirmarCancelado(self):
        _logger.info("CancelarSolTonerMassAction.confirmar()")

        for ticket in self.ticket_ids:
            ticket.cambioCancelado()




class CrearYValidarSolTonerMassAction(TransientModel):
    _name = 'helpdesk.validar.toner'
    _description = 'Crear y validad solicitudes de toner'
    
    def _default_ticket_ids(self):
        return self.env['helpdesk.ticket'].browse(
            self.env.context.get('active_ids'))

    ticket_ids = fields.Many2many(
        string = 'Tickets',
        comodel_name = "helpdesk.ticket",
        default = lambda self: self._default_ticket_ids(),
        help = "",
    )

    almacenes = fields.Many2one(
                                    'stock.warehouse',
                                    store = True,
                                    track_visibility = 'onchange',
                                    string = 'Almacén'
                                )

    def confirmar(self):
        _logger.info("CrearYValidarSolTonerMassAction.confirmar()")
        _logger.info('3312: CrearYValidarSolTonerMassAction.confirmar() inicio de proceso: ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        listaTicketsSale = []
        listaDeTicketsConSolicitud = []
        listaDeTicketsValidados = []
        listaDeTicketsSinPoroductos = []
        for ticket in self.ticket_ids:
            if not ticket.x_studio_field_nO7Xg:
                jalaSolicitudes = ''
                if ticket.stage_id.id == 91 and ticket.x_studio_field_nO7Xg:
                    #self.stage_id.id = 93
                    
                    #query = "update helpdesk_ticket set stage_id = 93 where id = " + str(ticket.x_studio_id_ticket) + ";"
                    #ss = self.env.cr.execute(query)
                    break
                if ticket.team_id.id == 8 or ticket.team_id.id == 13 or ticket.team_id.id == 50 or ticket.team_id.id == 60:
                    x = 1 ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                    if self.almacenes:
                        #if ticket.x_studio_almacen_1== 'Agricola':
                        if self.almacenes.id == 1:
                        #   sale.write({'warehouse_id':1})
                            x = 12
                        #if ticket.x_studio_almacen_1=='Queretaro':
                        if self.almacenes.id == 18:
                        #   sale.write({'warehouse_id':18})
                            x = 115
                    sale = self.env['sale.order'].sudo().create({ 'partner_id' : ticket.partner_id.id
                                                                , 'origin' : "Ticket de tóner: " + str(ticket.x_studio_id_ticket)
                                                                , 'x_studio_tipo_de_solicitud' : "Venta"
                                                                , 'x_studio_requiere_instalacin' : True                                       
                                                                , 'user_id' : ticket.user_id.id                                           
                                                                #, 'x_studio_tcnico' : ticket.x_studio_tcnico.id
                                                                , 'x_studio_field_RnhKr': ticket.localidadContacto.id
                                                                , 'partner_shipping_id' : ticket.x_studio_empresas_relacionadas.id
                                                                , 'warehouse_id' : self.almacenes.id
                                                                , 'team_id' : 1
                                                                , 'x_studio_comentario_adicional': ticket.x_studio_comentarios_de_localidad
                                                                , 'x_studio_field_bxHgp': int(ticket.x_studio_id_ticket)
                                                                ,'x_studio_corte': ticket.x_studio_corte     
                                                              })
                    if self.almacenes:
                        ticket.write({'almacenes': self.almacenes.id})
                    ticket.write({'x_studio_field_nO7Xg': sale.id})
                    #record['x_studio_field_nO7Xg'] = sale.id
                    serieaca = ''
                    
                    for c in ticket.x_studio_equipo_por_nmero_de_serie_1:
                        bn=''
                        amar=''
                        cian=''
                        magen=''
                        car=0
                        serieaca=c.serie.name
                        weirtihgone=0
                        weirtihgwtwo=0
                        insert="insert into sale_order_line values (order_id,product_id,product_uom_qty,x_studio_field_9nQhR,route_id,price_unit, customer_lead,x_studio_toner_negro,porcentajeNegro)values("+str(sale.id)+","+str(weirtihgone)+",1,"+str(c.serie.id)+","+str(weirtihgwtwo)+",0,0,"+str(c.x_studio_toner_negro)+",1)"
                        _logger.info("Error al capturar."+str(insert))
                        #some like this need to be faster than create insert into sale_order_line (name,order_id,product_id,product_uom_qty,"x_studio_field_9nQhR",route_id,price_unit, customer_lead,product_uom)values('a',2220,10770,1,31902,1,0,0,1);
                            
                        c.write({'x_studio_tickett':ticket.x_studio_id_ticket})
                        c.write({'fuente':'helpdesk.ticket'})
                        
                        #Toner BN
                        if c.x_studio_cartuchonefro:
                            car=car+1                        
                            if c.serie.x_studio_color_bn=="B/N":
                             c.write({'porcentajeNegro':c.porcentajeNegro})
                             c.write({'x_studio_toner_negro':1})
                            else:
                             c.write({'porcentajeNegro':c.porcentajeNegro})    
                             c.write({'x_studio_toner_negro':1})
                            pro = self.env['product.product'].search([['name','=',c.x_studio_cartuchonefro.name],['categ_id','=',5]])
                            gen = pro.sorted(key='qty_available',reverse=True)[0]
                            weirtihgone = c.x_studio_cartuchonefro.id if(len(gen)==0) else gen.id
                            datos={'name': ' '
                                   ,'order_id' : sale.id
                                   , 'product_id' : weirtihgone
                                   #, 'product_id' : c.x_studio_toner_compatible.id
                                   , 'product_uom_qty' : 1
                                   , 'x_studio_field_9nQhR': c.serie.id 
                                   , 'price_unit': 0 
                                   , 'customer_lead' : 0
                                   #, 'partner_shipping_id' : ticket.x_studio_empresas_relacionadas.id
                                   }
                            if(gen['qty_available']<=0) and not weirtihgone:
                                #datos['route_id']=1
                                datos['product_id']= c.x_studio_cartuchonefro.id
                                weirtihgone=c.serie.x_studio_toner_compatible.id
                                weirtihgtwo=1
                            #insert='insert into sale_order_line values (order_id,product_id,product_uom_qty,x_studio_field_9nQhR,route_id,price_unit, customer_lead,x_studio_toner_negro,porcentajeNegro)values('+str(sale.id)+','+  str(weirtihgone)+','+1+','+str(c.serie.id)+','+str(weirtihgtwo)+',0,0,'+str(c.x_studio_toner_negro)+',1)'
                            #raise exceptions.ValidationError("Error al capturar."+str(insert))
                            
                            self.env['sale.order.line'].create(datos)
                            bn=str(c.serie.x_studio_reftoner)+', '
                        #Toner Ama
                        if c.x_studio_cartucho_amarillo:
                            car=car+1
                            c.write({'x_studio_toner_amarillo':1})
                            pro = self.env['product.product'].search([['name','=',c.x_studio_cartucho_amarillo.name],['categ_id','=',5]])
                            gen = pro.sorted(key='qty_available',reverse=True)[0]
                            datos={'name': ' '
                                   ,'order_id' : sale.id
                                   , 'product_id' : c.x_studio_cartucho_amarillo.id if(len(gen)==0) else gen.id
                                   #, 'product_id' : c.x_studio_toner_compatible.id
                                   , 'product_uom_qty' : 1
                                   , 'x_studio_field_9nQhR': c.serie.id
                                   , 'price_unit': 0 
                                   , 'customer_lead' : 0
                                   #, 'partner_shipping_id' : ticket.x_studio_empresas_relacionadas.id
                                   }
                            if(gen['qty_available']<=0) and not weirtihgone:
                                #datos['route_id']=1
                                datos['product_id']=c.x_studio_cartucho_amarillo.id
                            self.env['sale.order.line'].create(datos)
                            amar=str(c.x_studio_cartucho_amarillo.name)+', '
                        #Toner cian
                        if c.x_studio_cartucho_cian_1:
                            car=car+1
                            c.write({'x_studio_toner_cian':1})
                            pro = self.env['product.product'].search([['name','=',c.x_studio_cartucho_cian_1.name],['categ_id','=',5]])
                            gen = pro.sorted(key='qty_available',reverse=True)[0]
                            datos={'name': ' '
                                   ,'order_id' : sale.id
                                   , 'product_id' : c.x_studio_cartucho_cian_1.id if(len(gen)==0) else gen.id
                                   #, 'product_id' : c.x_studio_toner_compatible.id
                                   , 'product_uom_qty' : 1
                                   , 'x_studio_field_9nQhR': c.serie.id 
                                   , 'price_unit': 0 
                                   , 'customer_lead' : 0
                                   #, 'partner_shipping_id' : ticket.x_studio_empresas_relacionadas.id
                                   }
                            if(gen['qty_available']<=0) and not weirtihgone:
                                #datos['route_id']=1
                                datos['product_id']=c.x_studio_cartucho_cian_1.id
                            self.env['sale.order.line'].create(datos)
                            cian=str(c.x_studio_cartucho_cian_1.name)+', '
                        #Toner mage
                        if c.x_studio_cartucho_magenta:
                            car=car+1
                            c.write({'x_studio_toner_magenta':1})
                            pro = self.env['product.product'].search([['name','=',c.x_studio_cartucho_magenta.name],['categ_id','=',5]])
                            gen = pro.sorted(key='qty_available',reverse=True)[0]
                            datos={'name': ' '
                                   ,'order_id' : sale.id
                                   , 'product_id' : c.x_studio_cartucho_magenta.id if(len(gen)==0) else gen.id
                                   #, 'product_id' : c.x_studio_toner_compatible.id
                                   , 'product_uom_qty' : 1
                                   , 'x_studio_field_9nQhR': c.serie.id 
                                   , 'price_unit': 0 
                                   , 'customer_lead' : 0
                                   #, 'partner_shipping_id' : ticket.x_studio_empresas_relacionadas.id
                                   }
                            if(gen['qty_available']<=0) and not weirtihgone:
                                #datos['route_id']=1
                                datos['product_id']=c.x_studio_cartucho_magenta.id
                            self.env['sale.order.line'].create(datos)
                            magen=str(c.x_studio_cartucho_magenta.name)
                            
                        
                        if car==0:
                           #raise exceptions.ValidationError("Ningun cartucho selecionado, serie ."+str(c.serie.name))
                           listaDeTicketsSinPoroductos.append(ticket.id)
                           break
                        
                        jalaSolicitudes='solicitud de toner '+sale.name+' para la serie :'+serieaca +' '+bn+' '+amar+' '+cian+' '+magen
                    if len(sale.order_line)==0:
                       #raise exceptions.ValidationError("Ningun cartucho selecionado, revisar series .")
                       listaDeTicketsSinPoroductos.append(ticket.id)
                       break
                    sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                    jalaSolicitudess='solicitud de toner '+sale.name+' para la serie :'+serieaca
                    self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                


                    if ticket.x_studio_field_nO7Xg.order_line:
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                        sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
                        sale.write({'x_studio_corte':ticket.x_studio_corte})
                        sale.write({'x_studio_comentario_adicional':ticket.x_studio_comentarios_de_localidad})
                        x = 0
                        if self.almacenes:
                            _logger.info('3312: Exisate el almacen')
                            sale.write({'warehouse_id': self.almacenes.id})
                            #if ticket.x_studio_almacen_1=='Agricola':
                            if self.almacenes.id == 1:
                               #sale.write({'warehouse_id':1})
                               x = 12
                               _logger.info('3312: x agricola: ' + str(x))
                            if self.almacenes.id == 18:
                               #sale.write({'warehouse_id':18})
                               x = 115
                               _logger.info('3312: x Queretaro: ' + str(x))
                        
                        for lineas in sale.order_line:
                            st=self.env['stock.quant'].search([['location_id','=',x],['product_id','=',lineas.product_id.id]]).sorted(key='quantity',reverse=True)
                            requisicion=False
                            if(len(st)>0):
                                if(st[0].quantity==0):
                                    _logger.info('ptm: ' + str(datetime.datetime.now()))
                                    requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']]).sorted(key='create_date',reverse=True)
                            else:
                                requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']]).sorted(key='create_date',reverse=True)
                            if requisicion:
                                if(len(requisicion)==0):
                                    re=self.env['requisicion.requisicion'].create({'origen':'Tóner','area':'Almacen','state':'draft'})
                                    re.product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                                if(len(requisicion)>0):
                                    requisicion[0].product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                        sale.action_confirm()
                        _logger.info('3312: existe picking? ' + str(sale.picking_ids))
                        estadoActual = ticket.stage_id.name
                        estadoActualId = 0
                        if sale.picking_ids:
                            listaPickingsOrdenada = self.env['stock.picking'].sudo().search([('id', 'in', sale.mapped( 'picking_ids.id'))], order='id asc')
                            _logger.info('3312: picking ordenados ' + str(listaPickingsOrdenada))
                            if listaPickingsOrdenada[0].state == 'assigned':
                                estadoActual = 'En almacén'
                                estadoActualId = 93
                            elif 'waiting' in listaPickingsOrdenada[0].state or 'confirmed' in listaPickingsOrdenada[0].state:
                                estadoActual = 'Sin stock'
                                estadoActualId = 114
                        if estadoActualId != 0:
                            ticket.write({
                                            'stage_id': estadoActualId
                                        })
                        listaDeTicketsValidados.append(ticket.id)
                        self.env['helpdesk.diagnostico'].create({
                                                            'ticketRelacion': ticket.id,
                                                            'estadoTicket': estadoActual,
                                                            #'evidencia': [(6,0,self.evidencia.ids)],
                                                            #'mostrarComentario': self.check,
                                                            'write_uid':  self.env.user.name,
                                                            'comentario': 'Ticket validado por ' + str(self.env.user.name) +'. Pasa al proceso de almacén.' ,
                                                            'creadoPorSistema': True
                                                        })
                        ticket.obten_ulimo_diagnostico_fecha_usuario()
                    else:
                        listaDeTicketsSinPoroductos.append(ticket.id)
                        
                        """
                        mensajeTitulo = 'Solicitud sin productos!!!'
                        mensajeCuerpo = 'No es posible validar una solicitud que no tiene productos.'
                        #wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                        wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
                        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                                'context': self.env.context,
                                }
                        """
            else:
                listaDeTicketsConSolicitud.append(ticket.id)
                """
                mensajeTitulo = 'Solicitud de tóner existente!!!'
                mensajeCuerpo = 'Ya existe una solicitud de tóner. No es posible generar dos solicitudes.'
                #wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
                view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                        'context': self.env.context,
                        }
                """

            """
            saleTemp = ticket.x_studio_field_nO7Xg
            if saleTemp.id != False:
                if ticket.x_studio_id_ticket:
                    estadoAntes = str(self.stage_id.name)
                    if self.estadoSolicitudDeToner == False:    
                        query = "update helpdesk_ticket set stage_id = 93 where id = " + str(self.x_studio_id_ticket) + ";"
                        ss = self.env.cr.execute(query)
                        
                        message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: En almacén' + ". " + "\n\nSolicitud " + str(saleTemp.name) + " generada" + "\n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                        mess= {
                                'title': _('Estado de ticket actualizado!!!'),
                                'message' : message
                              }
                        self.estadoSolicitudDeToner = True
                        return {'warning': mess}
            """


            listaTicketsSale.append(ticket.x_studio_field_nO7Xg)


        #listaTicketsSale.sudo().action_confirm()
        #self.ticket_ids.write({'stage_id': 93})

        wiz = ''
        mensajeTitulo = "Solicitudes de tóner creadas y validadas !!!"
        mensajeCuerpo = "Se crearon y validaron las solicitudes de los tickets. \n\n"
        
        for ticket in listaDeTicketsValidados:
            #query = "update helpdesk_ticket set stage_id = 93 where id = " + str(ticket) + ";"
            #ss = self.env.cr.execute(query)
            #self.env.cr.commit()
            mensajeCuerpo = mensajeCuerpo + str(ticket) + ', '

        mensajeCuerpo = mensajeCuerpo + '\n\nLos siguientes tickets ya contaban con Solicitudes creadas por lo cual no fueron validados. \n\n'
        
        for ticket in listaDeTicketsConSolicitud:
            mensajeCuerpo = mensajeCuerpo + str(ticket) + ', '
        #for ticket in self.ticket_ids:
        #    mensajeCuerpo = mensajeCuerpo + str(ticket.x_studio_id_ticket) + ', '
        
        mensajeCuerpo = mensajeCuerpo + '\n\n Los siguientes tickets no tienen cartuchos en sus solicitudes, favor de revisar las series y sus cartuchos seleccionados. \n\n'
        for ticket in listaDeTicketsSinPoroductos:
            mensajeCuerpo = mensajeCuerpo + str(ticket) + ', '
        _logger.info('3312: CrearYValidarSolTonerMassAction.confirmar() fin de proceso: ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        wiz = self.env['helpdesk.alerta.series'].create({'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta_series')
        return {
                'name': _(mensajeTitulo),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.alerta.series',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }







class HelpDeskDatosToner(TransientModel):
    _name = 'helpdesk.datos.toner'
    _description = 'HelpDesk informacion de toner'

    ticket_id = fields.Many2one("helpdesk.ticket")
    diagnostico_id = fields.One2many(
                                        'helpdesk.diagnostico',
                                        'ticketRelacion',
                                        compute = '_compute_diagnosticos' 
                                    )
    serie = fields.Text(string = "Serie", compute = '_compute_serie_nombre')
    """
    series = fields.One2many(
                                'dcas.dcas',
                                'x_studio_tiquete',
                                string = 'Series',
                                #store = True,
                                compute = '_compute_series'
                            )
    """
    corte = fields.Selection(
                                [('1ero','1ero'),('2do','2do'),('3ro','3ro'),('4to','4to')], 
                                string = 'Corte', 
                                compute = '_compute_corte'
                            )
    solicitud = fields.Many2one(
                                    'sale.order', 
                                    string = 'Solicitud',
                                    compute = '_compute_solicitud'
                                )
    #backorder = fields.One2many(
    #                                'stock.picking',
    #                                'backorder_id',
    #                                string = 'Backorder',
    #                                compute = '_compute_backorder'
    #                            )
    cliente = fields.Many2one(  
                                'res.partner',
                                string = 'Cliente',
                                compute = '_compute_cliente'
                            )
    tipoCliente = fields.Selection(
                                        [('A','A'),('B','B'),('C','C'),('OTRO','D'),('VIP','VIP')], 
                                        string = 'Tipo de cliente', 
                                        compute = '_compute_tipo_cliente'
                                    )
    localidad = fields.Many2one(  
                                    'res.partner',
                                    string = 'Localidad',
                                    compute = '_compute_localidad'
                                )
    zonaLocalidad = fields.Selection(
                                        [('CHIHUAHUA','CHIHUAHUA'), ('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')], 
                                        string = 'Zona localidad',
                                        compute = '_compute_zona_localidad'
                                    )
    localidadContacto = fields.Many2one(  
                                    'res.partner',
                                    string = 'Localidad contacto',
                                    compute = '_compute_localidad_contacto'
                                )
    estadoLocalidad = fields.Text(
                                    string = 'Estado de localidad',
                                    compute = '_compute_estado_localidad'
                                )
    telefonoContactoLocalidad = fields.Text(
                                    string = 'Télefgono localidad contacto',
                                    compute = '_compute_telefono_localidad'
                                )
    movilContactoLocalidad = fields.Text(
                                    string = 'Movil localidad contacto',
                                    compute = '_compute_movil_localidad'
                                )
    correoContactoLocalidad = fields.Text(
                                    string = 'Correo electrónico localidad contacto',
                                    compute = '_compute_correo_localidad'
                                )
    direccionLocalidad = fields.Text(
                                    string = 'Dirección localidad',
                                    compute = '_compute_direccion_localidad'
                                )
    creadoEl = fields.Text(
                            string = 'Creado el',
                            compute = '_compute_creado_el'
                        )
    areaAtencion = fields.Many2one(  
                                    'helpdesk.team',
                                    string = 'Área de atención',
                                    compute = '_compute_area_atencion'
                                )
    ejecutivo = fields.Many2one(  
                                    'res.users',
                                    string = 'Ejecutivo',
                                    compute = '_compute_ejecutivo'
                                )
    encargadoArea = fields.Many2one(  
                                    'hr.employee',
                                    string = 'Encargado de área',
                                    compute = '_compute_encargado_area'
                                )
    diasAtraso = fields.Integer(
                            string = 'Días de atraso',
                            compute = '_compute_dias_atraso'
                        )
    prioridad = fields.Selection(
                                    [('0','Todas'),('1','Baja'),('2','Media'),('3','Alta'),('4','Critica')], 
                                    string = 'Prioridad', 
                                    compute = '_compute_prioridad'
                                )
    zona = fields.Selection(
                                        [('CHIHUAHUA','CHIHUAHUA'),('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')],
                                        string = 'Zona',
                                        compute = '_compute_zona'
                                    )
    zonaEstados = fields.Selection(
                                        [('Estado de México','Estado de México'), ('Campeche','Campeche'), ('Ciudad de México','Ciudad de México'), ('Yucatán','Yucatán'), ('Guanajuato','Guanajuato'), ('Puebla','Puebla'), ('Coahuila','Coahuila'), ('Sonora','Sonora'), ('Tamaulipas','Tamaulipas'), ('Oaxaca','Oaxaca'), ('Tlaxcala','Tlaxcala'), ('Morelos','Morelos'), ('Jalisco','Jalisco'), ('Sinaloa','Sinaloa'), ('Nuevo León','Nuevo León'), ('Baja California','Baja California'), ('Nayarit','Nayarit'), ('Querétaro','Querétaro'), ('Tabasco','Tabasco'), ('Hidalgo','Hidalgo'), ('Chihuahua','Chihuahua'), ('Quintana Roo','Quintana Roo'), ('Chiapas','Chiapas'), ('Veracruz','Veracruz'), ('Michoacán','Michoacán'), ('Aguascalientes','Aguascalientes'), ('Guerrero','Guerrero'), ('San Luis Potosí', 'San Luis Potosí'), ('Colima','Colima'), ('Durango','Durango'), ('Baja California Sur','Baja California Sur'), ('Zacatecas','Zacatecas')],
                                        string = 'Zona Estados',
                                        compute = '_compute_zona_estados'
                                    )
    numeroTicketCliente = fields.Text(
                                        string = 'Número de ticket cliente',
                                        compute = '_compute_numero_ticket_cliente'
                                    )
    numeroTicketDistribuidor = fields.Text(
                                            string = 'Número de ticket distribuidor',
                                            compute = '_compute_numero_ticket_distribuidor'
                                        )
    numeroTicketGuia = fields.Text(
                                    string = 'Número de ticket guía',
                                    compute = '_compute_numero_ticket_guia'
                                )
    comentarioLocalidad = fields.Text(
                                        string = 'Comentario de localidad',
                                        compute = '_compute_comentario_localidad'
                                    )
    tiempoAtrasoTicket = fields.Text(
                                        string = 'Tiempo de atraso ticket',
                                        compute = '_compute_tiempo_ticket'
                                    )
    tiempoAtrasoAlmacen = fields.Text(
                                        string = 'Tiempo de atraso almacén',
                                        compute = '_compute_tiempo_almacen'
                                    )
    tiempoAtrasoDistribucion = fields.Text(
                                            string = 'Tiempo de atraso distribución',
                                            compute = '_compute_tiempo_distribucion'
                                        )
    reportes = fields.Many2one(
                                    'ir.actions.report',
                                    string = 'Reportes disponibles',
                                    store = True
                                )

    pdfToner = fields.Binary(
                                string = "PDF",
                                store = True
                            )

    @api.depends('reportes')
    def obtenerReportePdf(self):
        for record in self:
            idExterno = record.reportes.xml_id
            pdf = self.env.ref(idExterno).sudo().render_qweb_pdf([record.ticket_id.id])[0]
            #pdf = self.env['report'].sudo().get_pdf([self.ticket_id.id], report_name)
            record.pdfToner = False
            record.pdfToner = base64.encodestring(pdf)


    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids

    def _compute_serie_nombre(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
            for serie in self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
                if self.serie:
                    self.serie = str(self.serie) + ', ' + str(serie.serie.name)
                else:
                    self.serie = str(serie.serie.name) + ', '


    def _compute_series(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
            self.series = self.ticket_id.x_studio_equipo_por_nmero_de_serie_1.ids

    def _compute_corte(self):
        if self.ticket_id.x_studio_corte:
            self.corte = self.ticket_id.x_studio_corte

    def _compute_solicitud(self):
        if self.ticket_id.x_studio_field_nO7Xg:
            self.solicitud = self.ticket_id.x_studio_field_nO7Xg.id

    #def _compute_backorder(self):
    #    if self.ticket_id.x_studio_backorder:
    #        self.backorder = self.ticket_id.x_studio_backorder.ids

    def _compute_cliente(self):
        if self.ticket_id.partner_id:
            self.cliente = self.ticket_id.partner_id.id
    
    def _compute_tipo_cliente(self):
        if self.ticket_id.x_studio_nivel_del_cliente:
            self.tipoCliente = self.ticket_id.x_studio_nivel_del_cliente

    def _compute_localidad(self):
        if self.ticket_id.x_studio_empresas_relacionadas:
            self.localidad = self.ticket_id.x_studio_empresas_relacionadas.id

    def _compute_zona_localidad(self):
        if self.ticket_id.x_studio_field_6furK:
            self.zonaLocalidad = self.ticket_id.x_studio_field_6furK

    def _compute_localidad_contacto(self):
        if self.ticket_id.localidadContacto:
            self.localidadContacto = self.ticket_id.localidadContacto.id

    def _compute_estado_localidad(self):
        if self.ticket_id.x_studio_estado_de_localidad:
            self.estadoLocalidad = self.ticket_id.x_studio_estado_de_localidad

    def _compute_telefono_localidad(self):
        if self.ticket_id.telefonoLocalidadContacto:
            self.telefonoContactoLocalidad = self.ticket_id.telefonoLocalidadContacto

    def _compute_movil_localidad(self):
        if self.ticket_id.movilLocalidadContacto:
            self.movilContactoLocalidad = self.ticket_id.movilLocalidadContacto

    def _compute_correo_localidad(self):
        if self.ticket_id.correoLocalidadContacto:
            self.correoContactoLocalidad = self.ticket_id.correoLocalidadContacto

    def _compute_direccion_localidad(self):
        if self.ticket_id.direccionLocalidadText:
            self.direccionLocalidad = self.ticket_id.direccionLocalidadText

    def _compute_creado_el(self):
        if self.ticket_id.create_date:
            self.creadoEl = str(self.ticket_id.create_date)

    def _compute_area_atencion(self):
        if self.ticket_id.team_id:
            self.areaAtencion = self.ticket_id.team_id.id

    def _compute_ejecutivo(self):
        if self.ticket_id.user_id:
            self.ejecutivo = self.ticket_id.user_id.id

    def _compute_encargado_area(self):
        if self.ticket_id.x_studio_responsable_de_equipo:
            self.encargadoArea = self.ticket_id.x_studio_responsable_de_equipo.id

    def _compute_dias_atraso(self):
        if self.ticket_id.days_difference:
            self.diasAtraso = self.ticket_id.days_difference

    def _compute_prioridad(self):
        if self.ticket_id.priority:
            self.prioridad = self.ticket_id.priority

    def _compute_zona(self):
        if self.ticket_id.x_studio_zona:
            self.zona = self.ticket_id.x_studio_zona

    def _compute_zona_estados(self):
        if self.ticket_id.zona_estados:
            self.zonaEstados = self.ticket_id.zona_estados

    def _compute_numero_ticket_cliente(self):
        if self.ticket_id.x_studio_nmero_de_ticket_cliente:
            self.numeroTicketCliente = self.ticket_id.x_studio_nmero_de_ticket_cliente

    def _compute_numero_ticket_distribuidor(self):
        if self.ticket_id.x_studio_nmero_ticket_distribuidor_1:
            self.numeroTicketDistribuidor = self.ticket_id.x_studio_nmero_ticket_distribuidor_1
    
    def _compute_numero_ticket_guia(self):
        if self.ticket_id.x_studio_nmero_de_guia_1:
            self.numeroTicketGuia = self.ticket_id.x_studio_nmero_de_guia_1

    def _compute_comentario_localidad(self):
        if self.ticket_id.x_studio_comentarios_de_localidad:
            self.comentarioLocalidad = self.ticket_id.x_studio_comentarios_de_localidad
    
    def _compute_tiempo_ticket(self):
        if self.ticket_id.tiempoDeAtrasoTicket:
            self.tiempoAtrasoTicket = self.ticket_id.tiempoDeAtrasoTicket

    def _compute_tiempo_almacen(self):
        if self.ticket_id.tiempoDeAtrasoAlmacen:
            self.tiempoAtrasoAlmacen = self.ticket_id.tiempoDeAtrasoAlmacen

    def _compute_tiempo_distribucion(self):
        if self.ticket_id.tiempoDeAtrasoDistribucion:
            self.tiempoAtrasoDistribucion = self.ticket_id.tiempoDeAtrasoDistribucion


class HelpDeskDetalleSerieToner(TransientModel):
    _name = 'helpdesk.detalle.serie.toner'
    _description = 'HelpDesk Detalle Serie del equipo de toner'
    ticket_id = fields.Many2one("helpdesk.ticket")
    historicoTickets = fields.One2many('dcas.dcas', 'serie', string = 'Historico de tickets', store = True)
    lecturas = fields.One2many('dcas.dcas', 'serie', string = 'Lecturas', store = True)
    toner = fields.One2many('dcas.dcas', 'serie', string = 'Tóner', store = True)
    historicoDeComponentes = fields.One2many('x_studio_historico_de_componentes', 'x_studio_field_MH4DO', string = 'Historico de Componentes', store = True)
    movimientos = fields.One2many('stock.move.line', 'lot_id', string = 'Movimientos', store = True)
    serie = fields.Text(string = "Serie", compute = '_compute_serie_nombre')

    filtro = fields.Boolean('Filtra series', default = False)
    series = fields.Many2one(
                                'stock.production.lot',
                                string = 'Series',
                                #default = lambda self: self._default_serie_ids(),
                                store = True,
                            )

    


    dominio = fields.Text(
                            string = 'Dominio', 
                            #store = True, 
                            #default = lambda self: self._default_dominio(),
                            compute = '_default_dominio'
                        )
    

    def _default_dominio(self):
        ids = []
        _logger.info('hola2: ' + str(self.ticket_id.x_studio_equipo_por_nmero_de_serie_1))
        for dca in self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
            ids.append(dca.serie.id)
        #ids = str(self._context['dominioTest'])
        #ids = str(self.env.context.get('dominio'))
        self.dominio = str(ids)
        #return str(ids)
        

    @api.onchange('filtro')
    def cambiaDominioSeries(self):
        if self.filtro:
            return {'domain': {'series': [('id', 'in', ast.literal_eval(self.dominio))] }}
        else:
            return {'domain': {'series': [()] }}


    def _compute_serie_nombre(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
            for serie in self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
                if self.serie:
                    self.serie = str(self.serie) + ', ' + str(serie.serie.name)
                else:
                    self.serie = str(serie.serie.name) + ', '

    @api.onchange('series')
    def actualizaRegistros(self):
        _logger.info('HelpDeskDetalleSerieToner.actualizaRegistros()')
        self.historicoTickets = [(5, 0, 0)]
        self.lecturas = [(5, 0, 0)]
        self.toner = [(5, 0, 0)]
        self.historicoDeComponentes = [(5, 0, 0)]
        self.movimientos = [(5, 0, 0)]
        _logger.info('dca if self.series: ' + str(self.series))
        if self.series:
            self.historicoTickets = self.series.x_studio_field_Yxv2m.ids
            #_logger.info('dca forantes0: ' + str(self.ticket_id.x_studio_equipo_por_nmero_de_serie_1))
            #_logger.info('dac forantes1: ' + str(self.ticket_id))
            #_logger.info('dac forantes2: ' + str(self.ticket_id.x_studio_equipo_por_nmero_de_serie_1))
            #for dca in self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
                #_logger.info('dca For: ' + str(dca))
                #_logger.info('dca If1 furea: ' + str(dca.serie.id))
                #_logger.info('dca If2 fuera: ' + str(self.series.id))
                #if dca.serie.id == self.series.id:
                    #_logger.info('dca If1: ' + str(dca.serie.id))
                    #_logger.info('dca If2: ' + str(self.series.id))
            _logger.info('dca self.series: ' + str(self.series))
            _logger.info('dca self.series.x_studio_field_PYss4: ' + str(self.series.x_studio_field_PYss4))
            _logger.info('dca self.series.x_studio_field_PYss4.ids: ' + str(self.series.x_studio_field_PYss4.ids))
            self.lecturas = self.series.x_studio_field_PYss4.ids
            self.toner = self.series.x_studio_toner_1.ids

            self.historicoDeComponentes = self.series.x_studio_histrico_de_componentes.ids
            self.movimientos = self.series.x_studio_move_line.ids
        else:
            self.historicoTickets = [(5, 0, 0)]
            self.lecturas = [(5, 0, 0)]
            self.toner = [(5, 0, 0)]
            self.historicoDeComponentes = [(5, 0, 0)]
            self.movimientos = [(5, 0, 0)]

    """
    @api.onchange('series')
    def _compute_historico_tickets(self):
        self.historicoTickets = []
        #self.write({'historicoTickets': [] })
        if self.series:
            self.historicoTickets = self.series.x_studio_field_Yxv2m.ids

    @api.onchange('series')
    def _compute_lecturas(self):
        _logger.info('aggggg: ' + str(self.series.x_studio_field_PYss4))
        for dca in self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
            if dca.serie.id == self.series.id:
                self.lecturas = self.dca.serie.x_studio_field_PYss4.ids
        #self.lecturas = []
        #self.write({'lecturas': [] })
        #if self.series:
        #    self.lecturas = self.series.x_studio_field_PYss4.ids

    @api.onchange('series')
    def _compute_toner(self):
        _logger.info('aggggg: ' + str(self.series.x_studio_toner_1))
        for dca in self.ticket_id.x_studio_equipo_por_nmero_de_serie_1:
            if dca.serie.id == self.series.id:
                self.toner = self.dca.serie.x_studio_toner_1.ids
        #self.toner = []
        #self.write({'toner': [] })
        #if self.series:
        #    self.toner = self.series.x_studio_toner_1.ids

    @api.onchange('series')
    def _compute_historico_de_componentes(self):
        self.historicoDeComponentes = []
        #self.write({'historicoDeComponentes': [] })
        if self.series:
            self.historicoDeComponentes = self.series.x_studio_histrico_de_componentes.ids

    @api.onchange('series')
    def _compute_movimientos(self):
        self.movimientos = []
        #self.write({'movimientos': [] })
        if self.series:
            self.movimientos = self.series.x_studio_move_line.ids
    """





class helpdesk_crearToner(TransientModel):
    _name = 'helpdesk.tonerticket'
    _description = 'helpdesk crear ticket de tóner'


    #localidad = fields.Many2one('res.partner', string = 'Localidad', default = False, store = True)
    tipoDeDireccion = fields.Selection([('contact','Contacto')
                                        ,('invoice','Dirección de facturación')
                                        ,('delivery','Dirección de envío')
                                        ,('other','Otra dirección')
                                        ,('private','Dirección Privada')]
                                        , default='contact', string = "Tipo de dirección", store=True)
    subtipo = fields.Selection([('Contacto comercial','Contacto comercial')
                                ,('Contacto sistemas','Contacto sistemas')
                                ,('Contacto para pagos','Contacto parra pagos')
                                ,('Contacto para compras','Contacto para compras')
                                ,('Representante legal','Representante legal')
                                ,('Contacto de localidad','Contacto de localidad')
                                ,('private','Dirección Privada')]
                                , string = "Subtipo", store=True)
    nombreDelContacto = fields.Char(string='Nombre de contacto', default = ' ')
    titulo = fields.Many2one('res.partner.title', store=True, string='Titulo')
    puestoDeTrabajo = fields.Char(string='Puesto de trabajo')
    correoElectronico = fields.Char(string='Correo electrónico')
    telefono = fields.Char(string='Teléfono')
    movil = fields.Char(string='Móvil')
    notas = fields.Text(string="Notas")

    direccionNombreCalle = fields.Char(string='Nombre de la calle')
    direccionNumeroExterior = fields.Char(string='Número exterior')
    direccionNumeroInterior = fields.Char(string='Número interior')
    direccionColonia = fields.Char(string='Colonia')
    direccionLocalidad = fields.Char(string='Localidad')
    direccionCiudad = fields.Char(string='Ciudad', default='Ciudad de México')
    direccionCodigoPostal = fields.Char(string='Código postal')
    direccionPais = fields.Many2one('res.country', store=True, string='País', default='156')
    direccionEstado = fields.Many2one('res.country.state', store=True, string='Estado', domain="[('country_id', '=?', direccionPais)]")
    
    direccionZona = fields.Selection([('SUR','SUR')
                                      ,('NORTE','NORTE')
                                      ,('PONIENTE','PONIENTE')
                                      ,('ORIENTE','ORIENTE')
                                      ,('CENTRO','CENTRO')
                                      ,('DISTRIBUIDOR','DISTRIBUIDOR')
                                      ,('MONTERREY','MONTERREY')
                                      ,('CUERNAVACA','CUERNAVACA')
                                      ,('GUADALAJARA','GUADALAJARA')
                                      ,('QUERETARO','QUERETARO')
                                      ,('CANCUN','CANCUN')
                                      ,('VERACRUZ','VERACRUZ')
                                      ,('PUEBLA','PUEBLA')
                                      ,('TOLUCA','TOLUCA')
                                      ,('LEON','LEON')
                                      ,('COMODIN','COMODIN')
                                      ,('VILLAHERMOSA','VILLAHERMOSA')
                                      ,('MERIDA','MERIDA')
                                      ,('ALTAMIRA','ALTAMIRA')]
                                      , string = 'Zona')
    mostrarAnadirContacto = fields.Boolean(
                                            string = "mostrar añadir contacto",
                                            default = False, 
                                            store = True
                                        )



    #dca = fields.One2many('dcas.dcas', 'x_studio_tiquete', string = 'Serie', store = True)
    tipoReporte = fields.Selection(
                                        [('Falla','Falla'),('Incidencia','Incidencia'),('Reeincidencia','Reeincidencia'),('Prefunta','Pregunta'),('Requerimiento','Requerimiento'),('Solicitud de refacción','Solicitud de refacción'),('Conectividad','Conectividad'),('Reincidencias','Reincidencias'),('Instalación','Instalación'),('Mantenimiento Preventivo','Mantenimiento Preventivo'),('IMAC','IMAC'),('Proyecto','Proyecto'),('Retiro de equipo','Retiro de equipo'),('Cambio','Cambio'),('Servicio de Software','Servicio de Software'),('Resurtido de Almacen','Resurtido de Almacen'),('Supervisión','Supervisión'),('Demostración','Demostración'),('Toma de lectura','Toma de lectura')], 
                                        string = 'Tipo de reporte', 
                                        store = True
                                    )
    corte = fields.Selection(
                                [('1ero','1ero'),('2do','2do'),('3ro','3ro'),('4to','4to')], 
                                string = 'Corte', 
                                store = True
                            )
    almacen = fields.Selection(
                                [('Agricola','Agricola'),('Queretaro','Queretaro')],
                                string = 'Almacen', 
                                store = True
                            )
    almacenes = fields.Many2one(
                                    'stock.warehouse',
                                    store = True,
                                    track_visibility = 'onchange',
                                    string = 'Almacén'
                                )
    cliente = fields.Many2one(  
                                'res.partner',
                                string = 'Cliente',
                                store = True
                            )
    tipoCliente = fields.Selection(
                                        [('A','A'),('B','B'),('C','C'),('OTRO','D'),('VIP','VIP')], 
                                        string = 'Tipo de cliente', 
                                        store = True
                                    )
    localidad = fields.Many2one(  
                                    'res.partner',
                                    string = 'Localidad',
                                    store = True
                                )
    zonaLocalidad = fields.Selection(
                                        [('CHIHUAHUA','CHIHUAHUA'),('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')], 
                                        string = 'Zona localidad',
                                        store = True
                                    )
    localidadContacto = fields.Many2one(  
                                    'res.partner',
                                    string = 'Localidad contacto',
                                    store = True
                                )
    estadoLocalidad = fields.Text(
                                    string = 'Estado de localidad',
                                    store = True
                                )
    telefonoContactoLocalidad = fields.Text(
                                    string = 'Télefgono localidad contacto',
                                    store = True
                                )
    movilContactoLocalidad = fields.Text(
                                    string = 'Movil localidad contacto',
                                    store = True
                                )
    correoContactoLocalidad = fields.Text(
                                    string = 'Correo electrónico localidad contacto',
                                    store = True
                                )
    direccionLocalidad = fields.Text(
                                    string = 'Dirección localidad',
                                    store = True
                                )
    comentarioLocalidad = fields.Text(
                                    string = 'Comentarios de localidad',
                                    store = True
                                )
    prioridad = fields.Selection(
                                [('0','Todas'),('1','Baja'),('2','Media'),('3','Alta'),('4','Critica')], 
                                string = 'Prioridad', 
                                store = True
                            )


    validarTicket = fields.Boolean(
                                    string = "Solicitar autorización",
                                    default = False, 
                                    store = True
                                )
    validarHastaAlmacenTicket = fields.Boolean(
                                                string = "Crear y validar la solicitud de tóner",
                                                default = False, 
                                                store = True
                                            )
    ponerTicketEnEspera = fields.Boolean(
                                            string = "Crear ticket en espera",
                                            default = False, 
                                            store = True
                                        )
    textoTicketExistente = fields.Text(store = True)
    editarCliente = fields.Boolean(
                                        string = 'Editar cliente',
                                        default = False,
                                        store = True
                                    )
    idClienteAyuda = fields.Integer(
                                        string = 'idClienteAyuda',
                                        store = True,
                                        compute = '_compute_idClienteAyuda'
                                    )
    idLocalidadAyuda = fields.Integer(
                                        string = 'idLocalidadAyuda',
                                        store = True,
                                        compute = '_compute_idLocalidadAyuda'
                                    )
    numeroTicketCliente = fields.Text(
                                        string = 'Número de ticket cliente',
                                        store = True
                                    )
    numeroTicketDistribuidor = fields.Text(
                                            string = 'Número de ticket distribuidor',
                                            store = True
                                        )
    textoClienteMoroso = fields.Text(
                                        string = ' ', 
                                        store = True
                                    )
    estatus = fields.Selection(
                                    [('No disponible','No disponible'),('Moroso','Moroso'),('Al corriente','Al corriente')], 
                                    string = 'Estatus', 
                                    store = True, 
                                    default = 'No disponible'
                                )
    noCrearTicket = fields.Boolean(
                                        string = 'No crear ticket',
                                        default = False,
                                        store = True
                                    )

    @api.depends('cliente')
    def _compute_idClienteAyuda(self):
        if self.cliente:
            self.idClienteAyuda = self.cliente.id

    @api.depends('localidad')
    def _compute_idLocalidadAyuda(self):
        if self.localidad:
            self.idLocalidadAyuda = self.localidad.id


    def contacto_toner(self):
        if self.mostrarAnadirContacto:
            self.mostrarAnadirContacto = False
        else:
            self.mostrarAnadirContacto = True

    def anadirContactoALocalidad(self):
        if self.tipoDeDireccion == "contact" and self.nombreDelContacto != False:
            self.subtipo = 'Contacto de localidad'
            titulo = ''
            contacto = self.sudo().env['res.partner'].create({
                                                                'parent_id' : self.localidad.id, 
                                                                'type' : self.tipoDeDireccion, 
                                                                'x_studio_subtipo' : self.subtipo, 
                                                                'name' : self.nombreDelContacto, 
                                                                'title' : titulo, 
                                                                'function' : self.puestoDeTrabajo, 
                                                                'email' : self.correoElectronico.lower(), 
                                                                'phone' : self.telefono, 
                                                                'mobile' : self.movil, 
                                                                'comment' : self.notas, 
                                                                'team_id': 1
                                                            })
            self.mostrarAnadirContacto = False
        return {
            "type": "ir.actions.do_nothing",
        }

  
    @api.onchange('cliente')
    def cliente_moroso(self):
        if self.cliente:
            if self.cliente.x_studio_moroso:
                    self.estatus = 'Moroso'
                    textoHtml = []
                    textoHtml.append("<h2>El cliente es moroso.</h2>")
                    self.textoClienteMoroso = ''.join(textoHtml)
            else:
                #no es moroso
                self.estatus = 'Al corriente'
                self.textoClienteMoroso = ''
        else:
            #No existe cliente
            self.estatus = 'No disponible'
            self.textoClienteMoroso = ''

    @api.onchange('localidadContacto')
    def cambia_contacto_localidad(self):
        if self.localidadContacto:
            self.telefonoContactoLocalidad = self.localidadContacto.phone
            self.movilContactoLocalidad = self.localidadContacto.mobile
            self.correoContactoLocalidad = self.localidadContacto.email
        else:
            self.telefonoContactoLocalidad = ''
            self.movilContactoLocalidad = ''
            self.correoContactoLocalidad = ''

    @api.onchange('dca')
    def cambia_dca(self):
        if self.dca:
            _my_object = self.env['helpdesk.crearconserie']
            
            textoHtml = []
            textoHtml.append("<br/>")
            textoHtml.append("<br/>")
            textoHtml.append("<h1>Esta serie ya tiene un ticket en proceso.</h1>")
            textoHtml.append("<br/>")
            textoHtml.append("<br/>")
            textoHtml.append("<h3 class='text-center'>El ticket en proceso es: ")
            
            for dca in self.dca: 
                query = "select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = " +  str(dca.serie.id) + " limit 1;"
                _logger.info("test query: " + str(query))
                self.env.cr.execute(query)
                informacion = self.env.cr.fetchall()
                _logger.info("test informacion: " + str(informacion))
                if len(informacion) > 0:
                  textoHtml.append(str(informacion[0][0]))
                else:
                  self.textoTicketExistente = ''

                
                
            textoHtml.append("</h3>")
            self.textoTicketExistente =  ''.join(textoHtml)
            
            cliente = self.dca[0].serie.x_studio_cliente
            localidad = self.dca[0].serie.x_studio_localidad_2

            if cliente and localidad:
                moveLineOrdenado = self.dca[0].serie.x_studio_move_line.sorted(key="date", reverse=True)
                

                self.cliente = cliente.id
                self.tipoCliente = cliente.x_studio_nivel_del_cliente
                self.localidad = localidad.id
                self.zonaLocalidad = localidad.x_studio_field_SqU5B
                self.estadoLocalidad = localidad.state_id.name

                textoHtmlDireccion = []

                textoHtmlDireccion.append('<p>Calle: ' + localidad.street_name + '</p>')
                textoHtmlDireccion.append('<p>Número exterior: ' + localidad.street_number + '</p>')
                textoHtmlDireccion.append('<p>Número interior: ' + localidad.street_number2 + '</p>')
                textoHtmlDireccion.append('<p>Colonia: ' + localidad.l10n_mx_edi_colony + '</p>')
                textoHtmlDireccion.append('<p>Alcaldía: ' + localidad.city + '</p>')
                textoHtmlDireccion.append('<p>Estado: ' + localidad.state_id.name + '</p>')
                textoHtmlDireccion.append('<p>Código postal: ' + localidad.zip + '</p>')

                self.direccionLocalidad = ''.join(textoHtmlDireccion)
                
                #_my_object.write({'idCliente' : moveLineOrdenado[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                #                ,'idLocaliidad': moveLineOrdenado[0].location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id
                #                })
                #loc = localidad.id
                
                
                idLoc = self.env['res.partner'].search([['parent_id', '=', localidad.id],['x_studio_ultimo_contacto', '=', True]], order='create_date desc', limit=1)
                
                if idLoc:
                    self.localidadContacto = idLoc[0].id
                    self.telefonoContactoLocalidad = idLoc[0].phone
                    self.movilContactoLocalidad = idLoc[0].mobile
                    self.correoContactoLocalidad = idLoc[0].email

                else:
                    self.localidadContacto = False
                    self.telefonoContactoLocalidad = ''
                    self.movilContactoLocalidad = ''
                    self.correoContactoLocalidad = '' 
            else:
                mensajeTitulo = "Alerta!!!"
                mensajeCuerpo = "La serie seleccionada no cuenta con una ubicación. No se permitira crear el ticket. Favor de notificar al administrador con la serie seleccionada."
                warning = {'title': _(mensajeTitulo)
                        , 'message': _(mensajeCuerpo),
                }
                return {'warning': warning}

            self.noCrearTicket = False
            for dca in self.dca:
                if dca.colorEquipo == 'Color':
                    if not dca.x_studio_cartuchonefro and not dca.x_studio_cartucho_amarillo and not dca.x_studio_cartucho_cian_1 and not dca.x_studio_cartucho_magenta:
                        self.noCrearTicket = True
                        mensajeTitulo = "Alerta!!!"
                        mensajeCuerpo = "No se permitira crear un ticket hasta que no selecciones al menos un cartucho para la serie " + str(dca.serie.name)
                        warning = {'title': _(mensajeTitulo)
                                , 'message': _(mensajeCuerpo),
                        }
                        return {'warning': warning}
                elif dca.colorEquipo == 'B/N':
                    if not dca.x_studio_cartuchonefro:
                        self.noCrearTicket = True
                        mensajeTitulo = "Alerta!!!"
                        mensajeCuerpo = "No se permitira crear un ticket hasta que no selecciones cartucho para la serie " + str(dca.serie.name)
                        warning = {'title': _(mensajeTitulo)
                                , 'message': _(mensajeCuerpo),
                        }
                        return {'warning': warning}

                if dca.serie.x_studio_mini:
                    self.noCrearTicket = True
                    mensajeTitulo = "Alerta!!!"
                    mensajeCuerpo = "La serie " + str(dca.serie.name) + " pertenece a un mini almacén, no es posible crear el ticket de un mini almacén."
                    warning = {'title': _(mensajeTitulo)
                            , 'message': _(mensajeCuerpo),
                    }
                    return {'warning': warning}

        else:

            self.textoTicketExistente = ''

            self.cliente = False
            self.tipoCliente = ''
            self.localidad = False
            self.zonaLocalidad = ''
            self.estadoLocalidad = ''

            self.direccionLocalidad = ''

            self.localidadContacto = False
            self.telefonoContactoLocalidad = ''
            self.movilContactoLocalidad = ''
            self.correoContactoLocalidad = ''




    def crearTicketToner(self):
        if self.dca:
            ticket = self.env['helpdesk.ticket'].create({
                                                            'stage_id': 1,
                                                            'x_studio_tipo_de_vale': self.tipoReporte,
                                                            'x_studio_corte': self.corte,
                                                            #'x_studio_almacen_1': self.almacen,
                                                            'almacenes': self.almacenes.id,
                                                            'partner_id': self.cliente.id,
                                                            'x_studio_nivel_del_cliente': self.tipoCliente,
                                                            'x_studio_empresas_relacionadas': self.localidad.id,
                                                            'x_studio_field_6furK': self.zonaLocalidad,
                                                            'localidadContacto': self.localidadContacto.id,
                                                            'x_studio_estado_de_localidad': self.estadoLocalidad,
                                                            'telefonoLocalidadContacto': self.telefonoContactoLocalidad,
                                                            'movilLocalidadContacto': self.movilContactoLocalidad,
                                                            'correoLocalidadContacto': self.correoContactoLocalidad,
                                                            'direccionLocalidadText': self.direccionLocalidad,
                                                            'team_id': 8,
                                                            'priority': self.prioridad,
                                                            'x_studio_comentarios_de_localidad': self.comentarioLocalidad,
                                                            'x_studio_nmero_de_ticket_cliente': self.numeroTicketCliente,
                                                            'x_studio_nmero_ticket_distribuidor_1': self.numeroTicketDistribuidor,
                                                            'validarTicket': self.validarTicket,
                                                            'validarHastaAlmacenTicket': self.validarHastaAlmacenTicket,
                                                            'ponerTicketEnEspera': self.ponerTicketEnEspera
                                                        })
            self.env.cr.commit()
            objTicket = self.env['helpdesk.ticket'].search([['id', '=', ticket.id]], order='create_date desc', limit=1)
            listaDca = [(5, 0, 0)]
            for nuevoDca in self.dca:
                query = """
                            insert into dcas_dcas (\"serie\", \"colorEquipo\", \"ultimaUbicacion\",
                                                    \"equipo\", \"contadorMono\", \"contadorAnteriorNegro\", 
                                                    \"contadorColor\", \"contadorAnteriorColor\", \"x_studio_cartuchonefro\", 
                                                    \"x_studio_rendimiento_negro\", \"porcentajeNegro\", \"x_studio_cartucho_amarillo\", 
                                                    \"x_studio_rendimientoa\", \"porcentajeAmarillo\", \"x_studio_cartucho_cian_1\", 
                                                    \"x_studio_rendimientoc\", \"porcentajeCian\", \"x_studio_cartucho_magenta\", 
                                                    \"x_studio_rendimientom\", \"porcentajeMagenta\", \"tablahtml\", \"x_studio_tiquete\") 
                                                    values (
                                                    """ + str(nuevoDca.serie.id) + """,
                                                    """ + str(nuevoDca.colorEquipo) + """,
                                                    """ + str(nuevoDca.ultimaUbicacion) + """,
                                                    """ + str(nuevoDca.equipo) + """,
                                                    """ + str(nuevoDca.contadorMono) + """,
                                                    """ + str(nuevoDca.contadorAnteriorNegro) + """,
                                                    """ + str(nuevoDca.contadorColor) + """,
                                                    """ + str(nuevoDca.contadorAnteriorColor) + """,
                                                    """ + str(nuevoDca.x_studio_cartuchonefro.id) + """,
                                                    """ + str(nuevoDca.x_studio_rendimiento_negro) + """,
                                                    """ + str(nuevoDca.porcentajeNegro) + """,
                                                    """ + str(nuevoDca.x_studio_cartucho_amarillo.id) + """,
                                                    """ + str(nuevoDca.x_studio_rendimientoa) + """,
                                                    """ + str(nuevoDca.porcentajeAmarillo) + """,
                                                    """ + str(nuevoDca.x_studio_cartucho_cian_1.id) + """,
                                                    """ + str(nuevoDca.x_studio_rendimientoc) + """,
                                                    """ + str(nuevoDca.porcentajeCian) + """,
                                                    """ + str(nuevoDca.x_studio_cartucho_magenta.id) + """,
                                                    """ + str(nuevoDca.x_studio_rendimientom) + """,
                                                    """ + str(nuevoDca.porcentajeMagenta) + """,
                                                    """ + str(nuevoDca.tablahtml) + """,
                                                    """ + str(objTicket.id) + """
                                                    );
                        """
                self.env.cr.execute(query)
                self.env.cr.commit()
                informacion = self.env.cr.fetchall()
                _logger.info('3312: informacion: ' + str(informacion))
                """
                listaDca.append([
                                    0, 
                                    0, 
                                    {   
                                        'serie': nuevoDca.serie.id,
                                        'colorEquipo': nuevoDca.colorEquipo,
                                        'ultimaUbicacion': nuevoDca.ultimaUbicacion,
                                        'equipo': nuevoDca.equipo,
                                        'contadorMono': nuevoDca.contadorMono,
                                        'contadorAnteriorNegro': nuevoDca.contadorAnteriorNegro,
                                        'contadorColor': nuevoDca.contadorColor,
                                        'contadorAnteriorColor': nuevoDca.contadorAnteriorColor,
                                        'x_studio_cartuchonefro': nuevoDca.x_studio_cartuchonefro.id,
                                        'x_studio_rendimiento_negro': nuevoDca.x_studio_rendimiento_negro,
                                        'porcentajeNegro': nuevoDca.porcentajeNegro,
                                        'x_studio_cartucho_amarillo': nuevoDca.x_studio_cartucho_amarillo.id,
                                        'x_studio_rendimientoa': nuevoDca.x_studio_rendimientoa,
                                        'porcentajeAmarillo': nuevoDca.porcentajeAmarillo,
                                        'x_studio_cartucho_cian_1': nuevoDca.x_studio_cartucho_cian_1.id,
                                        'x_studio_rendimientoc': nuevoDca.x_studio_rendimientoc,
                                        'porcentajeCian': nuevoDca.porcentajeCian,
                                        'x_studio_cartucho_magenta': nuevoDca.x_studio_cartucho_magenta.id,
                                        'x_studio_rendimientom': nuevoDca.x_studio_rendimientom,
                                        'porcentajeMagenta': nuevoDca.porcentajeMagenta,
                                        'tablahtml': nuevoDca.tablahtml
                                    }
                               ])
                """
            #objTicket.write({
            #                    'x_studio_equipo_por_nmero_de_serie_1': listaDca
            #                })
            objTicket.write({
                            'partner_id': self.cliente.id,
                            'x_studio_empresas_relacionadas': self.localidad.id,
                            'team_id': 8,
                            'x_studio_field_6furK': self.zonaLocalidad,
                            #'x_studio_equipo_por_nmero_de_serie_1': listaDca
                            #'x_studio_equipo_por_nmero_de_serie_1': [(6,0,self.dca.ids)]
                        })
            #ticket.x_studio_equipo_por_nmero_de_serie_1 = listaDca
            self.env.cr.commit()
            objTicket._compute_datosCliente()

            #CASOS
            #CASO EN EL QUE SE PASA DIRECTO A ALMACEN
            if self.validarHastaAlmacenTicket and not self.validarTicket and not self.ponerTicketEnEspera:
                objTicket.crearYValidarSolicitudDeToner()
            #CASO EN EL QUE PASA A SER VALIDADO POR EL RESPONSABLE
            elif self.validarTicket and not self.validarHastaAlmacenTicket and not self.ponerTicketEnEspera:
                query = "update helpdesk_ticket set stage_id = 91 where id = " + str(objTicket.id) + ";"
                ss = self.env.cr.execute(query)
                self.env.cr.commit()
            #CASO EN EL QUE EL TICKET PASA A ESTAR EN ESPERA 'PRETICKET'
            elif self.ponerTicketEnEspera and not self.validarHastaAlmacenTicket and not self.validarTicket:
                query = "update helpdesk_ticket set stage_id = 1 where id = " + str(objTicket.id) + ";"
                ss = self.env.cr.execute(query)
                self.env.cr.commit()
            #CASO EN EL QUE PASA A DECICION DEL SISTEMA
            elif not self.validarHastaAlmacenTicket and not self.validarTicket and not self.ponerTicketEnEspera:
                #CASO COLOR
                if objTicket.x_studio_equipo_por_nmero_de_serie_1[0].colorEquipo == 'Color':
                    #dcaInfo = self.dca[0]
                    dcaInfo = objTicket.x_studio_equipo_por_nmero_de_serie_1[0]
                    #SI LOS PORCENTAJES SON MAYORES A 60%
                    if dcaInfo.porcentajeNegro >= 60 and dcaInfo.porcentajeAmarillo >= 60 and dcaInfo.porcentajeCian >= 60 and dcaInfo.porcentajeMagenta >= 60:
                        objTicket.crearYValidarSolicitudDeToner()
                    else:
                        # PASA A RESPONSABLE
                        query = "update helpdesk_ticket set stage_id = 91 where id = " + str(objTicket.id) + ";"
                        ss = self.env.cr.execute(query)
                        self.env.cr.commit()
                else:
                    #CASO EN QUE ES BLANCO NEGRO
                    dcaInfo = objTicket.x_studio_equipo_por_nmero_de_serie_1[0]
                    if dcaInfo.porcentajeNegro >= 60:
                        objTicket.crearYValidarSolicitudDeToner()
                    else:
                        # PASA A RESPONSABLE
                        query = "update helpdesk_ticket set stage_id = 91 where id = " + str(objTicket.id) + ";"
                        ss = self.env.cr.execute(query)
                        self.env.cr.commit()

            wiz = ''
            mensajeTitulo = "Ticket generado!!!"
            #mensajeCuerpo = "Se creo el ticket '" + str(ticket.id) + "' sin número de serie para cliente " + self.cliente + " con localidad " + self.localidad + "\n\n"
            mensajeCuerpo = "Se creo el ticket '" + str(objTicket.id) + "' con el número de serie " + self.dca[0].serie.name + ".\n\n"
            wiz = self.env['helpdesk.alerta.series'].create({'ticket_id': objTicket.id, 'mensaje': mensajeCuerpo})
            view = self.env.ref('helpdesk_update.view_helpdesk_alerta_series')
            return {
                      'name': _(mensajeTitulo),
                      'type': 'ir.actions.act_window',
                      'view_type': 'form',
                      'view_mode': 'form',
                      'res_model': 'helpdesk.alerta.series',
                      'views': [(view.id, 'form')],
                      'view_id': view.id,
                      'target': 'new',
                      'res_id': wiz.id,
                      'context': self.env.context,
                    }
        #else:
            #NO HAY DCA POR LO TANTO NO SE GENERA TICKET




"""
class helpdesk_agregar_productos(TransientModel):
    _name = 'helpdesk.agregar.productos'
    _description = 'helpdesk añade productos a la lista de productos de un ticket.'
    
    ticket_id = fields.Many2one(
                                    "helpdesk.ticket",
                                    string = 'Ticket'
                                )

    productos = fields.Many2many(
                                    'product.product', 
                                    string = "Productos"
                                )
    activar_compatibilidad = fields.Boolean(
                                                string = 'Activar compatibilidad',
                                                default = False
                                            )
    estadoSolicitud = fields.Text(
                                    string = 'Estado de la SO',
                                    store = True,
                                    help = 
                                                Estado en el que se encuentra la solicitud de refacción y/o accesorios.
                                                En caso de que no exista se muestra el mensaje 'No existe un SO'.
                                            
                                )
    accesorios = fields.One2many('helpdesk.refacciones', 'wizRela', string = 'Accesorios')


    @api.onchange('activar_compatibilidad')
    #
    def productos_filtro(self):
        res = {}             
        g = str(self.ticket_id.x_studio_nombretmp)
        
        if self.activar_compatibilidad and self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            if g != 'False':
                list = ast.literal_eval(g)
                idf = self.ticket_id.team_id.id
                tam = len(list)
                if idf == 8 or idf == 13 :  
                   res['domain']={'productos':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
                if idf == 9:
                   res['domain']={'productos':[('categ_id', '=', 7),('x_studio_toner_compatible.id','=',list[0])]}
                if idf != 9 and idf != 8:
                   res['domain']={'productos':[('categ_id', '!=', 5),('x_studio_toner_compatible.id','=',list[0])]}
        else:
            res['domain']={'productos':[('categ_id', '=', 7)]}
        return res

    def agregarProductos(self):
        #for producto in self.productos:
            #ticket_id.write({})

        self.ticket_id.x_studio_productos = [(6, 0, self.productos.ids)]
        mensajeTitulo = 'Productos agregados!!!'
        mensajeCuerpo = 'Se agregaron los productos y sus cantidades.'
        #wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
        wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                'context': self.env.context,
                }
"""        

















class HelpDeskContactoToner(TransientModel):
    _name = 'helpdesk.contacto.toner'
    _description = 'HelpDesk Contacto toner'
    #ticket_id = fields.Many2one("helpdesk.ticket")
    

    #dca = fields.One2many('dcas.dcas', 'x_studio_tiquete', string = 'Serie', store = True)
    tipoReporte = fields.Selection(
                                        [('Falla','Falla'),('Incidencia','Incidencia'),('Reeincidencia','Reeincidencia'),('Prefunta','Pregunta'),('Requerimiento','Requerimiento'),('Solicitud de refacción','Solicitud de refacción'),('Conectividad','Conectividad'),('Reincidencias','Reincidencias'),('Instalación','Instalación'),('Mantenimiento Preventivo','Mantenimiento Preventivo'),('IMAC','IMAC'),('Proyecto','Proyecto'),('Retiro de equipo','Retiro de equipo'),('Cambio','Cambio'),('Servicio de Software','Servicio de Software'),('Resurtido de Almacen','Resurtido de Almacen'),('Supervisión','Supervisión'),('Demostración','Demostración'),('Toma de lectura','Toma de lectura')], 
                                        string = 'Tipo de reporte', 
                                        store = True
                                    )
    corte = fields.Selection(
                                [('1ero','1ero'),('2do','2do'),('3ro','3ro'),('4to','4to')], 
                                string = 'Corte', 
                                store = True
                            )
    almacen = fields.Selection(
                                [('Agricola','Agricola'),('Queretaro','Queretaro')],
                                string = 'Almacen', 
                                store = True
                            )
    almacenes = fields.Many2one(
                                    'stock.warehouse',
                                    store = True,
                                    track_visibility = 'onchange',
                                    string = 'Almacén'
                                )
    cliente = fields.Many2one(  
                                'res.partner',
                                string = 'Cliente',
                                store = True
                            )
    tipoCliente = fields.Selection(
                                        [('A','A'),('B','B'),('C','C'),('OTRO','D'),('VIP','VIP')], 
                                        string = 'Tipo de cliente', 
                                        store = True
                                    )
    localidad = fields.Many2one(  
                                    'res.partner',
                                    string = 'Localidad',
                                    store = True
                                )
    zonaLocalidad = fields.Selection(
                                        [["SUR","SUR"],["NORTE","NORTE"],["PONIENTE","PONIENTE"],["ORIENTE","ORIENTE"],["CENTRO","CENTRO"],["DISTRIBUIDOR","DISTRIBUIDOR"],["MONTERREY","MONTERREY"],["CUERNAVACA","CUERNAVACA"],["GUADALAJARA","GUADALAJARA"],["QUERETARO","QUERETARO"],["CANCUN","CANCUN"],["VERACRUZ","VERACRUZ"],["PUEBLA","PUEBLA"],["TOLUCA","TOLUCA"],["LEON","LEON"],["COMODIN","COMODIN"],["VILLAHERMOSA","VILLAHERMOSA"],["MERIDA","MERIDA"],["VERACRUZ","VERACRUZ"],["ALTAMIRA","ALTAMIRA"],["DF00","DF00"],["SAN LP","SAN LP"],["ESTADO DE MÉXICO","ESTADO DE MÉXICO"],["Foraneo Norte","Foraneo Norte"],["Foraneo Sur","Foraneo Sur"],["CHIHUAHUA","CHIHUAHUA"]],
                                        string = 'Zona localidad',
                                        store = True
                                    )
    localidadContacto = fields.Many2one(  
                                    'res.partner',
                                    string = 'Localidad contacto',
                                    store = True
                                )
    estadoLocalidad = fields.Text(
                                    string = 'Estado de localidad',
                                    store = True
                                )
    telefonoContactoLocalidad = fields.Text(
                                    string = 'Télefgono localidad contacto',
                                    store = True
                                )
    movilContactoLocalidad = fields.Text(
                                    string = 'Movil localidad contacto',
                                    store = True
                                )
    correoContactoLocalidad = fields.Text(
                                    string = 'Correo electrónico localidad contacto',
                                    store = True
                                )
    direccionLocalidad = fields.Text(
                                    string = 'Dirección localidad',
                                    store = True
                                )
    comentarioLocalidad = fields.Text(
                                    string = 'Comentarios de localidad',
                                    store = True
                                )
    prioridad = fields.Selection(
                                [('0','Todas'),('1','Baja'),('2','Media'),('3','Alta'),('4','Critica')], 
                                string = 'Prioridad', 
                                store = True
                            )


    validarTicket = fields.Boolean(
                                    string = "Solicitar autorización",
                                    default = False, 
                                    store = True
                                )
    validarHastaAlmacenTicket = fields.Boolean(
                                                string = "Crear y validar la solicitud de tóner",
                                                default = False, 
                                                store = True
                                            )
    ponerTicketEnEspera = fields.Boolean(
                                            string = "Crear ticket en espera",
                                            default = False, 
                                            store = True
                                        )
    textoTicketExistente = fields.Text(store = True)
    editarCliente = fields.Boolean(
                                        string = 'Editar cliente',
                                        default = False,
                                        store = True
                                    )
    idClienteAyuda = fields.Integer(
                                        string = 'idClienteAyuda',
                                        store = True
                                    )
    idLocalidadAyuda = fields.Integer(
                                        string = 'idLocalidadAyuda',
                                        store = True
                                    )
    numeroTicketCliente = fields.Text(
                                        string = 'Número de ticket cliente',
                                        store = True
                                    )
    numeroTicketDistribuidor = fields.Text(
                                            string = 'Número de ticket distribuidor',
                                            store = True
                                        )
    textoClienteMoroso = fields.Text(
                                        string = ' ', 
                                        store = True
                                    )
    estatus = fields.Selection(
                                    [('No disponible','No disponible'),('Moroso','Moroso'),('Al corriente','Al corriente')], 
                                    string = 'Estatus', 
                                    store = True, 
                                    default = 'No disponible'
                                )




    localidad = fields.Many2one('res.partner', string = 'Localidad', default = False, store = True)
    tipoDeDireccion = fields.Selection([('contact','Contacto')
                                        ,('invoice','Dirección de facturación')
                                        ,('delivery','Dirección de envío')
                                        ,('other','Otra dirección')
                                        ,('private','Dirección Privada')]
                                        , default='contact', string = "Tipo de dirección", store=True)
    subtipo = fields.Selection([('Contacto comercial','Contacto comercial')
                                ,('Contacto sistemas','Contacto sistemas')
                                ,('Contacto para pagos','Contacto parra pagos')
                                ,('Contacto para compras','Contacto para compras')
                                ,('Representante legal','Representante legal')
                                ,('Contacto de localidad','Contacto de localidad')
                                ,('private','Dirección Privada')]
                                , string = "Subtipo", default = 'Contacto de localidad', store=True)
    nombreDelContacto = fields.Char(string='Nombre de contacto')
    titulo = fields.Many2one('res.partner.title', store=True, string='Titulo')
    puestoDeTrabajo = fields.Char(string='Puesto de trabajo')
    correoElectronico = fields.Char(string='Correo electrónico')
    telefono = fields.Char(string='Teléfono')
    movil = fields.Char(string='Móvil')
    notas = fields.Text(string="Notas")

    direccionNombreCalle = fields.Char(string='Nombre de la calle')
    direccionNumeroExterior = fields.Char(string='Número exterior')
    direccionNumeroInterior = fields.Char(string='Número interior')
    direccionColonia = fields.Char(string='Colonia')
    direccionLocalidad = fields.Char(string='Localidad')
    direccionCiudad = fields.Char(string='Ciudad', default='Ciudad de México')
    direccionCodigoPostal = fields.Char(string='Código postal')
    direccionPais = fields.Many2one('res.country', store=True, string='País', default='156')
    direccionEstado = fields.Many2one('res.country.state', store=True, string='Estado', domain="[('country_id', '=?', direccionPais)]")
    
    direccionZona = fields.Selection([('SUR','SUR')
                                      ,('NORTE','NORTE')
                                      ,('PONIENTE','PONIENTE')
                                      ,('ORIENTE','ORIENTE')
                                      ,('CENTRO','CENTRO')
                                      ,('DISTRIBUIDOR','DISTRIBUIDOR')
                                      ,('MONTERREY','MONTERREY')
                                      ,('CUERNAVACA','CUERNAVACA')
                                      ,('GUADALAJARA','GUADALAJARA')
                                      ,('QUERETARO','QUERETARO')
                                      ,('CANCUN','CANCUN')
                                      ,('VERACRUZ','VERACRUZ')
                                      ,('PUEBLA','PUEBLA')
                                      ,('TOLUCA','TOLUCA')
                                      ,('LEON','LEON')
                                      ,('COMODIN','COMODIN')
                                      ,('VILLAHERMOSA','VILLAHERMOSA')
                                      ,('MERIDA','MERIDA')
                                      ,('ALTAMIRA','ALTAMIRA')]
                                      , string = 'Zona')

    
    def agregarContactoALocalidad(self):
        mensajeTitulo = ''
        mensajeCuerpo = ''
        if self.localidad:
            contactoId = 0
            titulo = ''
            if len(self.titulo) == 0:
                titulo = ''
            else:
                titulo = self.titulo.id
            if self.tipoDeDireccion == "contact" and self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.localidad.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                })
                contactoId = contacto.id
            elif self.tipoDeDireccion == "delivery" and self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.localidad.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                  
                                                                 , 'street_name' : self.direccionNombreCalle
                                                                 , 'street_number' : self.direccionNumeroExterior
                                                                 , 'street_number2' : self.direccionNumeroInterior
                                                                 , 'l10n_mx_edi_colony' : self.direccionColonia
                                                                 , 'l10n_mx_edi_locality' : self.direccionLocalidad
                                                                 , 'city' : self.direccionCiudad
                                                                 , 'state_id' : self.direccionEstado.id
                                                                 , 'zip' : self.direccionCodigoPostal
                                                                 , 'country_id' : self.direccionPais.id
                                                                  
                                                                 , 'x_studio_field_SqU5B' : self.direccionZona
                                                                })
                contactoId = contacto.id
            #elif self.tipoDeDireccion != "delivery" or self.tipoDeDireccion != "contact":
            elif self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.localidad.id
                                                                 , 'type' : self.tipoDeDireccion
                                                                 , 'x_studio_subtipo' : self.subtipo
                                                                 , 'name' : self.nombreDelContacto
                                                                 , 'title' : titulo
                                                                 , 'function' : self.puestoDeTrabajo
                                                                 , 'email' : self.correoElectronico
                                                                 , 'phone' : self.telefono
                                                                 , 'mobile' : self.movil
                                                                 , 'comment' : self.notas
                                                                 , 'team_id': 1
                                                                  
                                                                 , 'street_name' : self.direccionNombreCalle
                                                                 , 'street_number' : self.direccionNumeroExterior
                                                                 , 'street_number2' : self.direccionNumeroInterior
                                                                 , 'l10n_mx_edi_colony' : self.direccionColonia
                                                                 , 'l10n_mx_edi_locality' : self.direccionLocalidad
                                                                 , 'city' : self.direccionCiudad
                                                                 , 'state_id' : self.direccionEstado.id
                                                                 , 'zip' : self.direccionCodigoPostal
                                                                 , 'country_id' : self.direccionPais.id
                                                                })
                contactoId = contacto.id
            else:
                mensajeTitulo = "Contacto sin nombre"
                mensajeCuerpo = "No es posible añadir un contacto sin nombre. Favor de indicar el nombre primero."
                #raise exceptions.except_orm(_(errorContactoSinNombre), _(mensajeContactoSinNombre))
            #self.env.cr.commit()
            if contactoId > 0:
                mensajeTitulo = "Contacto agregado." 
                mensajeCuerpo = "Contacto " + str(self.nombreDelContacto) + " agregado a la localidad " + str(self.localidad.name)
                #self.ticket_id.localidadContacto = contactoId
                
                #raise exceptions.except_orm(_(errorContactoGenerado), _(mensajeContactoGenerado))
            else:
                mensajeTitulo = "Contacto no agregado"
                mensajeCuerpo = "Contacto no agregado. Favor de verificar la información ingresada."
                #raise exceptions.except_orm(_(errorContactoNoGenerado), _(mensajeContactoNoGenerado))
        else:
            mensajeTitulo = "Contacto sin localidad"
            mensajeCuerpo = "No es posible añadir un contacto sin primero indicar la localidad. Favor de indicar la localidad primero."
            #raise exceptions.except_orm(_(errorContactoSinLocalidad), _(mensajeContactoSinLocalidad))
        


        wiz = self.env['helpdesk.tonerticket'].create({
                                                            'tipoReporte': self.tipoReporte,
                                                            'corte': self.corte,
                                                            'almacen': self.almacen,
                                                            'almacenes': self.almacenes.id,
                                                            'cliente': self.cliente.id,
                                                            'tipoCliente': self.tipoCliente,
                                                            'localidad': self.localidad.id,
                                                            'zonaLocalidad': self.zonaLocalidad,
                                                            'localidadContacto': self.localidadContacto.id,
                                                            'estadoLocalidad': self.estadoLocalidad,
                                                            'telefonoContactoLocalidad': self.telefonoContactoLocalidad,
                                                            'movilContactoLocalidad': self.movilContactoLocalidad,
                                                            'correoContactoLocalidad': self.correoContactoLocalidad,
                                                            'direccionLocalidad': self.direccionLocalidad,
                                                            'comentarioLocalidad': self.comentarioLocalidad,
                                                            'prioridad': self.prioridad,

                                                            'validarTicket': self.validarTicket,
                                                            'validarHastaAlmacenTicket': self.validarHastaAlmacenTicket,
                                                            'ponerTicketEnEspera': self.ponerTicketEnEspera,
                                                            'textoTicketExistente': self.textoTicketExistente, 
                                                            'editarCliente': self.editarCliente,
                                                            'idClienteAyuda': self.idClienteAyuda,
                                                            'idLocalidadAyuda': self.idLocalidadAyuda,
                                                            'numeroTicketCliente': self.numeroTicketCliente,
                                                            'numeroTicketDistribuidor': self.numeroTicketDistribuidor,
                                                            'textoClienteMoroso': self.textoClienteMoroso,
                                                            'estatus': self.estatus
                                                        })
        #wiz.dca = [(6, 0, self.dca.ids)]
        #wiz.dca = []
        listaDeDcas = []
        for dcaTemp in self.dca:
            listaDeDcas.append([0, 0, {
                                            'tablahtml': dcaTemp.tablahtml,
                                            'x_studio_cliente': dcaTemp.x_studio_cliente,
                                            'serie': dcaTemp.serie.id,
                                            'x_studio_color_o_bn': dcaTemp.x_studio_color_o_bn,
                                            'x_studio_cartuchonefro': dcaTemp.x_studio_cartuchonefro.id,
                                            'x_studio_rendimiento_negro': dcaTemp.x_studio_rendimiento_negro,
                                            'x_studio_cartucho_amarillo': dcaTemp.x_studio_cartucho_amarillo.id,
                                            'x_studio_rendimientoa': dcaTemp.x_studio_rendimientoa,
                                            'x_studio_cartucho_cian_1': dcaTemp.x_studio_cartucho_cian_1.id,
                                            'x_studio_rendimientoc': dcaTemp.x_studio_rendimientoc,
                                            'x_studio_cartucho_magenta': dcaTemp.x_studio_cartucho_magenta.id,
                                            'x_studio_rendimientom': dcaTemp.x_studio_rendimientom,
                                            'x_studio_fecha': dcaTemp.x_studio_fecha,
                                            'x_studio_tiquete': dcaTemp.x_studio_tiquete.id,
                                            'x_studio_tickett': dcaTemp.x_studio_tickett,
                                            'fuente': dcaTemp.fuente,

                                            'contadorColor': dcaTemp.contadorColor,
                                            'x_studio_contador_color_anterior': dcaTemp.x_studio_contador_color_anterior,
                                            'contadorMono': dcaTemp.contadorMono,
                                            'x_studio_contador_mono_anterior_1': dcaTemp.x_studio_contador_mono_anterior_1,

                                            'paginasProcesadasBN': dcaTemp.paginasProcesadasBN,
                                            'porcentajeNegro': dcaTemp.porcentajeNegro,
                                            'porcentajeAmarillo': dcaTemp.porcentajeAmarillo,
                                            'porcentajeCian': dcaTemp.porcentajeCian,
                                            'porcentajeMagenta': dcaTemp.porcentajeMagenta,
                                            'x_studio_rendimiento': dcaTemp.x_studio_rendimiento,
                                            'x_studio_rendimiento_color': dcaTemp.x_studio_rendimiento_color,
                                            'x_studio_toner_negro': dcaTemp.x_studio_toner_negro,
                                            'x_studio_toner_cian': dcaTemp.x_studio_toner_cian,
                                            'x_studio_toner_magenta': dcaTemp.x_studio_toner_magenta,
                                            'x_studio_toner_amarillo': dcaTemp.x_studio_toner_amarillo,
                                            'nivelCA': dcaTemp.nivelCA,
                                            'nivelMA': dcaTemp.nivelMA,
                                            'nivelNA': dcaTemp.nivelNA,
                                            'nivelAA': dcaTemp.nivelAA,
                                            'contadorAnteriorNegro': dcaTemp.contadorAnteriorNegro,
                                            'contadorAnteriorAmarillo': dcaTemp.contadorAnteriorAmarillo,
                                            'contadorAnteriorMagenta': dcaTemp.contadorAnteriorMagenta,
                                            'contadorAnteriorCian': dcaTemp.contadorAnteriorCian,
                                            'paginasProcesadasA': dcaTemp.paginasProcesadasA,
                                            'paginasProcesadasC': dcaTemp.paginasProcesadasC,
                                            'paginasProcesadasM': dcaTemp.paginasProcesadasM,
                                            'renM': dcaTemp.renM,
                                            'renA': dcaTemp.renA,
                                            'renC': dcaTemp.renC
                                        }])

        wiz.dca = listaDeDcas
        view = self.env.ref('helpdesk_update.view_helpdesk_crear_solicitud_toner')
        mensajeTitulo = "Crear ticket tóner"
        return {
                'name': _(mensajeTitulo),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.tonerticket',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
                }
        #wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
        #view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        #return {
        #        'name': _(mensajeTitulo),
        #        'type': 'ir.actions.act_window',
        #        'view_type': 'form',
        #        'view_mode': 'form',
        #        'res_model': 'helpdesk.alerta',
        #        'views': [(view.id, 'form')],
        #        'view_id': view.id,
        #        'target': 'new',
        #        'res_id': wiz.id,
        #        'context': self.env.context,
        #        }



class HelpdeskTicketReporte(TransientModel):
    _name = 'helpdesk.ticket.reporte'
    _description = 'Reporte de Tickets todo'
    fechaInicial = fields.Date(
                                    string = 'Fecha inicial',
                                    store = True
                                )
    fechaFinal = fields.Date(
                                string = 'Fecha final',
                                store = True
                            )
    estado = fields.Many2one(
                                'helpdesk.state',
                                string = 'Etapa'
                            )
    tipo = fields.Selection(
                                [['Todos', 'Todos'], ["Falla","Falla"], ["Toner","Toner"], ['Sistemas', 'Sistemas']],
                                string = 'Tipo de ticket'
                            )
    area = fields.Many2many(
                                'helpdesk.team',
                                string = 'Área de atención'
                            )
    tipoDeReporte = fields.Selection(
        [
            ('reporteSinContadores','Reporte sin contadores'),
            ('reporteConContadores','Reporte con contadores')
        ], 
        default = 'reporteSinContadores', 
        string = 'Tipo de reporte (backlog)'
    )
    mostrarCerrados = fields.Boolean(
                                        string = 'Mostrar cerrados',
                                        default = False
                                    )
    mostrarCancelados = fields.Boolean(
                                        string = 'Mostrar cancelados',
                                        default = False
                                    )
    tipoReporteFalla = fields.Boolean(
                                            string = 'Falla',
                                            default = False
                                        )
    tipoReporteIncidencia = fields.Boolean(
                                            string = 'Incidencia',
                                            default = False
                                        )
    tipoReporteReeincidencia = fields.Boolean(
                                            string = 'Reeincidencia',
                                            default = False
                                        )
    tipoReportePregunta = fields.Boolean(
                                            string = 'Pregunta',
                                            default = False
                                        )
    tipoReporteRequerimiento = fields.Boolean(
                                            string = 'Requerimiento',
                                            default = False
                                        )
    tipoReporteSolicitudDeRefaccion = fields.Boolean(
                                            string = 'Solicitud de Refacción',
                                            default = False
                                        )
    tipoReporteConectividad = fields.Boolean(
                                            string = 'Conectividad',
                                            default = False
                                        )
    tipoReporteReincidencias = fields.Boolean(
                                            string = 'Reincidencias',
                                            default = False
                                        )
    tipoReporteInstalacion = fields.Boolean(
                                            string = 'Instalación',
                                            default = False
                                        )
    tipoReporteMantenimientoPreventivo = fields.Boolean(
                                            string = 'Mantenimiento Preventivo',
                                            default = False
                                        )
    tipoReporteIMAC = fields.Boolean(
                                            string = 'IMAC',
                                            default = False
                                        )
    tipoReporteProyecto = fields.Boolean(
                                            string = 'Proyecto',
                                            default = False
                                        )
    tipoReporteRetiroDeEquipo = fields.Boolean(
                                            string = 'Retiro de equipo',
                                            default = False
                                        )
    tipoReporteCambio = fields.Boolean(
                                            string = 'Cambio',
                                            default = False
                                        )
    tipoReporteServicioDeSoftware = fields.Boolean(
                                            string = 'Servicio de software',
                                            default = False
                                        )
    tipoReporteResurtidoDeAlmacen = fields.Boolean(
                                            string = 'Resurtido de almacén',
                                            default = False
                                        )
    tipoReporteSupervision = fields.Boolean(
                                            string = 'Supervisión',
                                            default = False
                                        )
    tipoReporteDemostracion = fields.Boolean(
                                            string = 'Demostración',
                                            default = False
                                        )
    tipoReporteTomaDeLectura = fields.Boolean(
                                            string = 'Toma de lectura',
                                            default = False
                                        )
    clienteRelacion = fields.Many2many(
                                        'res.partner', 
                                        string = 'Cliente'
                                    )
    def areasMesa(self):
        self.area = [[5, 0, 0],[6, 0, [9,67,76,82,80,81,13,57,50,49,1,77,55,5,54,11,10,61,74,51,60,59,88]]]
        wiz = self.env['helpdesk.ticket.reporte'].search([('id', '=', self.id)], order = 'create_date desc', limit = 1 )
        view = self.env.ref('helpdesk_update.view_helpdesk_ticket_reporte')
        return {
                'name': _('Más información'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.ticket.reporte',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

    def areasToner(self):
        self.area = [[5, 0, 0],[6, 0, [8, 13]]]
        wiz = self.env['helpdesk.ticket.reporte'].search([('id', '=', self.id)], order = 'create_date desc', limit = 1 )
        view = self.env.ref('helpdesk_update.view_helpdesk_ticket_reporte')
        return {
                'name': _('Más información'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.ticket.reporte',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

    def quitarAreas(self):
        self.area = [[5, 0, 0]]
        wiz = self.env['helpdesk.ticket.reporte'].search([('id', '=', self.id)], order = 'create_date desc', limit = 1 )
        view = self.env.ref('helpdesk_update.view_helpdesk_ticket_reporte')
        return {
                'name': _('Más información'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.ticket.reporte',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

    def ponerTodos(self):
        self.tipoReporteFalla = True
        self.tipoReporteIncidencia = True
        self.tipoReporteReeincidencia = True
        self.tipoReportePregunta = True
        self.tipoReporteRequerimiento = True
        self.tipoReporteSolicitudDeRefaccion = True
        self.tipoReporteConectividad = True
        self.tipoReporteReincidencias = True
        self.tipoReporteInstalacion = True
        self.tipoReporteMantenimientoPreventivo = True
        self.tipoReporteIMAC = True
        self.tipoReporteProyecto = True
        self.tipoReporteRetiroDeEquipo = True
        self.tipoReporteCambio = True
        self.tipoReporteServicioDeSoftware = True
        self.tipoReporteResurtidoDeAlmacen = True
        self.tipoReporteSupervision = True
        self.tipoReporteDemostracion = True
        self.tipoReporteTomaDeLectura = True
        wiz = self.env['helpdesk.ticket.reporte'].search([('id', '=', self.id)], order = 'create_date desc', limit = 1 )
        view = self.env.ref('helpdesk_update.view_helpdesk_ticket_reporte')
        return {
                'name': _('Más información'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.ticket.reporte',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }


    def quitarTodos(self):
        self.tipoReporteFalla = False
        self.tipoReporteIncidencia = False
        self.tipoReporteReeincidencia = False
        self.tipoReportePregunta = False
        self.tipoReporteRequerimiento = False
        self.tipoReporteSolicitudDeRefaccion = False
        self.tipoReporteConectividad = False
        self.tipoReporteReincidencias = False
        self.tipoReporteInstalacion = False
        self.tipoReporteMantenimientoPreventivo = False
        self.tipoReporteIMAC = False
        self.tipoReporteProyecto = False
        self.tipoReporteRetiroDeEquipo = False
        self.tipoReporteCambio = False
        self.tipoReporteServicioDeSoftware = False
        self.tipoReporteResurtidoDeAlmacen = False
        self.tipoReporteSupervision = False
        self.tipoReporteDemostracion = False
        self.tipoReporteTomaDeLectura = False
        wiz = self.env['helpdesk.ticket.reporte'].search([('id', '=', self.id)], order = 'create_date desc', limit = 1 )
        view = self.env.ref('helpdesk_update.view_helpdesk_ticket_reporte')
        return {
                'name': _('Más información'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.ticket.reporte',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

    def report(self):
        i = []
        d = []
        m=[]
        bandera = False
        yaEntre = False
        contador = 0
        if self.tipoReporteFalla:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Falla']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteIncidencia:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Incidencia']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteReeincidencia:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Reeincidencia']
            i.append(m)
            contador = contador + 1
        if self.tipoReportePregunta:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Pregunta']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteRequerimiento:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Requerimiento']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteSolicitudDeRefaccion:
            i = ['|'] + i 
            m = ['x_studio_tipo_de_vale', '=', 'Solicitud de refacción']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteConectividad:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Conectividad']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteReincidencias:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Reincidencias']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteInstalacion:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Instalación']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteMantenimientoPreventivo:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Mantenimiento Preventivo']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteIMAC:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'IMAC']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteProyecto:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Proyecto']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteRetiroDeEquipo:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Retiro de equipo']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteCambio:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Cambio']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteServicioDeSoftware:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Servicio de Software']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteResurtidoDeAlmacen:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Resurtido de Almacen']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteSupervision:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Supervisión']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteDemostracion:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Demostración']
            i.append(m)
            contador = contador + 1
        if self.tipoReporteTomaDeLectura:
            i = ['|'] + i
            m = ['x_studio_tipo_de_vale', '=', 'Toma de lectura']
            i.append(m)
            contador = contador + 1
        
        i = ['|'] + i
        m = ['x_studio_tipo_de_vale', '=', False]
        i.append(m)
        contador = contador + 1
        #if self.fechaInicial:
        #    i = ['&'] + i
        #    m = ['create_date', '>=', self.fechaInicial]
        #    i.append(m)
        #if self.fechaFinal:
        #    m = ['create_date', '<=', self.fechaFinal]
        #    i.append(m)

        if contador > 0:
            i.pop(0)

        #_logger.info('3312: filtro reporte: ' + str(i))
        d = self.env['helpdesk.ticket'].search(i, order = 'create_date asc')
        #_logger.info('d: '+ str(len(d)))
        if self.mostrarCerrados or self.mostrarCancelados:
            if self.mostrarCerrados and not self.mostrarCancelados:
                d = d.filtered(lambda x:  x.stage_id.id != 4 )
            if self.mostrarCancelados and not self.mostrarCerrados:
                d = d.filtered(lambda x:  x.stage_id.id != 18 )
            #_logger.info('d 2: '+ str(len(d)))
            #if self.mostrarCerrados and self.mostrarCancelados:
            #    d = self.env['helpdesk.ticket'].search(i, order = 'create_date asc').filtered(lambda x:  x.stage_id.id == 18 and x.stage_id.id == 4 )
        else:
            #_logger.info('entre ultimo caso')
            d = d.filtered(lambda x:  x.stage_id.id != 18 and x.stage_id.id != 4 )
        #_logger.info('d 3: '+ str(len(d)))
        if self.area:
            d = d.filtered(lambda x: (x.team_id.id in self.area.ids) )
        #_logger.info('d 4: '+ str(len(d)))
        if self.clienteRelacion:
            d = d.filtered(lambda x: (x.partner_id.id in self.clienteRelacion.ids) )
        #_logger.info('d 5: '+ str(len(d)))
        #_logger.info('fecha inicial: ' + str(self.fechaInicial))
        #_logger.info('datos: dias final: ' + str(self.fechaFinal + datetime.timedelta(days=2)))
        #d = d.filtered(lambda x: ( datetime.datetime.strptime(x.create_date.strftime('%Y-%m-%d'), '%Y-%m-%d').date() >= self.fechaInicial and datetime.datetime.strptime(x.create_date.strftime('%Y-%m-%d'), '%Y-%m-%d').date() <= self.fechaFinal + datetime.timedelta(days=2) ))
        d = d.filtered(lambda x: ( datetime.datetime.strptime(x.create_date.strftime('%Y-%m-%d'), '%Y-%m-%d').date() >= self.fechaInicial and datetime.datetime.strptime(x.create_date.strftime('%Y-%m-%d'), '%Y-%m-%d').date() <= self.fechaFinal ))
        d = d.filtered(lambda x: len(x.diagnosticos) != 0)
        #_logger.info('datos: d final: ' + str(d))
        #d = self.env['helpdesk.ticket'].search(i, order = 'create_date asc').filtered(lambda x: len(x.x_studio_equipo_por_nmero_de_serie_1) > 0 or len(x.x_studio_equipo_por_nmero_de_serie) > 0)
        #_logger.info('d 6: '+ str(len(d)))
        if len(d) > 0:
            d[0].write({
                            'x_studio_arreglo': str(d.mapped('id'))
                        })
            if self.tipoDeReporte == 'reporteSinContadores':
                return self.env.ref('stock_picking_mass_action.ticket_xlsx').report_action(d[0])
            if self.tipoDeReporte == 'reporteConContadores':
                return self.env.ref('stock_picking_mass_action.ticketContadores_xlsx').report_action(d[0])
        if len(d) == 0:
            raise UserError(_("No hay registros para la selecion actual"))



class helpdesk_reiniciar_contadores_mesa(TransientModel):
    _name = 'helpdesk.contadores.reiniciar.mesa'
    _description = 'helpdesk permite reiniciar los contadores actuales en mesa de ayuda.'

    ticket_id = fields.Many2one(
                                    "helpdesk.ticket",
                                    string = 'Ticket'
                                )
    serieSeleccionada = fields.Text(
                            string = 'Serie seleccionada',
                            compute = "_compute_serieSeleccionada"
                        )
    tipoEquipo = fields.Selection(
                                    [('Color','Color'),('B/N','B/N')],
                                    string = 'Equipo color o B/N',
                                    compute = '_compute_equipoSeleccionado'
                                )
    contadorMonoActual = fields.Integer(
                                            string = 'Contador Monocromatico actual',
                                            store = False,
                                            compute = '_compute_contador_bn_actual'
                                        )
    contadorColorActual = fields.Integer(
                                            string = 'Contador Color actual',
                                            store = False,
                                            compute = '_compute_contador_color_actual'
                                        )
    contadorMonoActualizado = fields.Integer(
                                                string = 'Contador Monocromatico nuevo',
                                                store = True,
                                                default = 0
                                            )
    contadorColorActualizado = fields.Integer(
                                                string = 'Contador Color nuevo',
                                                store = True,
                                                default = 0
                                            )

    evidencia = fields.Many2many(
                                    'ir.attachment',
                                    string = "Evidencias"
                                )
    comentario = fields.Text(
                                string = 'Comentario'
                            )
    check = fields.Boolean(
                                string = 'Mostrar en reporte',
                                default = False
                            )
    estado = fields.Char(
                            string = 'Estado', 
                            compute = "_compute_estadoTicket"
                        )
    textoInformativo = fields.Text(
                                        string = ' ',
                                        default = ' ',
                                        store = False,
                                        compute = '_compute_textoInformativo'
                                    )

    def _compute_equipoSeleccionado(self):
        for record in self:
            if record.ticket_id.x_studio_equipo_por_nmero_de_serie and record.ticket_id.x_studio_equipo_por_nmero_de_serie.x_studio_color_bn:
                record.tipoEquipo = record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_color_bn

    def _compute_serieSeleccionada(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.serieSeleccionada = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name

    def _compute_estadoTicket(self):
        if self.ticket_id:
            self.estado = self.ticket_id.stage_id.name

    def _compute_contador_bn_actual(self):
        for record in self:
            fuente = 'stock.production.lot'
            ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
            if ultimoDcaStockProductionLot:
                record.contadorMonoActual = ultimoDcaStockProductionLot.contadorMono
            #if record.ticket_id.x_studio_equipo_por_nmero_de_serie:
            #    record.contadorMonoActual = record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_contador_bn_mesa
            

    def _compute_contador_color_actual(self):
        for record in self:
            fuente = 'stock.production.lot'
            ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
            if ultimoDcaStockProductionLot:
                record.contadorMonoActual = ultimoDcaStockProductionLot.contadorColor
            #if record.ticket_id.x_studio_equipo_por_nmero_de_serie:
            #    record.contadorColorActual = record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_contador_color_mesa

    def _compute_textoInformativo(self):
        q = 'stock.production.lot'
        ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        q = 'dcas.dcas'
        ultimoDcaDcasDcas = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        q = 'helpdesk.ticket'
        ultimoDcaHelpdeskTicket = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        q = 'tfs.tfs'
        ultimoDcaTfsTfs = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        #self.textoInformativo = 'ultimoDcaStockProductionLot: ' + str(ultimoDcaStockProductionLot.id) + '\nultimoDcaDcasDcas: ' + str(ultimoDcaDcasDcas.id) + '\nultimoDcaHelpdeskTicket: ' + str(ultimoDcaHelpdeskTicket.id) + '\nultimoDcaTfsTfs: ' + str(ultimoDcaTfsTfs.id) + '\n\n'

        for c in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            comentarioDeReinicio = """
                    <div class='alert alert-info' role='alert'>
                        <h4 class="alert-heading">Reinicio de contadores por realizar !!!</h4>

                        <p>Se reiniciara el contador de la serie <strong>""" + str(c.name) + """</strong> por medio del ticket <strong>""" + str(self.ticket_id.id) + """</strong> y con los siguientes detalles: </p>
                        <br/>
                        <div class='row'>
                            <div class='col-sm-3'>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>Realizado el día:</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>""" + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ) + """</p>
                                    </div>
                                </div>
                            </div>

                            <div class='col-sm-3'>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>Realizado por:</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>""" + self.env.user.name + """</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class='col-sm-3'>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>Contador anterior B/N:</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>""" + str(ultimoDcaStockProductionLot.contadorMono) + """</p>
                                    </div>
                                </div>
                            </div>

                            <div class='col-sm-3'>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>Contador anterior Color:</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>""" + str(ultimoDcaStockProductionLot.contadorColor) + """</p>
                                    </div>
                                </div>
                            </div>


                        </div>
                        
                    </div>
                    """

        self.textoInformativo = comentarioDeReinicio


    def comentarioDeReinicio(self, tipoEquipo, serie, ticket_id, fecha, usuario, contadorAnteriorNegro, contadorAnteriorColor):
        comentarioDeReinicio = """ """
        if tipoEquipo == 'B/N':
            comentarioDeReinicio = """
                                            <div class='alert alert-info' role='alert'>
                                                <h4 class="alert-heading">Reinicio de contadores realizado !!!</h4>

                                                <p>Se reinicio el contador de la serie <strong>""" + serie + """</strong> por medio del ticket <strong>""" + ticket_id + """</strong> y con los siguientes detalles: </p>
                                                <br/>
                                                <div class='row'>
                                                    <div class='col-sm-4'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Realizado el día:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + fecha + """</p>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class='col-sm-4'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Realizado por:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + usuario + """</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class='col-sm-4'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Contador anterior B/N:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + contadorAnteriorNegro + """</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                
                                            </div>
                                            """
        elif tipoEquipo == 'Color':
            comentarioDeReinicio = """
                                            <div class='alert alert-info' role='alert'>
                                                <h4 class="alert-heading">Reinicio de contadores realizado !!!</h4>

                                                <p>Se reinicio el contador de la serie <strong>""" + serie + """</strong> por medio del ticket <strong>""" + ticket_id + """</strong> y con los siguientes detalles: </p>
                                                <br/>
                                                <div class='row'>
                                                    <div class='col-sm-3'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Realizado el día:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + fecha + """</p>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class='col-sm-3'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Realizado por:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + usuario + """</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class='col-sm-3'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Contador anterior B/N:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + contadorAnteriorNegro + """</p>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class='col-sm-3'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Contador anterior Color:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + contadorAnteriorColor + """</p>
                                                            </div>
                                                        </div>
                                                    </div>


                                                </div>
                                                
                                            </div>
                                            """
        return comentarioDeReinicio


    def reiniciarContadores(self):
        for c in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            q = 'stock.production.lot'
            if str(c.x_studio_color_bn) == 'B/N':
                #if int(self.contadorBNActual) >= int(c.x_studio_contador_bn):
                negrot = c.x_studio_contador_bn_mesa
                colort = c.x_studio_contador_color_mesa
                negroMesa = 0
                colorMesa = 0
                comentarioDeReinicio = """ """

                rr = ''
                dcaFuente = ''
                mesaFuente = ''
                tfsFuente = ''
                #Creando dca para mesa stock.production.lot
                ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaStockProductionLot:
                    negrot = ultimoDcaStockProductionLot.contadorMono
                    negroMesa = ultimoDcaStockProductionLot.contadorMono
                    rr = self.env['dcas.dcas'].create({
                                                        'x_studio_cliente': ultimoDcaStockProductionLot.x_studio_cliente,
                                                        'serie': c.id,
                                                        'x_studio_color_o_bn': ultimoDcaStockProductionLot.x_studio_color_o_bn,
                                                        'x_studio_cartuchonefro': ultimoDcaStockProductionLot.x_studio_cartuchonefro.id,
                                                        'x_studio_rendimiento_negro': ultimoDcaStockProductionLot.x_studio_rendimiento_negro,
                                                        'x_studio_cartucho_amarillo': ultimoDcaStockProductionLot.x_studio_cartucho_amarillo.id,
                                                        'x_studio_rendimientoa': ultimoDcaStockProductionLot.x_studio_rendimientoa,
                                                        'x_studio_cartucho_cian_1': ultimoDcaStockProductionLot.x_studio_cartucho_cian_1.id,
                                                        'x_studio_rendimientoc': ultimoDcaStockProductionLot.x_studio_rendimientoc,
                                                        'x_studio_cartucho_magenta': ultimoDcaStockProductionLot.x_studio_cartucho_magenta.id,
                                                        'x_studio_rendimientom': ultimoDcaStockProductionLot.x_studio_rendimientom,
                                                        'x_studio_fecha': ultimoDcaStockProductionLot.x_studio_fecha,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,

                                                        'contadorColor': 0,
                                                        'x_studio_contador_color_anterior': 0,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,

                                                        'paginasProcesadasBN': ultimoDcaStockProductionLot.paginasProcesadasBN,
                                                        'porcentajeNegro': ultimoDcaStockProductionLot.porcentajeNegro,
                                                        'porcentajeAmarillo': ultimoDcaStockProductionLot.porcentajeAmarillo,
                                                        'porcentajeCian': ultimoDcaStockProductionLot.porcentajeCian,
                                                        'porcentajeMagenta': ultimoDcaStockProductionLot.porcentajeMagenta,
                                                        'x_studio_rendimiento': ultimoDcaStockProductionLot.x_studio_rendimiento,
                                                        'x_studio_rendimiento_color': ultimoDcaStockProductionLot.x_studio_rendimiento_color,
                                                        'x_studio_toner_negro': ultimoDcaStockProductionLot.x_studio_toner_negro,
                                                        'x_studio_toner_cian': ultimoDcaStockProductionLot.x_studio_toner_cian,
                                                        'x_studio_toner_magenta': ultimoDcaStockProductionLot.x_studio_toner_magenta,
                                                        'x_studio_toner_amarillo': ultimoDcaStockProductionLot.x_studio_toner_amarillo,
                                                        'nivelCA': ultimoDcaStockProductionLot.nivelCA,
                                                        'nivelMA': ultimoDcaStockProductionLot.nivelMA,
                                                        'nivelNA': ultimoDcaStockProductionLot.nivelNA,
                                                        'nivelAA': ultimoDcaStockProductionLot.nivelAA,
                                                        'contadorAnteriorNegro': ultimoDcaStockProductionLot.contadorAnteriorNegro,
                                                        'contadorAnteriorAmarillo': ultimoDcaStockProductionLot.contadorAnteriorAmarillo,
                                                        'contadorAnteriorMagenta': ultimoDcaStockProductionLot.contadorAnteriorMagenta,
                                                        'contadorAnteriorCian': ultimoDcaStockProductionLot.contadorAnteriorCian,
                                                        'paginasProcesadasA': ultimoDcaStockProductionLot.paginasProcesadasA,
                                                        'paginasProcesadasC': ultimoDcaStockProductionLot.paginasProcesadasC,
                                                        'paginasProcesadasM': ultimoDcaStockProductionLot.paginasProcesadasM,
                                                        'renM': ultimoDcaStockProductionLot.renM,
                                                        'renA': ultimoDcaStockProductionLot.renA,
                                                        'renC': ultimoDcaStockProductionLot.renC,
                                                        'reinicioDeContador': True
                                                  })
                else:
                    negrot = 0
                    rr = self.env['dcas.dcas'].create({
                                                        
                                                        'serie': c.id,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,
                                                        'contadorColor': 0,
                                                        'x_studio_contador_color_anterior': 0,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'reinicioDeContador': True
                                                  })
                tipoEquipoTemp = str(c.x_studio_color_bn)
                nombreSerieTemp = c.name
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(rr.create_date)
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(negrot)
                contadorAnteriorColorTemp = str(0)
                #comentarioDeReinicio(tipoEquipo, serie, ticket_id, fecha, usuario, contadorAnteriorNegro, contadorAnteriorColor)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                rr.comentarioDeReinicio = comentarioDeReinicio
                q = 'dcas.dcas'
                ultimoDcaDcasDcas = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaDcasDcas:
                    negrot = ultimoDcaDcasDcas.contadorMono
                    dcaFuente = self.env['dcas.dcas'].create({
                                                        'x_studio_cliente': ultimoDcaDcasDcas.x_studio_cliente,
                                                        'serie': c.id,
                                                        'x_studio_color_o_bn': ultimoDcaDcasDcas.x_studio_color_o_bn,
                                                        'x_studio_cartuchonefro': ultimoDcaDcasDcas.x_studio_cartuchonefro.id,
                                                        'x_studio_rendimiento_negro': ultimoDcaDcasDcas.x_studio_rendimiento_negro,
                                                        'x_studio_cartucho_amarillo': ultimoDcaDcasDcas.x_studio_cartucho_amarillo.id,
                                                        'x_studio_rendimientoa': ultimoDcaDcasDcas.x_studio_rendimientoa,
                                                        'x_studio_cartucho_cian_1': ultimoDcaDcasDcas.x_studio_cartucho_cian_1.id,
                                                        'x_studio_rendimientoc': ultimoDcaDcasDcas.x_studio_rendimientoc,
                                                        'x_studio_cartucho_magenta': ultimoDcaDcasDcas.x_studio_cartucho_magenta.id,
                                                        'x_studio_rendimientom': ultimoDcaDcasDcas.x_studio_rendimientom,
                                                        'x_studio_fecha': ultimoDcaDcasDcas.x_studio_fecha,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,

                                                        'contadorColor': 0,
                                                        'x_studio_contador_color_anterior': 0,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,

                                                        'paginasProcesadasBN': ultimoDcaDcasDcas.paginasProcesadasBN,
                                                        'porcentajeNegro': ultimoDcaDcasDcas.porcentajeNegro,
                                                        'porcentajeAmarillo': ultimoDcaDcasDcas.porcentajeAmarillo,
                                                        'porcentajeCian': ultimoDcaDcasDcas.porcentajeCian,
                                                        'porcentajeMagenta': ultimoDcaDcasDcas.porcentajeMagenta,
                                                        'x_studio_rendimiento': ultimoDcaDcasDcas.x_studio_rendimiento,
                                                        'x_studio_rendimiento_color': ultimoDcaDcasDcas.x_studio_rendimiento_color,
                                                        'x_studio_toner_negro': ultimoDcaDcasDcas.x_studio_toner_negro,
                                                        'x_studio_toner_cian': ultimoDcaDcasDcas.x_studio_toner_cian,
                                                        'x_studio_toner_magenta': ultimoDcaDcasDcas.x_studio_toner_magenta,
                                                        'x_studio_toner_amarillo': ultimoDcaDcasDcas.x_studio_toner_amarillo,
                                                        'nivelCA': ultimoDcaDcasDcas.nivelCA,
                                                        'nivelMA': ultimoDcaDcasDcas.nivelMA,
                                                        'nivelNA': ultimoDcaDcasDcas.nivelNA,
                                                        'nivelAA': ultimoDcaDcasDcas.nivelAA,
                                                        'contadorAnteriorNegro': ultimoDcaDcasDcas.contadorAnteriorNegro,
                                                        'contadorAnteriorAmarillo': ultimoDcaDcasDcas.contadorAnteriorAmarillo,
                                                        'contadorAnteriorMagenta': ultimoDcaDcasDcas.contadorAnteriorMagenta,
                                                        'contadorAnteriorCian': ultimoDcaDcasDcas.contadorAnteriorCian,
                                                        'paginasProcesadasA': ultimoDcaDcasDcas.paginasProcesadasA,
                                                        'paginasProcesadasC': ultimoDcaDcasDcas.paginasProcesadasC,
                                                        'paginasProcesadasM': ultimoDcaDcasDcas.paginasProcesadasM,
                                                        'renM': ultimoDcaDcasDcas.renM,
                                                        'renA': ultimoDcaDcasDcas.renA,
                                                        'renC': ultimoDcaDcasDcas.renC,

                                                        'reinicioDeContador': True
                                                  })
                else:
                    negrot = 0
                    dcaFuente = self.env['dcas.dcas'].create({
                                                        
                                                        'serie': c.id,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,
                                                        'contadorColor': 0,
                                                        'x_studio_contador_color_anterior': 0,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'reinicioDeContador': True
                                                  })
                tipoEquipoTemp = str(c.x_studio_color_bn)
                nombreSerieTemp = c.name
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(dcaFuente.create_date)
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(negrot)
                contadorAnteriorColorTemp = str(0)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                dcaFuente.comentarioDeReinicio = comentarioDeReinicio
                q = 'helpdesk.ticket'
                ultimoDcaHelpdeskTicket = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaHelpdeskTicket:
                    negrot = ultimoDcaHelpdeskTicket.contadorMono
                    mesaFuente = self.env['dcas.dcas'].create({
                                                        #'serie': c.id,
                                                        #'contadorMono' : self.contadorBNActual,
                                                        #'x_studio_contador_color_anterior': colort,
                                                        #'contadorColor': self.contadorColorMesa
                                                        #'x_studio_tickett': self.ticket_id.id,
                                                        #'x_studio_contador_mono_anterior_1': negrot,
                                                        #'x_studio_tiquete': self.ticket_id.id,
                                                        #'x_studio_tickett': self.ticket_id.id,
                                                        #'fuente': q,

                                                        'x_studio_cliente': ultimoDcaHelpdeskTicket.x_studio_cliente,
                                                        'serie': c.id,
                                                        'x_studio_color_o_bn': ultimoDcaHelpdeskTicket.x_studio_color_o_bn,
                                                        'x_studio_cartuchonefro': ultimoDcaHelpdeskTicket.x_studio_cartuchonefro.id,
                                                        'x_studio_rendimiento_negro': ultimoDcaHelpdeskTicket.x_studio_rendimiento_negro,
                                                        'x_studio_cartucho_amarillo': ultimoDcaHelpdeskTicket.x_studio_cartucho_amarillo.id,
                                                        'x_studio_rendimientoa': ultimoDcaHelpdeskTicket.x_studio_rendimientoa,
                                                        'x_studio_cartucho_cian_1': ultimoDcaHelpdeskTicket.x_studio_cartucho_cian_1.id,
                                                        'x_studio_rendimientoc': ultimoDcaHelpdeskTicket.x_studio_rendimientoc,
                                                        'x_studio_cartucho_magenta': ultimoDcaHelpdeskTicket.x_studio_cartucho_magenta.id,
                                                        'x_studio_rendimientom': ultimoDcaHelpdeskTicket.x_studio_rendimientom,
                                                        'x_studio_fecha': ultimoDcaHelpdeskTicket.x_studio_fecha,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,

                                                        'contadorColor': 0,
                                                        'x_studio_contador_color_anterior': 0,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,

                                                        'paginasProcesadasBN': ultimoDcaHelpdeskTicket.paginasProcesadasBN,
                                                        'porcentajeNegro': ultimoDcaHelpdeskTicket.porcentajeNegro,
                                                        'porcentajeAmarillo': ultimoDcaHelpdeskTicket.porcentajeAmarillo,
                                                        'porcentajeCian': ultimoDcaHelpdeskTicket.porcentajeCian,
                                                        'porcentajeMagenta': ultimoDcaHelpdeskTicket.porcentajeMagenta,
                                                        'x_studio_rendimiento': ultimoDcaHelpdeskTicket.x_studio_rendimiento,
                                                        'x_studio_rendimiento_color': ultimoDcaHelpdeskTicket.x_studio_rendimiento_color,
                                                        'x_studio_toner_negro': ultimoDcaHelpdeskTicket.x_studio_toner_negro,
                                                        'x_studio_toner_cian': ultimoDcaHelpdeskTicket.x_studio_toner_cian,
                                                        'x_studio_toner_magenta': ultimoDcaHelpdeskTicket.x_studio_toner_magenta,
                                                        'x_studio_toner_amarillo': ultimoDcaHelpdeskTicket.x_studio_toner_amarillo,
                                                        'nivelCA': ultimoDcaHelpdeskTicket.nivelCA,
                                                        'nivelMA': ultimoDcaHelpdeskTicket.nivelMA,
                                                        'nivelNA': ultimoDcaHelpdeskTicket.nivelNA,
                                                        'nivelAA': ultimoDcaHelpdeskTicket.nivelAA,
                                                        'contadorAnteriorNegro': ultimoDcaHelpdeskTicket.contadorAnteriorNegro,
                                                        'contadorAnteriorAmarillo': ultimoDcaHelpdeskTicket.contadorAnteriorAmarillo,
                                                        'contadorAnteriorMagenta': ultimoDcaHelpdeskTicket.contadorAnteriorMagenta,
                                                        'contadorAnteriorCian': ultimoDcaHelpdeskTicket.contadorAnteriorCian,
                                                        'paginasProcesadasA': ultimoDcaHelpdeskTicket.paginasProcesadasA,
                                                        'paginasProcesadasC': ultimoDcaHelpdeskTicket.paginasProcesadasC,
                                                        'paginasProcesadasM': ultimoDcaHelpdeskTicket.paginasProcesadasM,
                                                        'renM': ultimoDcaHelpdeskTicket.renM,
                                                        'renA': ultimoDcaHelpdeskTicket.renA,
                                                        'renC': ultimoDcaHelpdeskTicket.renC,
                                                        'reinicioDeContador': True
                                                  })
                else:
                    negrot = 0
                    mesaFuente = self.env['dcas.dcas'].create({
                                                        
                                                        'serie': c.id,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,
                                                        'contadorColor': 0,
                                                        'x_studio_contador_color_anterior': 0,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'reinicioDeContador': True
                                                  })
                tipoEquipoTemp = str(c.x_studio_color_bn)
                nombreSerieTemp = c.name
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(mesaFuente.create_date)
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(negrot)
                contadorAnteriorColorTemp = str(0)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                mesaFuente.comentarioDeReinicio = comentarioDeReinicio
                q = 'tfs.tfs'
                ultimoDcaTfsTfs = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaTfsTfs:
                    negrot = ultimoDcaTfsTfs.contadorMono
                    tfsFuente = self.env['dcas.dcas'].create({
                                                        #'serie': c.id,
                                                        #'contadorMono' : self.contadorBNActual,
                                                        #'x_studio_contador_color_anterior': colort,
                                                        #'contadorColor': self.contadorColorMesa
                                                        #'x_studio_tickett': self.ticket_id.id,
                                                        #'x_studio_contador_mono_anterior_1': negrot,
                                                        #'x_studio_tiquete': self.ticket_id.id,
                                                        #'x_studio_tickett': self.ticket_id.id,
                                                        #'fuente': q,

                                                        'x_studio_cliente': ultimoDcaTfsTfs.x_studio_cliente,
                                                        'serie': c.id,
                                                        'x_studio_color_o_bn': ultimoDcaTfsTfs.x_studio_color_o_bn,
                                                        'x_studio_cartuchonefro': ultimoDcaTfsTfs.x_studio_cartuchonefro.id,
                                                        'x_studio_rendimiento_negro': ultimoDcaTfsTfs.x_studio_rendimiento_negro,
                                                        'x_studio_cartucho_amarillo': ultimoDcaTfsTfs.x_studio_cartucho_amarillo.id,
                                                        'x_studio_rendimientoa': ultimoDcaTfsTfs.x_studio_rendimientoa,
                                                        'x_studio_cartucho_cian_1': ultimoDcaTfsTfs.x_studio_cartucho_cian_1.id,
                                                        'x_studio_rendimientoc': ultimoDcaTfsTfs.x_studio_rendimientoc,
                                                        'x_studio_cartucho_magenta': ultimoDcaTfsTfs.x_studio_cartucho_magenta.id,
                                                        'x_studio_rendimientom': ultimoDcaTfsTfs.x_studio_rendimientom,
                                                        'x_studio_fecha': ultimoDcaTfsTfs.x_studio_fecha,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,

                                                        'contadorColor': 0,
                                                        'x_studio_contador_color_anterior': 0,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,

                                                        'paginasProcesadasBN': ultimoDcaTfsTfs.paginasProcesadasBN,
                                                        'porcentajeNegro': ultimoDcaTfsTfs.porcentajeNegro,
                                                        'porcentajeAmarillo': ultimoDcaTfsTfs.porcentajeAmarillo,
                                                        'porcentajeCian': ultimoDcaTfsTfs.porcentajeCian,
                                                        'porcentajeMagenta': ultimoDcaTfsTfs.porcentajeMagenta,
                                                        'x_studio_rendimiento': ultimoDcaTfsTfs.x_studio_rendimiento,
                                                        'x_studio_rendimiento_color': ultimoDcaTfsTfs.x_studio_rendimiento_color,
                                                        'x_studio_toner_negro': ultimoDcaTfsTfs.x_studio_toner_negro,
                                                        'x_studio_toner_cian': ultimoDcaTfsTfs.x_studio_toner_cian,
                                                        'x_studio_toner_magenta': ultimoDcaTfsTfs.x_studio_toner_magenta,
                                                        'x_studio_toner_amarillo': ultimoDcaTfsTfs.x_studio_toner_amarillo,
                                                        'nivelCA': ultimoDcaTfsTfs.nivelCA,
                                                        'nivelMA': ultimoDcaTfsTfs.nivelMA,
                                                        'nivelNA': ultimoDcaTfsTfs.nivelNA,
                                                        'nivelAA': ultimoDcaTfsTfs.nivelAA,
                                                        'contadorAnteriorNegro': ultimoDcaTfsTfs.contadorAnteriorNegro,
                                                        'contadorAnteriorAmarillo': ultimoDcaTfsTfs.contadorAnteriorAmarillo,
                                                        'contadorAnteriorMagenta': ultimoDcaTfsTfs.contadorAnteriorMagenta,
                                                        'contadorAnteriorCian': ultimoDcaTfsTfs.contadorAnteriorCian,
                                                        'paginasProcesadasA': ultimoDcaTfsTfs.paginasProcesadasA,
                                                        'paginasProcesadasC': ultimoDcaTfsTfs.paginasProcesadasC,
                                                        'paginasProcesadasM': ultimoDcaTfsTfs.paginasProcesadasM,
                                                        'renM': ultimoDcaTfsTfs.renM,
                                                        'renA': ultimoDcaTfsTfs.renA,
                                                        'renC': ultimoDcaTfsTfs.renC,
                                                        'reinicioDeContador': True
                                                  })
                else:
                    negrot = 0
                    tfsFuente = self.env['dcas.dcas'].create({
                                                        
                                                        'serie': c.id,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,
                                                        'contadorColor': 0,
                                                        'x_studio_contador_color_anterior': 0,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'reinicioDeContador': True
                                                  })
                tipoEquipoTemp = str(c.x_studio_color_bn)
                nombreSerieTemp = c.name
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(tfsFuente.create_date)
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(negrot)
                contadorAnteriorColorTemp = str(0)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                tfsFuente.comentarioDeReinicio = comentarioDeReinicio
                
                self.env['helpdesk.diagnostico'].create({
                                                            'ticketRelacion':self.ticket_id.x_studio_id_ticket,
                                                            'estadoTicket': 'Reinicio de contadores en el estado ' + self.estado,
                                                            'evidencia': [(6,0,self.evidencia.ids)],
                                                            'mostrarComentario': self.check,
                                                            'write_uid':  self.env.user.name,
                                                            'comentario': 'Reinicio de contadores.\n Contador BN anterior: ' + str(negroMesa) + '\nContador BN capturado: ' + str(self.contadorMonoActualizado) + '\n\n' + self.comentario,
                                                            'creadoPorSistema': True
                                                        })
                self.ticket_id.write({'contadores_anteriores': '</br>Equipo BN o Color: ' + str(self.tipoEquipo) + ' </br></br>Contador BN: ' + str(self.contadorMonoActualizado) + '</br></br>Contador Color: ' + str(self.contadorColorActualizado)
                                    , 'x_studio_contador_bn': int(negroMesa)
                                    , 'x_studio_contador_bn_a_capturar': int(self.contadorMonoActualizado)
                                    , 'x_studio_contador_color': 0
                                    , 'x_studio_contador_color_a_capturar': 0
                                    })
                self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
                mensajeTitulo = "Contador reiniciado!!!"
                mensajeCuerpo = "Se reinicio el contador del equipo " + str(c.name) + "."
                wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                        'context': self.env.context,
                        }
                #else:
                #    raise exceptions.ValidationError("Contador Monocromatico Menor")                                   
            if str(c.x_studio_color_bn) != 'B/N':
                #if int(self.contadorColorMesa) >= int(c.x_studio_contador_color) and int(self.contadorBNActual) >= int(c.x_studio_contador_bn):                      
                if self.ticket_id.team_id.id == 8:
                    negrot = c.x_studio_contador_bn
                    colort = c.x_studio_contador_color
                else:
                    negrot = c.x_studio_contador_bn_mesa
                    colort = c.x_studio_contador_color_mesa

                negroMesa = 0
                colorMesa = 0
                comentarioDeReinicio = """ """

                rr = ''
                dcaFuente = ''
                mesaFuente = ''
                tfsFuente = ''

                ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaStockProductionLot:
                    negrot = ultimoDcaStockProductionLot.contadorMono
                    colort = ultimoDcaStockProductionLot.contadorColor
                    negroMesa = ultimoDcaStockProductionLot.contadorMono
                    colorMesa = ultimoDcaStockProductionLot.contadorColor
                    rr = self.env['dcas.dcas'].create({
                                                        'x_studio_cliente': ultimoDcaStockProductionLot.x_studio_cliente,
                                                        'serie': c.id,
                                                        'x_studio_color_o_bn': ultimoDcaStockProductionLot.x_studio_color_o_bn,
                                                        'x_studio_cartuchonefro': ultimoDcaStockProductionLot.x_studio_cartuchonefro.id,
                                                        'x_studio_rendimiento_negro': ultimoDcaStockProductionLot.x_studio_rendimiento_negro,
                                                        'x_studio_cartucho_amarillo': ultimoDcaStockProductionLot.x_studio_cartucho_amarillo.id,
                                                        'x_studio_rendimientoa': ultimoDcaStockProductionLot.x_studio_rendimientoa,
                                                        'x_studio_cartucho_cian_1': ultimoDcaStockProductionLot.x_studio_cartucho_cian_1.id,
                                                        'x_studio_rendimientoc': ultimoDcaStockProductionLot.x_studio_rendimientoc,
                                                        'x_studio_cartucho_magenta': ultimoDcaStockProductionLot.x_studio_cartucho_magenta.id,
                                                        'x_studio_rendimientom': ultimoDcaStockProductionLot.x_studio_rendimientom,
                                                        'x_studio_fecha': ultimoDcaStockProductionLot.x_studio_fecha,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,

                                                        'contadorColor': self.contadorColorActualizado,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,

                                                        'paginasProcesadasBN': ultimoDcaStockProductionLot.paginasProcesadasBN,
                                                        'porcentajeNegro': ultimoDcaStockProductionLot.porcentajeNegro,
                                                        'porcentajeAmarillo': ultimoDcaStockProductionLot.porcentajeAmarillo,
                                                        'porcentajeCian': ultimoDcaStockProductionLot.porcentajeCian,
                                                        'porcentajeMagenta': ultimoDcaStockProductionLot.porcentajeMagenta,
                                                        'x_studio_rendimiento': ultimoDcaStockProductionLot.x_studio_rendimiento,
                                                        'x_studio_rendimiento_color': ultimoDcaStockProductionLot.x_studio_rendimiento_color,
                                                        'x_studio_toner_negro': ultimoDcaStockProductionLot.x_studio_toner_negro,
                                                        'x_studio_toner_cian': ultimoDcaStockProductionLot.x_studio_toner_cian,
                                                        'x_studio_toner_magenta': ultimoDcaStockProductionLot.x_studio_toner_magenta,
                                                        'x_studio_toner_amarillo': ultimoDcaStockProductionLot.x_studio_toner_amarillo,
                                                        'nivelCA': ultimoDcaStockProductionLot.nivelCA,
                                                        'nivelMA': ultimoDcaStockProductionLot.nivelMA,
                                                        'nivelNA': ultimoDcaStockProductionLot.nivelNA,
                                                        'nivelAA': ultimoDcaStockProductionLot.nivelAA,
                                                        'contadorAnteriorNegro': ultimoDcaStockProductionLot.contadorAnteriorNegro,
                                                        'contadorAnteriorAmarillo': ultimoDcaStockProductionLot.contadorAnteriorAmarillo,
                                                        'contadorAnteriorMagenta': ultimoDcaStockProductionLot.contadorAnteriorMagenta,
                                                        'contadorAnteriorCian': ultimoDcaStockProductionLot.contadorAnteriorCian,
                                                        'paginasProcesadasA': ultimoDcaStockProductionLot.paginasProcesadasA,
                                                        'paginasProcesadasC': ultimoDcaStockProductionLot.paginasProcesadasC,
                                                        'paginasProcesadasM': ultimoDcaStockProductionLot.paginasProcesadasM,
                                                        'renM': ultimoDcaStockProductionLot.renM,
                                                        'renA': ultimoDcaStockProductionLot.renA,
                                                        'renC': ultimoDcaStockProductionLot.renC,

                                                        'reinicioDeContador': True
                                                  })
                else:
                    negrot = 0
                    colort = 0
                    rr = self.env['dcas.dcas'].create({
                                                        'serie': c.id,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,
                                                        'contadorColor': self.contadorColorActualizado,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'reinicioDeContador': True
                                                  })
                tipoEquipoTemp = str(c.x_studio_color_bn)
                nombreSerieTemp = c.name
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(rr.create_date)
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(negrot)
                contadorAnteriorColorTemp = str(colort)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                rr.comentarioDeReinicio = comentarioDeReinicio
                q = 'dcas.dcas'
                ultimoDcaDcasDcas = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaDcasDcas:
                    negrot = ultimoDcaDcasDcas.contadorMono
                    colort = ultimoDcaDcasDcas.contadorColor
                    dcaFuente = self.env['dcas.dcas'].create({
                                                        'x_studio_cliente': ultimoDcaDcasDcas.x_studio_cliente,
                                                        'serie': c.id,
                                                        'x_studio_color_o_bn': ultimoDcaDcasDcas.x_studio_color_o_bn,
                                                        'x_studio_cartuchonefro': ultimoDcaDcasDcas.x_studio_cartuchonefro.id,
                                                        'x_studio_rendimiento_negro': ultimoDcaDcasDcas.x_studio_rendimiento_negro,
                                                        'x_studio_cartucho_amarillo': ultimoDcaDcasDcas.x_studio_cartucho_amarillo.id,
                                                        'x_studio_rendimientoa': ultimoDcaDcasDcas.x_studio_rendimientoa,
                                                        'x_studio_cartucho_cian_1': ultimoDcaDcasDcas.x_studio_cartucho_cian_1.id,
                                                        'x_studio_rendimientoc': ultimoDcaDcasDcas.x_studio_rendimientoc,
                                                        'x_studio_cartucho_magenta': ultimoDcaDcasDcas.x_studio_cartucho_magenta.id,
                                                        'x_studio_rendimientom': ultimoDcaDcasDcas.x_studio_rendimientom,
                                                        'x_studio_fecha': ultimoDcaDcasDcas.x_studio_fecha,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,

                                                        'contadorColor': self.contadorColorActualizado,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,

                                                        'paginasProcesadasBN': ultimoDcaDcasDcas.paginasProcesadasBN,
                                                        'porcentajeNegro': ultimoDcaDcasDcas.porcentajeNegro,
                                                        'porcentajeAmarillo': ultimoDcaDcasDcas.porcentajeAmarillo,
                                                        'porcentajeCian': ultimoDcaDcasDcas.porcentajeCian,
                                                        'porcentajeMagenta': ultimoDcaDcasDcas.porcentajeMagenta,
                                                        'x_studio_rendimiento': ultimoDcaDcasDcas.x_studio_rendimiento,
                                                        'x_studio_rendimiento_color': ultimoDcaDcasDcas.x_studio_rendimiento_color,
                                                        'x_studio_toner_negro': ultimoDcaDcasDcas.x_studio_toner_negro,
                                                        'x_studio_toner_cian': ultimoDcaDcasDcas.x_studio_toner_cian,
                                                        'x_studio_toner_magenta': ultimoDcaDcasDcas.x_studio_toner_magenta,
                                                        'x_studio_toner_amarillo': ultimoDcaDcasDcas.x_studio_toner_amarillo,
                                                        'nivelCA': ultimoDcaDcasDcas.nivelCA,
                                                        'nivelMA': ultimoDcaDcasDcas.nivelMA,
                                                        'nivelNA': ultimoDcaDcasDcas.nivelNA,
                                                        'nivelAA': ultimoDcaDcasDcas.nivelAA,
                                                        'contadorAnteriorNegro': ultimoDcaDcasDcas.contadorAnteriorNegro,
                                                        'contadorAnteriorAmarillo': ultimoDcaDcasDcas.contadorAnteriorAmarillo,
                                                        'contadorAnteriorMagenta': ultimoDcaDcasDcas.contadorAnteriorMagenta,
                                                        'contadorAnteriorCian': ultimoDcaDcasDcas.contadorAnteriorCian,
                                                        'paginasProcesadasA': ultimoDcaDcasDcas.paginasProcesadasA,
                                                        'paginasProcesadasC': ultimoDcaDcasDcas.paginasProcesadasC,
                                                        'paginasProcesadasM': ultimoDcaDcasDcas.paginasProcesadasM,
                                                        'renM': ultimoDcaDcasDcas.renM,
                                                        'renA': ultimoDcaDcasDcas.renA,
                                                        'renC': ultimoDcaDcasDcas.renC,

                                                        'reinicioDeContador': True
                                                  })
                else:
                    negrot = 0
                    colort = 0
                    dcaFuente = self.env['dcas.dcas'].create({
                                                        'serie': c.id,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,
                                                        'contadorColor': self.contadorColorActualizado,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'reinicioDeContador': True
                                                  })
                tipoEquipoTemp = str(c.x_studio_color_bn)
                nombreSerieTemp = c.name
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(dcaFuente.create_date)
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(negrot)
                contadorAnteriorColorTemp = str(colort)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                dcaFuente.comentarioDeReinicio = comentarioDeReinicio
                q = 'helpdesk.ticket'
                ultimoDcaHelpdeskTicket = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaHelpdeskTicket:
                    negrot = ultimoDcaHelpdeskTicket.contadorMono
                    colort = ultimoDcaHelpdeskTicket.contadorColor
                    mesaFuente = self.env['dcas.dcas'].create({
                                                        'x_studio_cliente': ultimoDcaHelpdeskTicket.x_studio_cliente,
                                                        'serie': c.id,
                                                        'x_studio_color_o_bn': ultimoDcaHelpdeskTicket.x_studio_color_o_bn,
                                                        'x_studio_cartuchonefro': ultimoDcaHelpdeskTicket.x_studio_cartuchonefro.id,
                                                        'x_studio_rendimiento_negro': ultimoDcaHelpdeskTicket.x_studio_rendimiento_negro,
                                                        'x_studio_cartucho_amarillo': ultimoDcaHelpdeskTicket.x_studio_cartucho_amarillo.id,
                                                        'x_studio_rendimientoa': ultimoDcaHelpdeskTicket.x_studio_rendimientoa,
                                                        'x_studio_cartucho_cian_1': ultimoDcaHelpdeskTicket.x_studio_cartucho_cian_1.id,
                                                        'x_studio_rendimientoc': ultimoDcaHelpdeskTicket.x_studio_rendimientoc,
                                                        'x_studio_cartucho_magenta': ultimoDcaHelpdeskTicket.x_studio_cartucho_magenta.id,
                                                        'x_studio_rendimientom': ultimoDcaHelpdeskTicket.x_studio_rendimientom,
                                                        'x_studio_fecha': ultimoDcaHelpdeskTicket.x_studio_fecha,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,

                                                        'contadorColor': self.contadorColorActualizado,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,

                                                        'paginasProcesadasBN': ultimoDcaHelpdeskTicket.paginasProcesadasBN,
                                                        'porcentajeNegro': ultimoDcaHelpdeskTicket.porcentajeNegro,
                                                        'porcentajeAmarillo': ultimoDcaHelpdeskTicket.porcentajeAmarillo,
                                                        'porcentajeCian': ultimoDcaHelpdeskTicket.porcentajeCian,
                                                        'porcentajeMagenta': ultimoDcaHelpdeskTicket.porcentajeMagenta,
                                                        'x_studio_rendimiento': ultimoDcaHelpdeskTicket.x_studio_rendimiento,
                                                        'x_studio_rendimiento_color': ultimoDcaHelpdeskTicket.x_studio_rendimiento_color,
                                                        'x_studio_toner_negro': ultimoDcaHelpdeskTicket.x_studio_toner_negro,
                                                        'x_studio_toner_cian': ultimoDcaHelpdeskTicket.x_studio_toner_cian,
                                                        'x_studio_toner_magenta': ultimoDcaHelpdeskTicket.x_studio_toner_magenta,
                                                        'x_studio_toner_amarillo': ultimoDcaHelpdeskTicket.x_studio_toner_amarillo,
                                                        'nivelCA': ultimoDcaHelpdeskTicket.nivelCA,
                                                        'nivelMA': ultimoDcaHelpdeskTicket.nivelMA,
                                                        'nivelNA': ultimoDcaHelpdeskTicket.nivelNA,
                                                        'nivelAA': ultimoDcaHelpdeskTicket.nivelAA,
                                                        'contadorAnteriorNegro': ultimoDcaHelpdeskTicket.contadorAnteriorNegro,
                                                        'contadorAnteriorAmarillo': ultimoDcaHelpdeskTicket.contadorAnteriorAmarillo,
                                                        'contadorAnteriorMagenta': ultimoDcaHelpdeskTicket.contadorAnteriorMagenta,
                                                        'contadorAnteriorCian': ultimoDcaHelpdeskTicket.contadorAnteriorCian,
                                                        'paginasProcesadasA': ultimoDcaHelpdeskTicket.paginasProcesadasA,
                                                        'paginasProcesadasC': ultimoDcaHelpdeskTicket.paginasProcesadasC,
                                                        'paginasProcesadasM': ultimoDcaHelpdeskTicket.paginasProcesadasM,
                                                        'renM': ultimoDcaHelpdeskTicket.renM,
                                                        'renA': ultimoDcaHelpdeskTicket.renA,
                                                        'renC': ultimoDcaHelpdeskTicket.renC,
                                                        'reinicioDeContador': True
                                                  })
                else:
                    negrot = 0
                    colort = 0
                    mesaFuente = self.env['dcas.dcas'].create({
                                                        'serie': c.id,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,
                                                        'contadorColor': self.contadorColorActualizado,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'reinicioDeContador': True
                                                  })
                tipoEquipoTemp = str(c.x_studio_color_bn)
                nombreSerieTemp = c.name
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(mesaFuente.create_date)
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(negrot)
                contadorAnteriorColorTemp = str(colort)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                mesaFuente.comentarioDeReinicio = comentarioDeReinicio
                q = 'tfs.tfs'
                ultimoDcaTfsTfs = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaTfsTfs:
                    negrot = ultimoDcaTfsTfs.contadorMono
                    colort = ultimoDcaTfsTfs.contadorColor
                    tfsFuente = self.env['dcas.dcas'].create({
                                                        'x_studio_cliente': ultimoDcaTfsTfs.x_studio_cliente,
                                                        'serie': c.id,
                                                        'x_studio_color_o_bn': ultimoDcaTfsTfs.x_studio_color_o_bn,
                                                        'x_studio_cartuchonefro': ultimoDcaTfsTfs.x_studio_cartuchonefro.id,
                                                        'x_studio_rendimiento_negro': ultimoDcaTfsTfs.x_studio_rendimiento_negro,
                                                        'x_studio_cartucho_amarillo': ultimoDcaTfsTfs.x_studio_cartucho_amarillo.id,
                                                        'x_studio_rendimientoa': ultimoDcaTfsTfs.x_studio_rendimientoa,
                                                        'x_studio_cartucho_cian_1': ultimoDcaTfsTfs.x_studio_cartucho_cian_1.id,
                                                        'x_studio_rendimientoc': ultimoDcaTfsTfs.x_studio_rendimientoc,
                                                        'x_studio_cartucho_magenta': ultimoDcaTfsTfs.x_studio_cartucho_magenta.id,
                                                        'x_studio_rendimientom': ultimoDcaTfsTfs.x_studio_rendimientom,
                                                        'x_studio_fecha': ultimoDcaTfsTfs.x_studio_fecha,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,

                                                        'contadorColor': self.contadorColorActualizado,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,

                                                        'paginasProcesadasBN': ultimoDcaTfsTfs.paginasProcesadasBN,
                                                        'porcentajeNegro': ultimoDcaTfsTfs.porcentajeNegro,
                                                        'porcentajeAmarillo': ultimoDcaTfsTfs.porcentajeAmarillo,
                                                        'porcentajeCian': ultimoDcaTfsTfs.porcentajeCian,
                                                        'porcentajeMagenta': ultimoDcaTfsTfs.porcentajeMagenta,
                                                        'x_studio_rendimiento': ultimoDcaTfsTfs.x_studio_rendimiento,
                                                        'x_studio_rendimiento_color': ultimoDcaTfsTfs.x_studio_rendimiento_color,
                                                        'x_studio_toner_negro': ultimoDcaTfsTfs.x_studio_toner_negro,
                                                        'x_studio_toner_cian': ultimoDcaTfsTfs.x_studio_toner_cian,
                                                        'x_studio_toner_magenta': ultimoDcaTfsTfs.x_studio_toner_magenta,
                                                        'x_studio_toner_amarillo': ultimoDcaTfsTfs.x_studio_toner_amarillo,
                                                        'nivelCA': ultimoDcaTfsTfs.nivelCA,
                                                        'nivelMA': ultimoDcaTfsTfs.nivelMA,
                                                        'nivelNA': ultimoDcaTfsTfs.nivelNA,
                                                        'nivelAA': ultimoDcaTfsTfs.nivelAA,
                                                        'contadorAnteriorNegro': ultimoDcaTfsTfs.contadorAnteriorNegro,
                                                        'contadorAnteriorAmarillo': ultimoDcaTfsTfs.contadorAnteriorAmarillo,
                                                        'contadorAnteriorMagenta': ultimoDcaTfsTfs.contadorAnteriorMagenta,
                                                        'contadorAnteriorCian': ultimoDcaTfsTfs.contadorAnteriorCian,
                                                        'paginasProcesadasA': ultimoDcaTfsTfs.paginasProcesadasA,
                                                        'paginasProcesadasC': ultimoDcaTfsTfs.paginasProcesadasC,
                                                        'paginasProcesadasM': ultimoDcaTfsTfs.paginasProcesadasM,
                                                        'renM': ultimoDcaTfsTfs.renM,
                                                        'renA': ultimoDcaTfsTfs.renA,
                                                        'renC': ultimoDcaTfsTfs.renC,
                                                        'reinicioDeContador': True
                                                  })
                else:
                    negrot = 0
                    colort = 0
                    tfsFuente = self.env['dcas.dcas'].create({
                                                        'serie': c.id,
                                                        'x_studio_tiquete': self.ticket_id.id,
                                                        'x_studio_tickett': self.ticket_id.id,
                                                        'fuente': q,
                                                        'contadorColor': self.contadorColorActualizado,
                                                        'x_studio_contador_color_anterior': colort,
                                                        'contadorMono': self.contadorMonoActualizado,
                                                        'x_studio_contador_mono_anterior_1': negrot,
                                                        'reinicioDeContador': True
                                                  })
                tipoEquipoTemp = str(c.x_studio_color_bn)
                nombreSerieTemp = c.name
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(tfsFuente.create_date)
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(negrot)
                contadorAnteriorColorTemp = str(colort)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                tfsFuente.comentarioDeReinicio = comentarioDeReinicio
                
                self.env['helpdesk.diagnostico'].create({
                                                            'ticketRelacion':self.ticket_id.x_studio_id_ticket,
                                                            'estadoTicket': 'Reinicio de contadores en el estado ' + self.estado,
                                                            'evidencia': [(6,0,self.evidencia.ids)],
                                                            'mostrarComentario': self.check,
                                                            'write_uid':  self.env.user.name,
                                                            'comentario': 'Reinicio de contadores.\nContador BN anterior: ' + str(negroMesa) + '\nContador BN capturado: ' + str(self.contadorMonoActualizado) + '\nContador color anterior: ' + str(colorMesa) + '\nContador color capturado: ' + str(self.contadorColorActualizado) + '\n\n' + self.comentario,
                                                            'creadoPorSistema': True
                                                        })
                self.ticket_id.write({'contadores_anteriores': '</br>Equipo BN o Color: ' + str(self.bnColor) + ' </br></br>Contador BN: ' + str(self.contadorMonoActualizado) + '</br></br>Contador Color: ' + str(self.contadorColorActualizado)
                                    , 'x_studio_contador_bn': int(negroMesa)
                                    , 'x_studio_contador_bn_a_capturar': int(self.contadorMonoActualizado)
                                    , 'x_studio_contador_color': int(colorMesa)
                                    , 'x_studio_contador_color_a_capturar': int(self.contadorColorActualizado)
                                    })
                self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
                mensajeTitulo = "Contador reiniciado!!!"
                mensajeCuerpo = "Se reinicio el contador del equipo " + str(c.name) + "."
                wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                        'context': self.env.context,
                        }
                #else:
                #    raise exceptions.ValidationError("Error al capturar contador, el contador capturado debe ser mayor.")










class helpdesk_editar_contadores_mesa(TransientModel):
    _name = 'helpdesk.contadores.editar.mesa'
    _description = 'helpdesk permite editar los contadores actuales en mesa de ayuda.'

    ticket_id = fields.Many2one(
                                    "helpdesk.ticket",
                                    string = 'Ticket'
                                )
    serieSeleccionada = fields.Text(
                            string = 'Serie seleccionada',
                            compute = "_compute_serieSeleccionada"
                        )
    tipoEquipo = fields.Selection(
                                    [('Color','Color'),('B/N','B/N')],
                                    string = 'Equipo color o B/N',
                                    compute = '_compute_equipoSeleccionado'
                                )
    contadorMonoActual = fields.Integer(
                                            string = 'Contador Monocromatico actual',
                                            store = False,
                                            compute = '_compute_contador_bn_actual'
                                        )
    contadorColorActual = fields.Integer(
                                            string = 'Contador Color actual',
                                            store = False,
                                            compute = '_compute_contador_color_actual'
                                        )
    contadorMonoActualizado = fields.Integer(
                                                string = 'Contador Monocromatico nuevo',
                                                store = True,
                                                default = 0
                                            )
    contadorColorActualizado = fields.Integer(
                                                string = 'Contador Color nuevo',
                                                store = True,
                                                default = 0
                                            )

    evidencia = fields.Many2many(
                                    'ir.attachment',
                                    string = "Evidencias"
                                )
    comentario = fields.Text(
                                string = 'Comentario'
                            )
    check = fields.Boolean(
                                string = 'Mostrar en reporte',
                                default = False
                            )
    estado = fields.Char(
                            string = 'Estado', 
                            compute = "_compute_estadoTicket"
                        )
    textoInformativo = fields.Text(
                                        string = ' ',
                                        default = ' ',
                                        store = False,
                                        compute = '_compute_textoInformativo'
                                    )

    def _compute_equipoSeleccionado(self):
        for record in self:
            if record.ticket_id.x_studio_equipo_por_nmero_de_serie and record.ticket_id.x_studio_equipo_por_nmero_de_serie.x_studio_color_bn:
                record.tipoEquipo = record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_color_bn

    def _compute_serieSeleccionada(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.serieSeleccionada = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name

    def _compute_estadoTicket(self):
        if self.ticket_id:
            self.estado = self.ticket_id.stage_id.name

    def _compute_contador_bn_actual(self):
        for record in self:
            dominio_ultimo_contador = [('serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
            dominio_ultimo_contador = [('serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
            _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))


            if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                record.contadorMonoActual = ultimo_contador_techra.contadorMono
            else:
                record.contadorMonoActual = ultimo_contador_odoo.contadorMono


            #fuente = 'stock.production.lot'
            #ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
            #if ultimoDcaStockProductionLot:
            #    record.contadorMonoActual = ultimoDcaStockProductionLot.contadorMono

    def _compute_contador_color_actual(self):
        for record in self:
            dominio_ultimo_contador = [('serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
            dominio_ultimo_contador = [('serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
            _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

            if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                record.contadorColorActual = ultimo_contador_techra.contadorColor
            else:
                record.contadorColorActual = ultimo_contador_odoo.contadorColor

            #fuente = 'stock.production.lot'
            #ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
            #if ultimoDcaStockProductionLot:
            #    record.contadorColorActual = ultimoDcaStockProductionLot.contadorColor

    def _compute_textoInformativo(self):
        #q = 'stock.production.lot'
        #ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        #q = 'dcas.dcas'
        #ultimoDcaDcasDcas = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        #q = 'helpdesk.ticket'
        #ultimoDcaHelpdeskTicket = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        #q = 'tfs.tfs'
        #ultimoDcaTfsTfs = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        #self.textoInformativo = 'ultimoDcaStockProductionLot: ' + str(ultimoDcaStockProductionLot.id) + '\nultimoDcaDcasDcas: ' + str(ultimoDcaDcasDcas.id) + '\nultimoDcaHelpdeskTicket: ' + str(ultimoDcaHelpdeskTicket.id) + '\nultimoDcaTfsTfs: ' + str(ultimoDcaTfsTfs.id) + '\n\n'

        dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
        ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
        dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
        ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
        _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

        ultimoDcaStockProductionLot = False
        if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
            ultimoDcaStockProductionLot = ultimo_contador_techra
        else:
            ultimoDcaStockProductionLot = ultimo_contador_odoo

        for c in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            comentarioDeReinicio = """
                    <div class='alert alert-info' role='alert'>
                        <h4 class="alert-heading">Edición de contadores por realizar !!!</h4>

                        <p>Se editara el contador de la serie <strong>""" + str(c.name) + """</strong> por medio del ticket <strong>""" + str(self.ticket_id.id) + """</strong> y con los siguientes detalles: </p>
                        <br/>
                        <div class='row'>
                            <div class='col-sm-3'>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>Realizado el día:</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>""" + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ) + """</p>
                                    </div>
                                </div>
                            </div>

                            <div class='col-sm-3'>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>Realizado por:</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>""" + self.env.user.name + """</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class='col-sm-3'>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>Contador anterior B/N:</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>""" + str(ultimoDcaStockProductionLot.contadorMono) + """</p>
                                    </div>
                                </div>
                            </div>

                            <div class='col-sm-3'>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>Contador anterior Color:</p>
                                    </div>
                                </div>
                                <div class='row'>
                                    <div class='col-sm-12'>
                                        <p>""" + str(ultimoDcaStockProductionLot.contadorColor) + """</p>
                                    </div>
                                </div>
                            </div>


                        </div>
                        
                    </div>
                    """

        self.textoInformativo = comentarioDeReinicio


    def comentarioDeReinicio(self, tipoEquipo, serie, ticket_id, fecha, usuario, contadorAnteriorNegro, contadorAnteriorColor):
        comentarioDeReinicio = """ """
        if tipoEquipo == 'B/N':
            comentarioDeReinicio = """
                                            <div class='alert alert-info' role='alert'>
                                                <h4 class="alert-heading">Edición de contadores realizado !!!</h4>

                                                <p>Se edito el contador de la serie <strong>""" + serie + """</strong> por medio del ticket <strong>""" + ticket_id + """</strong> y con los siguientes detalles: </p>
                                                <br/>
                                                <div class='row'>
                                                    <div class='col-sm-4'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Realizado el día:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + fecha + """</p>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class='col-sm-4'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Realizado por:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + usuario + """</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class='col-sm-4'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Contador anterior B/N:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + contadorAnteriorNegro + """</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                
                                            </div>
                                            """
        elif tipoEquipo == 'Color':
            comentarioDeReinicio = """
                                            <div class='alert alert-info' role='alert'>
                                                <h4 class="alert-heading">Edición de contadores realizado !!!</h4>

                                                <p>Se edito el contador de la serie <strong>""" + serie + """</strong> por medio del ticket <strong>""" + ticket_id + """</strong> y con los siguientes detalles: </p>
                                                <br/>
                                                <div class='row'>
                                                    <div class='col-sm-3'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Realizado el día:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + fecha + """</p>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class='col-sm-3'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Realizado por:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + usuario + """</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class='col-sm-3'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Contador anterior B/N:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + contadorAnteriorNegro + """</p>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class='col-sm-3'>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>Contador anterior Color:</p>
                                                            </div>
                                                        </div>
                                                        <div class='row'>
                                                            <div class='col-sm-12'>
                                                                <p>""" + contadorAnteriorColor + """</p>
                                                            </div>
                                                        </div>
                                                    </div>


                                                </div>
                                                
                                            </div>
                                            """
        return comentarioDeReinicio


    def editarContadores(self):
        dominio_ultimo_contador = [('serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
        ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
        dominio_ultimo_contador = [('serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
        ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
        _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))
        
        ultimoDcaStockProductionLot = False
        if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
            ultimoDcaStockProductionLot = ultimo_contador_techra
        else:
            ultimoDcaStockProductionLot = ultimo_contador_odoo
        #q = 'stock.production.lot'
        vals = {
            'x_studio_cliente': ultimoDcaStockProductionLot.x_studio_cliente,
            'serie': self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id,
            'x_studio_color_o_bn': ultimoDcaStockProductionLot.x_studio_color_o_bn,
            'x_studio_cartuchonefro': ultimoDcaStockProductionLot.x_studio_cartuchonefro.id,
            'x_studio_rendimiento_negro': ultimoDcaStockProductionLot.x_studio_rendimiento_negro,
            'x_studio_cartucho_amarillo': ultimoDcaStockProductionLot.x_studio_cartucho_amarillo.id,
            'x_studio_rendimientoa': ultimoDcaStockProductionLot.x_studio_rendimientoa,
            'x_studio_cartucho_cian_1': ultimoDcaStockProductionLot.x_studio_cartucho_cian_1.id,
            'x_studio_rendimientoc': ultimoDcaStockProductionLot.x_studio_rendimientoc,
            'x_studio_cartucho_magenta': ultimoDcaStockProductionLot.x_studio_cartucho_magenta.id,
            'x_studio_rendimientom': ultimoDcaStockProductionLot.x_studio_rendimientom,
            'x_studio_fecha': ultimoDcaStockProductionLot.x_studio_fecha,
            'x_studio_tiquete': self.ticket_id.id,
            'x_studio_tickett': self.ticket_id.id,

            'contadorColor': self.contadorColorActualizado,
            'x_studio_contador_color_anterior': ultimoDcaStockProductionLot.x_studio_contador_color_anterior,
            'contadorMono': self.contadorMonoActualizado,
            'x_studio_contador_mono_anterior_1': ultimoDcaStockProductionLot.x_studio_contador_mono_anterior_1,

            'paginasProcesadasBN': ultimoDcaStockProductionLot.paginasProcesadasBN,
            'porcentajeNegro': ultimoDcaStockProductionLot.porcentajeNegro,
            'porcentajeAmarillo': ultimoDcaStockProductionLot.porcentajeAmarillo,
            'porcentajeCian': ultimoDcaStockProductionLot.porcentajeCian,
            'porcentajeMagenta': ultimoDcaStockProductionLot.porcentajeMagenta,
            'x_studio_rendimiento': ultimoDcaStockProductionLot.x_studio_rendimiento,
            'x_studio_rendimiento_color': ultimoDcaStockProductionLot.x_studio_rendimiento_color,
            'x_studio_toner_negro': ultimoDcaStockProductionLot.x_studio_toner_negro,
            'x_studio_toner_cian': ultimoDcaStockProductionLot.x_studio_toner_cian,
            'x_studio_toner_magenta': ultimoDcaStockProductionLot.x_studio_toner_magenta,
            'x_studio_toner_amarillo': ultimoDcaStockProductionLot.x_studio_toner_amarillo,
            'nivelCA': ultimoDcaStockProductionLot.nivelCA,
            'nivelMA': ultimoDcaStockProductionLot.nivelMA,
            'nivelNA': ultimoDcaStockProductionLot.nivelNA,
            'nivelAA': ultimoDcaStockProductionLot.nivelAA,
            'contadorAnteriorNegro': ultimoDcaStockProductionLot.contadorAnteriorNegro,
            'contadorAnteriorAmarillo': ultimoDcaStockProductionLot.contadorAnteriorAmarillo,
            'contadorAnteriorMagenta': ultimoDcaStockProductionLot.contadorAnteriorMagenta,
            'contadorAnteriorCian': ultimoDcaStockProductionLot.contadorAnteriorCian,
            'paginasProcesadasA': ultimoDcaStockProductionLot.paginasProcesadasA,
            'paginasProcesadasC': ultimoDcaStockProductionLot.paginasProcesadasC,
            'paginasProcesadasM': ultimoDcaStockProductionLot.paginasProcesadasM,
            'renM': ultimoDcaStockProductionLot.renM,
            'renA': ultimoDcaStockProductionLot.renA,
            'renC': ultimoDcaStockProductionLot.renC,
            'reinicioDeContador': True
        }
        vals_sin_dca_previo = {
            'serie': self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id,
            'x_studio_tiquete': self.ticket_id.id,
            'x_studio_tickett': self.ticket_id.id,
            #'fuente': q,
            'contadorColor': self.contadorColorActualizado,
            'x_studio_contador_color_anterior': 0,
            'contadorMono': self.contadorMonoActualizado,
            'x_studio_contador_mono_anterior_1': 0,
            'reinicioDeContador': True
        }
        tipoEquipoTemp = str(self.tipoEquipo)
        nombreSerieTemp = self.serieSeleccionada
        idTicketTemp = str(self.ticket_id.id)
        nombreUsuarioTemp = self.env.user.name
        contadorAnteriorNegroTemp = str(0)
        contadorAnteriorColorTemp = str(0)
        #if str(self.tipoEquipo) == 'B/N':
        comentarioDeReinicio = """ """
        rr = ''
        dcaFuente = ''
        mesaFuente = ''
        tfsFuente = ''
        #Creando dca para mesa stock.production.lot
        #ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        vals['fuente'] = 'stock.production.lot'
        vals_sin_dca_previo['fuente'] = 'stock.production.lot'
        if ultimoDcaStockProductionLot:
            rr = self.env['dcas.dcas'].create(vals)
            contadorAnteriorNegroTemp = str(0)
            contadorAnteriorColorTemp = str(0)
        else:
            rr = self.env['dcas.dcas'].create(vals_sin_dca_previo)

        fechaCreacionTemp = str(rr.create_date)
        comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
        rr.write({
            'comentarioDeReinicio': comentarioDeReinicio
        })
        
        #Creando el dca de la fuente dcas.dcas
        vals['fuente'] = 'dcas.dcas'
        vals_sin_dca_previo['fuente'] = 'dcas.dcas'
        #ultimoDcaDcasDcas = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        if ultimoDcaStockProductionLot:
            dcaFuente = self.env['dcas.dcas'].create(vals)
            contadorAnteriorNegroTemp = str(0)
            contadorAnteriorColorTemp = str(0)
        else:
            dcaFuente = self.env['dcas.dcas'].create(vals_sin_dca_previo)

        fechaCreacionTemp = str(dcaFuente.create_date)
        comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
        dcaFuente.write({
            'comentarioDeReinicio': comentarioDeReinicio
        })

        #Creando el dca de la fuente helpdesk.ticket
        vals['fuente'] = 'helpdesk.ticket'
        vals_sin_dca_previo['fuente'] = 'helpdesk.ticket'
        #ultimoDcaHelpdeskTicket = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        if ultimoDcaStockProductionLot:
            mesaFuente = self.env['dcas.dcas'].create(vals)
            contadorAnteriorNegroTemp = str(0)
            contadorAnteriorColorTemp = str(0)
        else:
            mesaFuente = self.env['dcas.dcas'].create(vals_sin_dca_previo)
        
        fechaCreacionTemp = str(mesaFuente.create_date)
        
        comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
        mesaFuente.write({
            'comentarioDeReinicio': comentarioDeReinicio
        })

        #Creando el dca de la fuente tfs.tfs
        vals['fuente'] = 'tfs.tfs'
        vals_sin_dca_previo['fuente'] = 'tfs.tfs'
        #ultimoDcaTfsTfs = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        if ultimoDcaTfsTfs:
            tfsFuente = self.env['dcas.dcas'].create(vals)
            contadorAnteriorNegroTemp = str(0)
            contadorAnteriorColorTemp = str(0)
        else:
            tfsFuente = self.env['dcas.dcas'].create(vals_sin_dca_previo)

        fechaCreacionTemp = str(tfsFuente.create_date)
        comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
        tfsFuente.write({
            'comentarioDeReinicio': comentarioDeReinicio
        })
        comentario = ''
        contadores_anteriores = ''
        if str(self.tipoEquipo) == 'B/N':
            comentario = 'Reinicio de contadores.\nContador B/N anterior: ' + str(self.contadorMonoActual) + '\nContador B/N capturado: ' + str(self.contadorMonoActualizado)
            contadores_anteriores = 'Equipo B/N o Color: ' + str(self.tipoEquipo) + '</br>Contador B/N: ' + str(self.contadorMonoActualizado)
        elif str(self.tipoEquipo) == 'Color':
            comentario = 'Reinicio de contadores.\nContador B/N anterior: ' + str(self.contadorMonoActual) + '\nContador B/N capturado: ' + str(self.contadorMonoActualizado) + '\nContador Color anterior: ' + str(self.contadorColorActual) + '\nContador Color capturado: ' + str(self.contadorColorActualizado)
            contadores_anteriores = 'Equipo B/N o Color: ' + str(self.tipoEquipo) + '</br>Contador B/N: ' + str(self.contadorMonoActualizado) + '</br>Contador Color: ' + str(self.contadorColorActualizado)
        if self.comentario:
            comentario = comentario + self.comentario
        self.env['helpdesk.diagnostico'].create({
            'ticketRelacion':self.ticket_id.x_studio_id_ticket,
            'estadoTicket': self.estado,
            'evidencia': [(6, 0, self.evidencia.ids)],
            'mostrarComentario': self.check,
            'write_uid':  self.env.user.name,
            'comentario': comentario,
            'creadoPorSistema': True
        })
        self.ticket_id.write({
            'contadores_anteriores': contadores_anteriores,
            'x_studio_contador_bn': int(self.contadorMonoActual), 
            'x_studio_contador_bn_a_capturar': int(self.contadorMonoActualizado), 
            'x_studio_contador_color': int(self.contadorColorActual),
            'x_studio_contador_color_a_capturar': int(self.contadorColorActualizado)
        })
        self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
        mensajeTitulo = "Contador reiniciado!!!"
        mensajeCuerpo = "Se reinicio el contador del equipo " + str(self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name) + ".\n" + comentario
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                'context': self.env.context,
                }







        #for c in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            #fuente = 'stock.production.lot'
            #ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', fuente],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)

            dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
            dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
            _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))
            

            ultimoDcaStockProductionLot = False
            if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                ultimoDcaStockProductionLot = ultimo_contador_techra
            else:
                ultimoDcaStockProductionLot = ultimo_contador_odoo
                


            q = 'stock.production.lot'
            if self.tipoEquipo == 'B/N':
                comentarioDeReinicio = """ """
                #Creando dca para mesa stock.production.lot
                ultimoDcaCapturado = self.env['dcas.dcas'].search([['x_studio_tickett', '=', self.ticket_id.id],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
                if ultimoDcaCapturado:
                    ultimoDcaCapturado.write({
                                                'contadorMono': self.contadorMonoActualizado
                                            })
                tipoEquipoTemp = str(self.tipoEquipo)
                nombreSerieTemp = self.serieSeleccionada
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") )
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(self.contadorMonoActual)
                contadorAnteriorColorTemp = str(self.contadorColorActual)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                ultimoDcaCapturado.write({'comentarioDeReinicio': comentarioDeReinicio})
                self.env['helpdesk.diagnostico'].create({
                                                            'ticketRelacion':self.ticket_id.x_studio_id_ticket,
                                                            'estadoTicket': 'Reinicio de contadores en el estado ' + self.estado,
                                                            'evidencia': [(6,0,self.evidencia.ids)],
                                                            'mostrarComentario': self.check,
                                                            'write_uid':  self.env.user.name,
                                                            'comentario': 'Reinicio de contadores.\n Contador BN anterior: ' + str(self.contadorMonoActual) + '\nContador BN capturado: ' + str(self.contadorMonoActualizado) + '\n\n' + self.comentario,
                                                            'creadoPorSistema': False
                                                        })
                self.ticket_id.write({'contadores_anteriores': 'Equipo B/N o Color: ' + str(self.tipoEquipo) + '</br>Contador B/N: ' + str(self.contadorMonoActualizado) + '</br>Contador Color: ' + str(self.contadorColorActualizado)
                                    , 'x_studio_contador_bn': int(self.contadorMonoActual)
                                    , 'x_studio_contador_bn_a_capturar': int(self.contadorMonoActualizado)
                                    , 'x_studio_contador_color': 0
                                    , 'x_studio_contador_color_a_capturar': 0
                                    })
                self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
                mensajeTitulo = "Contador actualizado!!!"
                mensajeCuerpo = "Se edito el contador del equipo " + str(self.serieSeleccionada) + "."
                wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                        'context': self.env.context,
                        }
                
            if self.tipoEquipo != 'B/N':
                comentarioDeReinicio = """ """
                ultimoDcaCapturado = self.env['dcas.dcas'].search([['x_studio_tickett', '=', self.ticket_id.id],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)                
                if ultimoDcaCapturado:
                    ultimoDcaCapturado.write({
                                                'contadorColor': self.contadorColorActualizado,
                                                'contadorMono': self.contadorMonoActualizado
                                            })
                tipoEquipoTemp = str(self.tipoEquipo)
                nombreSerieTemp = self.serieSeleccionada
                idTicketTemp = str(self.ticket_id.id)
                fechaCreacionTemp = str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") )
                nombreUsuarioTemp = self.env.user.name
                contadorAnteriorNegroTemp = str(self.contadorMonoActual)
                contadorAnteriorColorTemp = str(self.contadorColorActual)
                comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
                ultimoDcaCapturado.write({'comentarioDeReinicio': comentarioDeReinicio})
                                
                self.env['helpdesk.diagnostico'].create({
                                                            'ticketRelacion':self.ticket_id.x_studio_id_ticket,
                                                            'estadoTicket': 'Reinicio de contadores en el estado ' + self.estado,
                                                            'evidencia': [(6,0,self.evidencia.ids)],
                                                            'mostrarComentario': self.check,
                                                            'write_uid':  self.env.user.name,
                                                            'comentario': 'Reinicio de contadores.\nContador BN anterior: ' + str(self.contadorMonoActual) + '\nContador BN capturado: ' + str(self.contadorMonoActualizado) + '\nContador color anterior: ' + str(self.contadorColorActual) + '\nContador color capturado: ' + str(self.contadorColorActualizado) + '\n\n' + self.comentario,
                                                            'creadoPorSistema': False
                                                        })
                self.ticket_id.write({'contadores_anteriores': '</br>Equipo BN o Color: ' + str(self.tipoEquipo) + ' </br></br>Contador BN: ' + str(self.contadorMonoActualizado) + '</br></br>Contador Color: ' + str(self.contadorColorActualizado)
                                    , 'x_studio_contador_bn': int(self.contadorMonoActual)
                                    , 'x_studio_contador_bn_a_capturar': int(self.contadorMonoActualizado)
                                    , 'x_studio_contador_color': int(self.contadorColorActual)
                                    , 'x_studio_contador_color_a_capturar': int(self.contadorColorActualizado)
                                    })
                self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
                mensajeTitulo = "Contador actualizado!!!"
                mensajeCuerpo = "Se edito el contador del equipo " + str(self.serieSeleccionada) + "."
                wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
                view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                        'context': self.env.context,
                        }
                #else:
                #    raise exceptions.ValidationError("Error al capturar contador, el contador capturado debe ser mayor.")


    def reiniciarContadores(self):
        #for c in self.ticket_id.x_studio_equipo_por_nmero_de_serie:
        dominio_ultimo_contador = [('serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
        ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
        dominio_ultimo_contador = [('serie', '=', record.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
        ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
        _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

        ultimoDcaStockProductionLot = False

        if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
            ultimoDcaStockProductionLot = ultimo_contador_techra
        else:
            ultimoDcaStockProductionLot = ultimo_contador_odoo
        #q = 'stock.production.lot'
        vals = {
            'x_studio_cliente': ultimoDcaStockProductionLot.x_studio_cliente,
            'serie': self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id,
            'x_studio_color_o_bn': ultimoDcaStockProductionLot.x_studio_color_o_bn,
            'x_studio_cartuchonefro': ultimoDcaStockProductionLot.x_studio_cartuchonefro.id,
            'x_studio_rendimiento_negro': ultimoDcaStockProductionLot.x_studio_rendimiento_negro,
            'x_studio_cartucho_amarillo': ultimoDcaStockProductionLot.x_studio_cartucho_amarillo.id,
            'x_studio_rendimientoa': ultimoDcaStockProductionLot.x_studio_rendimientoa,
            'x_studio_cartucho_cian_1': ultimoDcaStockProductionLot.x_studio_cartucho_cian_1.id,
            'x_studio_rendimientoc': ultimoDcaStockProductionLot.x_studio_rendimientoc,
            'x_studio_cartucho_magenta': ultimoDcaStockProductionLot.x_studio_cartucho_magenta.id,
            'x_studio_rendimientom': ultimoDcaStockProductionLot.x_studio_rendimientom,
            'x_studio_fecha': ultimoDcaStockProductionLot.x_studio_fecha,
            'x_studio_tiquete': self.ticket_id.id,
            'x_studio_tickett': self.ticket_id.id,

            'contadorColor': self.contadorColorActualizado,
            'x_studio_contador_color_anterior': ultimoDcaStockProductionLot.x_studio_contador_color_anterior,
            'contadorMono': self.contadorMonoActualizado,
            'x_studio_contador_mono_anterior_1': ultimoDcaStockProductionLot.x_studio_contador_mono_anterior_1,

            'paginasProcesadasBN': ultimoDcaStockProductionLot.paginasProcesadasBN,
            'porcentajeNegro': ultimoDcaStockProductionLot.porcentajeNegro,
            'porcentajeAmarillo': ultimoDcaStockProductionLot.porcentajeAmarillo,
            'porcentajeCian': ultimoDcaStockProductionLot.porcentajeCian,
            'porcentajeMagenta': ultimoDcaStockProductionLot.porcentajeMagenta,
            'x_studio_rendimiento': ultimoDcaStockProductionLot.x_studio_rendimiento,
            'x_studio_rendimiento_color': ultimoDcaStockProductionLot.x_studio_rendimiento_color,
            'x_studio_toner_negro': ultimoDcaStockProductionLot.x_studio_toner_negro,
            'x_studio_toner_cian': ultimoDcaStockProductionLot.x_studio_toner_cian,
            'x_studio_toner_magenta': ultimoDcaStockProductionLot.x_studio_toner_magenta,
            'x_studio_toner_amarillo': ultimoDcaStockProductionLot.x_studio_toner_amarillo,
            'nivelCA': ultimoDcaStockProductionLot.nivelCA,
            'nivelMA': ultimoDcaStockProductionLot.nivelMA,
            'nivelNA': ultimoDcaStockProductionLot.nivelNA,
            'nivelAA': ultimoDcaStockProductionLot.nivelAA,
            'contadorAnteriorNegro': ultimoDcaStockProductionLot.contadorAnteriorNegro,
            'contadorAnteriorAmarillo': ultimoDcaStockProductionLot.contadorAnteriorAmarillo,
            'contadorAnteriorMagenta': ultimoDcaStockProductionLot.contadorAnteriorMagenta,
            'contadorAnteriorCian': ultimoDcaStockProductionLot.contadorAnteriorCian,
            'paginasProcesadasA': ultimoDcaStockProductionLot.paginasProcesadasA,
            'paginasProcesadasC': ultimoDcaStockProductionLot.paginasProcesadasC,
            'paginasProcesadasM': ultimoDcaStockProductionLot.paginasProcesadasM,
            'renM': ultimoDcaStockProductionLot.renM,
            'renA': ultimoDcaStockProductionLot.renA,
            'renC': ultimoDcaStockProductionLot.renC,
            'reinicioDeContador': True
        }
        vals_sin_dca_previo = {
            'serie': self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id,
            'x_studio_tiquete': self.ticket_id.id,
            'x_studio_tickett': self.ticket_id.id,
            #'fuente': q,
            'contadorColor': self.contadorColorActualizado,
            'x_studio_contador_color_anterior': 0,
            'contadorMono': self.contadorMonoActualizado,
            'x_studio_contador_mono_anterior_1': 0,
            'reinicioDeContador': True
        }
        tipoEquipoTemp = str(self.tipoEquipo)
        nombreSerieTemp = self.serieSeleccionada
        idTicketTemp = str(self.ticket_id.id)
        nombreUsuarioTemp = self.env.user.name
        contadorAnteriorNegroTemp = str(0)
        contadorAnteriorColorTemp = str(0)
        #if str(self.tipoEquipo) == 'B/N':
        comentarioDeReinicio = """ """
        rr = ''
        dcaFuente = ''
        mesaFuente = ''
        tfsFuente = ''
        #Creando dca para mesa stock.production.lot
        #ultimoDcaStockProductionLot = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        vals['fuente'] = 'stock.production.lot'
        vals_sin_dca_previo['fuente'] = 'stock.production.lot'
        if ultimoDcaStockProductionLot:
            rr = self.env['dcas.dcas'].create(vals)
            contadorAnteriorNegroTemp = str(0)
            contadorAnteriorColorTemp = str(0)
        else:
            rr = self.env['dcas.dcas'].create(vals_sin_dca_previo)

        fechaCreacionTemp = str(rr.create_date)
        comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
        rr.write({
            'comentarioDeReinicio': comentarioDeReinicio
        })
        
        #Creando el dca de la fuente dcas.dcas
        vals['fuente'] = 'dcas.dcas'
        vals_sin_dca_previo['fuente'] = 'dcas.dcas'
        #ultimoDcaDcasDcas = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        if ultimoDcaStockProductionLot:
            dcaFuente = self.env['dcas.dcas'].create(vals)
            contadorAnteriorNegroTemp = str(0)
            contadorAnteriorColorTemp = str(0)
        else:
            dcaFuente = self.env['dcas.dcas'].create(vals_sin_dca_previo)

        fechaCreacionTemp = str(dcaFuente.create_date)
        comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
        dcaFuente.write({
            'comentarioDeReinicio': comentarioDeReinicio
        })

        #Creando el dca de la fuente helpdesk.ticket
        vals['fuente'] = 'helpdesk.ticket'
        vals_sin_dca_previo['fuente'] = 'helpdesk.ticket'
        #ultimoDcaHelpdeskTicket = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        if ultimoDcaStockProductionLot:
            mesaFuente = self.env['dcas.dcas'].create(vals)
            contadorAnteriorNegroTemp = str(0)
            contadorAnteriorColorTemp = str(0)
        else:
            mesaFuente = self.env['dcas.dcas'].create(vals_sin_dca_previo)
        
        fechaCreacionTemp = str(mesaFuente.create_date)
        
        comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
        mesaFuente.write({
            'comentarioDeReinicio': comentarioDeReinicio
        })

        #Creando el dca de la fuente tfs.tfs
        vals['fuente'] = 'tfs.tfs'
        vals_sin_dca_previo['fuente'] = 'tfs.tfs'
        #ultimoDcaTfsTfs = self.env['dcas.dcas'].search([['fuente', '=', q],['serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id]], order='create_date desc', limit=1)
        if ultimoDcaTfsTfs:
            tfsFuente = self.env['dcas.dcas'].create(vals)
            contadorAnteriorNegroTemp = str(0)
            contadorAnteriorColorTemp = str(0)
        else:
            tfsFuente = self.env['dcas.dcas'].create(vals_sin_dca_previo)

        fechaCreacionTemp = str(tfsFuente.create_date)
        comentarioDeReinicio = self.comentarioDeReinicio(tipoEquipoTemp, nombreSerieTemp, idTicketTemp, fechaCreacionTemp, nombreUsuarioTemp, contadorAnteriorNegroTemp, contadorAnteriorColorTemp)
        tfsFuente.write({
            'comentarioDeReinicio': comentarioDeReinicio
        })
        comentario = ''
        contadores_anteriores = ''
        if str(self.tipoEquipo) == 'B/N':
            comentario = 'Reinicio de contadores.\nContador B/N anterior: ' + str(self.contadorMonoActual) + '\nContador B/N capturado: ' + str(self.contadorMonoActualizado)
            contadores_anteriores = 'Equipo B/N o Color: ' + str(self.tipoEquipo) + '</br>Contador B/N: ' + str(self.contadorMonoActualizado)
        elif str(self.tipoEquipo) == 'Color':
            comentario = 'Reinicio de contadores.\nContador B/N anterior: ' + str(self.contadorMonoActual) + '\nContador B/N capturado: ' + str(self.contadorMonoActualizado) + '\nContador Color anterior: ' + str(self.contadorColorActual) + '\nContador Color capturado: ' + str(self.contadorColorActualizado)
            contadores_anteriores = 'Equipo B/N o Color: ' + str(self.tipoEquipo) + '</br>Contador B/N: ' + str(self.contadorMonoActualizado) + '</br>Contador Color: ' + str(self.contadorColorActualizado)

        if self.comentario:
            comentario = comentario + self.comentario
        self.env['helpdesk.diagnostico'].create({
            'ticketRelacion':self.ticket_id.x_studio_id_ticket,
            'estadoTicket': self.estado,
            'evidencia': [(6, 0, self.evidencia.ids)],
            'mostrarComentario': self.check,
            'write_uid':  self.env.user.name,
            'comentario': comentario,
            'creadoPorSistema': True
        })
        self.ticket_id.write({
            'contadores_anteriores': contadores_anteriores,
            'x_studio_contador_bn': int(self.contadorMonoActual), 
            'x_studio_contador_bn_a_capturar': int(self.contadorMonoActualizado), 
            'x_studio_contador_color': int(self.contadorColorActual),
            'x_studio_contador_color_a_capturar': int(self.contadorColorActualizado)
        })
        self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
        mensajeTitulo = "Contador reiniciado!!!"
        mensajeCuerpo = "Se reinicio el contador del equipo " + str(self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name) + ".\n" + comentario
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
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
                'context': self.env.context,
                }








class HelpDeskDatosMesa(TransientModel):
    _name = 'helpdesk.datos.mesa'
    _description = 'HelpDesk informacion de mesa'

    ticket_id = fields.Many2one("helpdesk.ticket")
    etapa = fields.Text(
                            string = 'Etapa'
                        )
    tipoDeReporte = fields.Selection(
                                        listaTipoDeVale, 
                                        string = 'Tipo de reporte',
                                        store = True
                                    )

    diagnostico_id = fields.One2many(
                                        'helpdesk.diagnostico',
                                        'ticketRelacion',
                                        compute = '_compute_diagnosticos' 
                                    )

    serie = fields.Text(
                            string = "Serie",
                            store = True 
                            #compute = '_compute_serie_nombre'
                        )
    #series = fields.Many2many(
    #                            'stock.production.lot',
    #                            string = 'Series'
    #                        )
    seriesText = fields.Text(
                                    string = 'Series',
                                    store = True
                                )
    refaccionesText = fields.Text(
                                    string = 'Refacciones y accesorios',
                                    store = True
                                )
    #refacciones = fields.Many2many(
    #                                    'product.product',
    #                                    string = 'Refacciones y accesorios'
    #                                )
    solicitud = fields.Many2one(
                                    'sale.order', 
                                    string = 'Solicitud',
                                    compute = '_compute_solicitud'
                                )
    cliente = fields.Text(
                            string = 'Cliente',
                            store = True

                        )
    #cliente = fields.Many2one(  
    #                            'res.partner',
    #                            string = 'Cliente',
    #                            compute = '_compute_cliente'
    #                        )
    tipoCliente = fields.Selection(
                                        [('A','A'),('B','B'),('C','C'),('OTRO','D'),('VIP','VIP')], 
                                        string = 'Tipo de cliente',
                                        store = True
                                        #compute = '_compute_tipo_cliente'
                                    )
    localidad = fields.Text(
                                string = 'Localidad',
                                store = True
                            )
    #localidad = fields.Many2one(
    #                                'res.partner',
    #                                string = 'Localidad',
    #                                compute = '_compute_localidad'
    #                            )
    zonaLocalidad = fields.Selection(
                                        [('CHIHUAHUA','CHIHUAHUA'),('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')], 
                                        string = 'Zona localidad',
                                        store = True
                                        #compute = '_compute_zona_localidad'
                                    )
    localidadContacto = fields.Text(
                                        string = 'Localidad contacto',
                                        store = True
                                    )
    #localidadContacto = fields.Many2one(  
    #                                'res.partner',
    #                                string = 'Localidad contacto',
    #                                compute = '_compute_localidad_contacto'
    #                            )
    estadoLocalidad = fields.Text(
                                    string = 'Estado de localidad',
                                    store = True
                                    #compute = '_compute_estado_localidad'
                                )
    telefonoContactoLocalidad = fields.Text(
                                                string = 'Télefgono localidad contacto',
                                                store = True
                                                #compute = '_compute_telefono_localidad'
                                            )
    movilContactoLocalidad = fields.Text(
                                            string = 'Movil localidad contacto',
                                            store = True
                                            #compute = '_compute_movil_localidad'
                                        )
    correoContactoLocalidad = fields.Text(
                                            string = 'Correo electrónico localidad contacto',
                                            store = True
                                            #compute = '_compute_correo_localidad'
                                        )
    direccionLocalidad = fields.Text(
                                        string = 'Dirección localidad',
                                        store = True
                                        #compute = '_compute_direccion_localidad'
                                    )
    creadoEl = fields.Text(
                                string = 'Creado el',
                                store = True
                                #compute = '_compute_creado_el'
                            )
    areaAtencion = fields.Many2one(  
                                    'helpdesk.team',
                                    string = 'Área de atención',
                                    compute = '_compute_area_atencion'
                                )
    ejecutivo = fields.Many2one(  
                                    'res.users',
                                    string = 'Ejecutivo',
                                    compute = '_compute_ejecutivo'
                                )
    encargadoArea = fields.Many2one(  
                                    'hr.employee',
                                    string = 'Encargado de área',
                                    compute = '_compute_encargado_area'
                                )
    diasAtraso = fields.Integer(
                                    string = 'Días de atraso',
                                    store = True
                                    #compute = '_compute_dias_atraso'
                                )
    prioridad = fields.Selection(
                                    [('0','Todas'),('1','Baja'),('2','Media'),('3','Alta'),('4','Critica')], 
                                    string = 'Prioridad',
                                    store = True
                                    #compute = '_compute_prioridad'
                                )
    zona = fields.Selection(
                                        [('CHIHUAHUA','CHIHUAHUA'),('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')],
                                        string = 'Zona',
                                        store = True
                                        #compute = '_compute_zona'
                                    )
    zonaEstados = fields.Selection(
                                        [('Estado de México','Estado de México'), ('Campeche','Campeche'), ('Ciudad de México','Ciudad de México'), ('Yucatán','Yucatán'), ('Guanajuato','Guanajuato'), ('Puebla','Puebla'), ('Coahuila','Coahuila'), ('Sonora','Sonora'), ('Tamaulipas','Tamaulipas'), ('Oaxaca','Oaxaca'), ('Tlaxcala','Tlaxcala'), ('Morelos','Morelos'), ('Jalisco','Jalisco'), ('Sinaloa','Sinaloa'), ('Nuevo León','Nuevo León'), ('Baja California','Baja California'), ('Nayarit','Nayarit'), ('Querétaro','Querétaro'), ('Tabasco','Tabasco'), ('Hidalgo','Hidalgo'), ('Chihuahua','Chihuahua'), ('Quintana Roo','Quintana Roo'), ('Chiapas','Chiapas'), ('Veracruz','Veracruz'), ('Michoacán','Michoacán'), ('Aguascalientes','Aguascalientes'), ('Guerrero','Guerrero'), ('San Luis Potosí', 'San Luis Potosí'), ('Colima','Colima'), ('Durango','Durango'), ('Baja California Sur','Baja California Sur'), ('Zacatecas','Zacatecas')],
                                        string = 'Zona Estados',
                                        store = True
                                        #compute = '_compute_zona_estados'
                                    )
    numeroTicketCliente = fields.Text(
                                        string = 'Número de ticket cliente',
                                        store = True
                                        #compute = '_compute_numero_ticket_cliente'
                                    )
    numeroTicketDistribuidor = fields.Text(
                                            string = 'Número de ticket distribuidor',
                                            store = True
                                            #compute = '_compute_numero_ticket_distribuidor'
                                        )
    numeroTicketGuia = fields.Text(
                                    string = 'Número de guía',
                                    store = True
                                    #compute = '_compute_numero_ticket_guia'
                                )
    comentarioLocalidad = fields.Text(
                                        string = 'Comentario de localidad',
                                        store = True
                                        #compute = '_compute_comentario_localidad'
                                    )
    tiempoAtrasoTicket = fields.Text(
                                        string = 'Tiempo de atraso ticket',
                                        store = True
                                        #compute = '_compute_tiempo_ticket'
                                    )
    tiempoAtrasoAlmacen = fields.Text(
                                        string = 'Tiempo de atraso almacén',
                                        store = True
                                        #compute = '_compute_tiempo_almacen'
                                    )
    tiempoAtrasoDistribucion = fields.Text(
                                            string = 'Tiempo de atraso distribución',
                                            store = True
                                            #compute = '_compute_tiempo_distribucion'
                                        )
    reportes = fields.Many2one(
                                    'ir.actions.report',
                                    string = 'Reportes disponibles',
                                    store = True
                                )

    pdfToner = fields.Binary(
                                string = "PDF",
                                store = True
                            )


    @api.depends('reportes')
    def obtenerReportePdf(self):
        for record in self:
            idExterno = record.reportes.xml_id
            pdf = self.env.ref(idExterno).sudo().render_qweb_pdf([record.ticket_id.id])[0]
            #pdf = self.env['report'].sudo().get_pdf([self.ticket_id.id], report_name)
            record.pdfToner = False
            record.pdfToner = base64.encodestring(pdf)

    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids

    def _compute_solicitud(self):
        if self.ticket_id.x_studio_field_nO7Xg:
            self.solicitud = self.ticket_id.x_studio_field_nO7Xg.id

    def _compute_area_atencion(self):
        if self.ticket_id.team_id:
            self.areaAtencion = self.ticket_id.team_id.id

    def _compute_ejecutivo(self):
        if self.ticket_id.user_id:
            self.ejecutivo = self.ticket_id.user_id.id

    def _compute_encargado_area(self):
        if self.ticket_id.x_studio_responsable_de_equipo:
            self.encargadoArea = self.ticket_id.x_studio_responsable_de_equipo.id

    



class HelpDeskResueltoConComentario(TransientModel):
    _name = 'helpdesk.comentario.resuelto'
    _description = 'Mover al estado resuelto con un comentario.'
    check = fields.Boolean(string = 'Mostrar en reporte', default = False)
    ticket_id = fields.Many2one("helpdesk.ticket")
    diagnostico_id = fields.One2many('helpdesk.diagnostico', 'ticketRelacion', string = 'Diagnostico', compute = '_compute_diagnosticos')
    estado = fields.Char('Estado previo a cerrar el ticket', compute = "_compute_estadoTicket")
    comentario = fields.Text('Comentario')
    evidencia = fields.Many2many('ir.attachment', string = "Evidencias")

    def resuletoTicketConComentario(self):
        estadoAntes = str(self.ticket_id.stage_id.name)
        ultimaEvidenciaTec = []
        ultimoComentario = ''
        if self.ticket_id.diagnosticos:
            if self.ticket_id.diagnosticos[-1].evidencia.ids:
                ultimaEvidenciaTec = self.ticket_id.diagnosticos[-1].evidencia.ids
            ultimoComentario = self.ticket_id.diagnosticos[-1].comentario
        comentarioGenerico = 'Cambio de estado al seleccionar botón Resuelto. Se cambio al estado Resuelto. Seleccion realizada por ' + str(self.env.user.name) +'.'
        estado = 'Resuelto'
        if self.comentario:
            comentarioGenerico = comentarioGenerico + '\nComentario de ' + self.env.user.name + ': ' + self.comentario
        self.env['helpdesk.diagnostico'].create({   
                                                    'ticketRelacion': self.ticket_id.id,
                                                    'comentario': comentarioGenerico,
                                                    'estadoTicket': estado,
                                                    'evidencia': [(6,0,ultimaEvidenciaTec)],
                                                    'mostrarComentario': self.check,
                                                    'creadoPorSistema': False if self.comentario else True
                                                })
        self.ticket_id.write({
                                'stage_id': 3,
                                'estadoResuelto': True,
                                'estadoAtencion': False
                            })
        self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
        self.ticket_id.datos_ticket_2()
        message = 'Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Resuelto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página."
        wiz = self.env['helpdesk.alerta'].create({'ticket_id': self.ticket_id.id, 'mensaje': message})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        return {
            'name': _('Estado de ticket actualizado!!!'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.alerta',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }


    def _compute_estadoTicket(self):
        self.estado = self.ticket_id.stage_id.name

    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids

