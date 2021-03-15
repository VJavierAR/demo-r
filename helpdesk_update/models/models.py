# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError,RedirectWarning
from odoo.addons.helpdesk.models.helpdesk import HelpdeskTeam
from odoo import exceptions, _
import logging, ast
import datetime, time
import pytz
import base64
_logger = logging.getLogger(__name__)


class HistoricoC(models.Model):
    _name='x_studio_historico_de_componentes'
    _description='Historio de componentes'
    x_fecha_de_entrega_text=fields.Text()
    x_robot=fields.Text()
    x_serieTexto=fields.Text()
    x_tipo=fields.Text()
    x_relacion_refacciones=fields.Many2one('helpdesk.confirmar.validar.refacciones')
    x_studio_field_MH4DO=fields.Many2one('stock.production.lot')
    x_studio_field_gKQ9k=fields.Many2one('product.product')
    x_studio_cantidad=fields.Integer()
    x_studio_contador_bn=fields.Integer()
    x_studio_contador_color=fields.Integer()
    x_studio_fecha_de_entrega=fields.Datetime()
    x_studio_fecha_de_uso=fields.Datetime()
    x_name=fields.Char()
    x_studio_field_yS42B=fields.Char()
    x_studio_modelo=fields.Char()
    x_studio_numero_de_parte=fields.Char()
    x_studio_ticket=fields.Char()
    x_esRefaccionDeTechra=fields.Boolean()
    x_studio_creado_por_script=fields.Boolean()
    x_ultimaCargaRefacciones=fields.Boolean()



#mensajeTituloGlobal = ''
#mensajeCuerpoGlobal = ''


listaTipoDeVale = [('Falla','Falla'),
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
def cambiaTipoDeVale(idEquipo):
    listaEquiposDeCoordinadoras = [11]
    if idEquipo in listaEquiposDeCoordinadoras:
            listaTipoDeVale = [('Mantenimiento Preventivo', 'Mantenimiento Preventivo')]
            #return listaTipoDeVale
    else:
            listaTipoDeVale = [('Falla','Falla'),
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
    return listaTipoDeVale

idTeamGlobal = 11


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds


class helpdesk_update(models.Model):
    #_inherit = ['mail.thread', 'helpdesk.ticket']
    _inherit = 'helpdesk.ticket'

    x_studio_tipo_de_vale = fields.Selection(listaTipoDeVale, store = True, track_visibility = 'onchange')
    #x_studio_tipo_de_vale = fields.Selection(lambda self: self._obtenerId(), store = True, track_visibility = 'onchange')
    """
    @api.onchange('team_id')
    def _obtenerId(self):
        _logger.info('3312: ' + str(cambiaTipoDeVale(self.team_id.id)))
        return cambiaTipoDeVale(self.team_id.id)
    """


    def creaDiagnosticoVistaLista(self, comentario, estado):
        #_logger.info('SElf de creaDiagnosticoVistaLista: ' + str(self))
        objTicket = self.env['helpdesk.ticket'].search([['id', '=', self.x_studio_id_ticket]], order='create_date desc', limit=1)
        listaDiagnosticos = [(5, 0, 0)]
        listaDeFechas = []
        listaDeUsuariosCreadores = []
        for record in self:
            if record.diagnosticos:
                for diagnostico in record.diagnosticos:
                    listaDiagnosticos.append((0, 0, {
                                                        'ticketRelacion': int(diagnostico.ticketRelacion.x_studio_id_ticket),
                                                        'estadoTicket': diagnostico.estadoTicket,
                                                        'evidencia': [(6, 0, diagnostico.evidencia.ids)],
                                                        'mostrarComentario': diagnostico.mostrarComentario,
                                                        'write_uid':  diagnostico.write_uid.id,
                                                        'comentario': str(diagnostico.comentario),
                                                        'create_date': diagnostico.create_date,
                                                        'create_uid': diagnostico.create_uid.id,
                                                        'creadoPorSistema': diagnostico.creadoPorSistema
                                                    }))
                    listaDeFechas.append(diagnostico.create_date)
                    listaDeUsuariosCreadores.append(diagnostico.create_uid.id)
            comentarioGenerico = comentario
            listaDiagnosticos.append((0, 0, {
                                                'ticketRelacion': int(self.x_studio_id_ticket),
                                                'estadoTicket': estado,
                                                'mostrarComentario': True,
                                                'write_uid':  self.env.user.id,
                                                'create_uid': self.env.user.id,
                                                'comentario': comentarioGenerico,
                                                'creadoPorSistema': True
                                            }))
            objTicket.write({'diagnosticos': listaDiagnosticos})
            _logger.info('3312 listaDeFechas: ' + str(listaDeFechas))
            if listaDeFechas:
                i = 0
                for fecha in listaDeFechas:
                    query = "update helpdesk_diagnostico set create_date = '" + str(fecha.strftime('%Y-%m-%d %H:%M:%S')) + "' where id = " + str(objTicket.diagnosticos[i].id) + ";"
                    self.env.cr.execute(query)
                    query = "update helpdesk_diagnostico set create_uid = " + str(listaDeUsuariosCreadores[i]) + " where id = " + str(objTicket.diagnosticos[i].id) + ";"
                    self.env.cr.execute(query)
                    #query = "update helpdesk_diagnostico set \"creadoPorSistema\" = '" + 't' + "' where id = " + str(objTicket.diagnosticos[i].id) + ";"
                    #self.env.cr.execute(query)
                    objTicket.diagnosticos[i].create_date = fecha
                    i = i + 1
        objTicket.obten_ulimo_diagnostico_fecha_usuario()

    

    tipoDeReporteTechra = fields.Text(
                                        string = 'Tipo de reporte techra'
                                    )
    estadoTicketTechra = fields.Text(
                                        string = 'Estado ticket techra'
                                    )
    nombreTfsTechra = fields.Text(
                                        string = 'Nombre TFS techra'
                                    )
    descripcionDelReporteTechra = fields.Text(
                                        string = 'Descripción del reporte techra'
                                    )
    obsAdicionalesTechra = fields.Text(
                                        string = 'Observaciones adicionales techra'
                                    )
    esTicketDeTechra = fields.Boolean(
                                        string = 'Es ticket de techra?',
                                        default = False
                                    )
    numTicketDeTechra = fields.Text(
                                        string = 'Número de ticket de techra'
                                    )
    numeroDeSerieTechra = fields.Text(
                                        string = 'Número de serie techra'
                                    )
    areaDeAtencionTechra = fields.Text(
                                        string = 'Área de atención techra'
                                    )
    




    esProspecto = fields.Boolean(string = '¿Es ticket de cliente prospecto?', default = False)
    clienteProspectoText = fields.Text(string = 'Nombre del cliente prospecto')
    comentarioClienteProspecto = fields.Text(string = 'Comentario cliente prospecto')



    resuelto_el = fields.Datetime(string = 'Resuelto el')
    cerrado_el = fields.Datetime(string = 'Cerrado_el')
    instalado_el = fields.Datetime(string = 'Fecha de instalación', store=True)

    ticketValidadoElDia = fields.Datetime(string = 'Fecha de validación de la solicitud')

    primerDiagnosticoUsuario = fields.Text(string = 'Primer diagnósticos', compute='_compute_primer_diagnostico')


    def _compute_primer_diagnostico(self):
        for rec in self:
            diagnosticoUsuario = ''
            for diagnostico in rec.diagnosticos:
                if not diagnostico.creadoPorSistema:
                    diagnosticoUsuario = str(diagnostico.comentario)
                    break
            rec.primerDiagnosticoUsuario = diagnosticoUsuario



    #priority = fields.Selection([('all','Todas'),('baja','Baja'),('media','Media'),('alta','Alta'),('critica','Critica')])
    x_studio_field_6furK = fields.Selection([('CHIHUAHUA','CHIHUAHUA'), ('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')], string = 'Zona localidad', store = True, track_visibility='onchange')
    x_studio_zona = fields.Selection([('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur'),('CHIHUAHUA','CHIHUAHUA')], string = 'Zona', store = True, track_visibility='onchange')
    zona_estados = fields.Selection([('Estado de México','Estado de México'), ('Campeche','Campeche'), ('Ciudad de México','Ciudad de México'), ('Yucatán','Yucatán'), ('Guanajuato','Guanajuato'), ('Puebla','Puebla'), ('Coahuila','Coahuila'), ('Sonora','Sonora'), ('Tamaulipas','Tamaulipas'), ('Oaxaca','Oaxaca'), ('Tlaxcala','Tlaxcala'), ('Morelos','Morelos'), ('Jalisco','Jalisco'), ('Sinaloa','Sinaloa'), ('Nuevo León','Nuevo León'), ('Baja California','Baja California'), ('Nayarit','Nayarit'), ('Querétaro','Querétaro'), ('Tabasco','Tabasco'), ('Hidalgo','Hidalgo'), ('Chihuahua','Chihuahua'), ('Quintana Roo','Quintana Roo'), ('Chiapas','Chiapas'), ('Veracruz','Veracruz'), ('Michoacán','Michoacán'), ('Aguascalientes','Aguascalientes'), ('Guerrero','Guerrero'), ('San Luis Potosí', 'San Luis Potosí'), ('Colima','Colima'), ('Durango','Durango'), ('Baja California Sur','Baja California Sur'), ('Zacatecas','Zacatecas')], track_visibility='onchange', store=True)
    estatus_techra = fields.Selection([('Cerrado','Cerrado'), ('Cancelado','Cancelado'), ('Cotización','Cotización'), ('Tiempo de espera','Tiempo de espera'), ('COTIZACION POR AUTORIZAR POR CLIENTE','COTIZACION POR AUTORIZAR POR CLIENTE'), ('Facturar','Facturar'), ('Refacción validada','Refacción validada'), ('Instalación','Instalación'), ('Taller','Taller'), ('En proceso de atención','En proceso de atención'), ('En Pedido','En Pedido'), ('Mensaje','Mensaje'), ('Resuelto','Resuelto'), ('Reasignación de área','Reasignación de área'), ('Diagnóstico de Técnico','Diagnóstico de Técnico'), ('Entregado','Entregado'), ('En Ruta','En Ruta'), ('Listo para entregar','Listo para entregar'), ('Espera de Resultados','Espera de Resultados'), ('Solicitud de refacción','Solicitud de refacción'), ('Abierto TFS','Abierto TFS'), ('Reparación en taller','Reparación en taller'), ('Abierto Mesa de Ayuda','Abierto Mesa de Ayuda'), ('Reabierto','Reabierto')], track_visibility='onchange', store=True)
    priority = fields.Selection([('0','Todas'),('1','Baja'),('2','Media'),('3','Alta'),('4','Critica')], track_visibility='onchange')
    x_studio_equipo_por_nmero_de_serie = fields.Many2many('stock.production.lot', store=True, track_visibility='onchange')
    x_studio_equipo_por_nmero_de_serie_1 = fields.One2many('dcas.dcas', 'x_studio_tiquete', store=True, track_visibility='onchange')
    #x_studio_equipo_por_nmero_de_serieRel = fields.Many2one('stock.production.lot', store=True)
    x_studio_empresas_relacionadas = fields.Many2one('res.partner', store=True, track_visibility='onchange', string='Localidad')
    #historialCuatro = fields.One2many('x_historial_helpdesk','x_id_ticket',string='historial de ticket estados',store=True,track_visibility='onchange')
    documentosTecnico = fields.Many2many('ir.attachment', string="Evidencias")
    stage_id = fields.Many2one('helpdesk.stage', string='Stage', ondelete='restrict', track_visibility='onchange',group_expand='_read_group_stage_ids',readonly=True,copy=False,index=True, domain="[('team_ids', '=', team_id)]")
    productos = fields.One2many('product.product','id',string='Solicitudes',store=True)
    #seriesDCA = fields.One2many('dcas.dcas', 'tickete', string="Series")
    requisicion=fields.Boolean()
    validarTicket = fields.Boolean(
                                    string = "Proceder a realizar la validacón del encargado", 
                                    default = False, 
                                    store = True
                                )
    validarHastaAlmacenTicket = fields.Boolean(
                                                string = "Crear y validar la solicitud de tóner", 
                                                default = False, 
                                                store = True
                                            )
    ponerTicketEnEspera = fields.Boolean(
                                            string = "Generar ticket en espera", 
                                            default = False, 
                                            store = True
                                        )

    almacenes = fields.Many2one(
                                    'stock.warehouse',
                                    store = True,
                                    track_visibility = 'onchange',
                                    string = 'Almacén'
                                )

    contactoInterno = fields.Many2one('res.partner', string = 'Contacto interno', default=False, store = True)

    esReincidencia = fields.Boolean(string = "¿Es reincidencia?", default = False, store = True)
    ticketDeReincidencia = fields.Text(string = 'Ticket de provenencia', store = True)

    days_difference = fields.Integer(compute='_compute_difference',string='días de atraso')
    x_studio_field_nO7Xg = fields.Many2one('sale.order')

    x_studio_fecha_prevista = fields.Datetime(string = 'Fecha Prevista')
    x_studio_fecha_nota = fields.Char(string='Fecha Nota', readonly=True)
    x_studio_field_XALSC = fields.Many2one('stock.picking', string = 'Transferir dis')
    

    

    
    def _get_dominio_localida_contacto(self):
        res = [] 
        vals = {}
        #for record in self:
        if self.partner_id.id:
            hijos = self.env['res.partner'].search([['parent_id', '=', self.partner_id.id]])
            hijosarr = hijos.mapped('id')
            nietos = self.env['res.partner'].search([['parent_id', 'in', hijosarr], ['type', '=', 'contact']]).mapped('id')
            hijosF = hijos.filtered(lambda x: x.type == 'contact').mapped('id')
            final = nietos + hijosF
            res = [('id', 'in', final)]
            vals['dominio_contacto_localidad'] = str(final)
        if vals:
            self.write(vals)

    
    @api.model
    def _get_dominio_localida_contacto_2(self):
        res = [] 
        vals = {}
        #for record in self:
        if self.partner_id.id:
            hijos = self.env['res.partner'].search([['parent_id', '=', self.partner_id.id]])
            hijosarr = hijos.mapped('id')
            nietos = self.env['res.partner'].search([['parent_id', 'in', hijosarr], ['type', '=', 'contact']]).mapped('id')
            hijosF = hijos.filtered(lambda x: x.type == 'contact').mapped('id')
            final = nietos + hijosF
            res = [('id', 'in', final)]
            
            contactos = self.env['res.partner'].search( res ).mapped('id')

            return contactos

    dominio_contacto_localidad = fields.Text(string = 'Dominio de localidad', default = lambda self: self._get_dominio_localida_contacto_2())


    localidadContacto = fields.Many2one('res.partner'
                                        , store = True
                                        , track_visibility = 'onchange'
                                        , string = 'Localidad contacto'
                                        #default = _get_dominio_localida_contacto_2
                                        #default = lambda self: self._get_dominio_localida_contacto_2()
                                        #, compute = 'cambiaContactoLocalidad'
                                        #, domain = "[('id', 'in', dominio_contacto_localidad )]"
                                        , domain = "['&',('parent_id.id','=',idLocalidadAyuda),('type','=','contact')]"

                                        )

    
            
    
    #@api.depends('x_studio_equipo_por_nmero_de_serie')
    @api.onchange('x_studio_equipo_por_nmero_de_serie')
    def cambiaContactoLocalidad(self):
        #_logger.info("aaaaaaaaaaaaaaaa cambiaContactoLocalidad()")
        #_logger.info("aaaaaaaaaaaaaaaa self.localidadContacto:" + str(self.localidadContacto))
        #_logger.info("aaaaaaaaaaaaaaaa self.x_studio_tipo_de_vale:" + str(self.x_studio_tipo_de_vale))
        #if self.team_id.id != 8:
        if self.x_studio_tipo_de_vale != 'Requerimiento':
            if self.x_studio_empresas_relacionadas and not self.localidadContacto:
                #_logger.info("Entre por toner: " + str(self.x_studio_empresas_relacionadas))
                loc = self.x_studio_empresas_relacionadas.id
                #idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_subtipo', '=', 'Contacto de localidad']], order='create_date desc', limit=1).id
                idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_ultimo_contacto', '=', True]], order='create_date desc', limit=1).id
                self.localidadContacto = idLoc
                self.x_studio_field_6furK = self.x_studio_empresas_relacionadas.x_studio_field_SqU5B
                #_logger.info("Entre por toner idLoc: " + str(idLoc))
                if idLoc:
                    #query = "update helpdesk_ticket set \"localidadContacto\" = " + str(idLoc) + " where id = " + str(self.x_studio_id_ticket) + ";"
                    query = "update helpdesk_ticket set \"localidadContacto\" = " + str(idLoc) + ", \"x_studio_field_6furK\" = '" + str(self.x_studio_empresas_relacionadas.x_studio_field_SqU5B) + "' where id = " + str(self.x_studio_id_ticket) + ";"
                    self.env.cr.execute(query)
                    self.env.cr.commit()
                else:
                    idLoc = self.env['res.partner'].search([['parent_id', '=', loc]], order='create_date desc', limit = 1).id
                    self.localidadContacto = idLoc
                    query = "update helpdesk_ticket set \"localidadContacto\" = " + str(idLoc) + ", \"x_studio_field_6furK\" = '" + str(self.x_studio_empresas_relacionadas.x_studio_field_SqU5B) + "' where id = " + str(self.x_studio_id_ticket) + ";"
                    self.env.cr.execute(query)
                    self.env.cr.commit()
                    

    @api.model
    def _contacto_definido(self):
        if self.x_studio_empresas_relacionadas:
            loc = self.x_studio_empresas_relacionadas.id
            return self.env['res.partner'].search([['parent_id', '=', loc],['subtipo' '=', 'Contacto de localidad']], order='create_date desc', limit=1).id


    

    tipoDeDireccion = fields.Selection([('contact','Contacto'),('invoice','Dirección de facturación'),('delivery','Dirección de envío'),('other','Otra dirección'),('private','Dirección Privada')], default='contact')
    subtipo = fields.Selection([('Contacto comercial','Contacto comercial'),('Contacto sistemas','Contacto sistemas'),('Contacto para pagos','Contacto parra pagos'),('Contacto para compras','Contacto para compras'),('private','Dirección Privada')])
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
    direccionCiudad = fields.Char(string='Ciudad')
    direccionCodigoPostal = fields.Char(string='Código postal')
    direccionPais = fields.Many2one('res.country', store=True, string='País')
    direccionEstado = fields.Many2one('res.country.state', store=True, string='Estado', domain="[('country_id', '=?', direccionPais)]")
    
    direccionZona = fields.Selection([('SUR','SUR'),('NORTE','NORTE'),('PONIENTE','PONIENTE'),('ORIENTE','ORIENTE'),('CENTRO','CENTRO'),('DISTRIBUIDOR','DISTRIBUIDOR'),('MONTERREY','MONTERREY'),('CUERNAVACA','CUERNAVACA'),('GUADALAJARA','GUADALAJARA'),('QUERETARO','QUERETARO'),('CANCUN','CANCUN'),('VERACRUZ','VERACRUZ'),('PUEBLA','PUEBLA'),('TOLUCA','TOLUCA'),('LEON','LEON'),('COMODIN','COMODIN'),('VILLAHERMOSA','VILLAHERMOSA'),('MERIDA','MERIDA'),('ALTAMIRA','ALTAMIRA'),('COMODIN','COMODIN'),('DF00','DF00'),('SAN LP','SAN LP'),('ESTADO DE MÉXICO','ESTADO DE MÉXICO'),('Foraneo Norte','Foraneo Norte'),('Foraneo Sur','Foraneo Sur')])
    
    agregarContactoCheck = fields.Boolean(string="Añadir contacto", default=False)
    
    idLocalidadAyuda = fields.Integer(compute='_compute_id_localidad',string='Id Localidad Ayuda', store=False) 
    user_id = fields.Many2one('res.users','Ejecutivo', default=lambda self: self.env.user.id)
    ultimoEvidencia = fields.Many2many('ir.attachment', string="Ultima evidencia",readonly=True,store=False)    
    cambiarDatosClienteCheck = fields.Boolean(string="Editar cliente", default=False, track_visibility='onchange')
    
    team_id = fields.Many2one('helpdesk.team', store = True, copied = True, index = True, string = 'Área de atención', default = 9)



    #@api.model
    #def _tipo_de_reporte_default(self):
    #    _logger.info('self.team_id.id: ' + str(self.team_id.id))
    #    if self.team_id.id == 8:
    #        return 'Requerimiento'



    x_studio_tipo_de_vale = fields.Selection(
        [["Falla","Falla"],["Incidencia","Incidencia"],["Reeincidencia","Reeincidencia"],["Prefunta","Pregunta"],["Requerimiento","Requerimiento"],["Solicitud de refacción","Solicitud de refacción"],["Conectividad","Conectividad"],["Reincidencias","Reincidencias"],["Instalación","Instalación"],["Mantenimiento Preventivo","Mantenimiento Preventivo"],["IMAC","IMAC"],["Proyecto","Proyecto"],["Retiro de equipo","Retiro de equipo"],["Cambio","Cambio"],["Servicio de Software","Servicio de Software"],["Resurtido de Almacen","Resurtido de Almacen"],["Supervisión","Supervisión"],["Demostración","Demostración"],["Toma de lectura","Toma de lectura"]],
        string = 'Tipo de reporte',
        default = 'Requerimiento',
        track_visibility = 'onchange',
        store = True
        )


    #name = fields.Text(string = 'Descripción del reporte', default = lambda self: self._compute_descripcion())
    name = fields.Text(string = 'Descripción del reporte')

    abiertoPor = fields.Text(string = 'Ticket abierto por', store = True, default = lambda self: self.env.user.name)

    clienteContactos = fields.Many2one('res.partner', string = 'Contactos de cliente', store = True)

    idClienteAyuda = fields.Integer(compute = '_compute_id_cliente', store = True)

    @api.depends('partner_id')
    def _compute_id_cliente(self):
        for record in self:
            if record.partner_id:
                record['idClienteAyuda'] = record.partner_id.id

    x_studio_contadores = fields.Text(string = 'Contadores Anteriores', store = True, default = lambda self: self.contadoresAnteriores())

    contadores_anteriores = fields.Text(string = 'Contadores Anteriores', store = True, default = lambda self: self.contadoresAnteriores())

    @api.model
    def contadoresAnteriores(self):
        if self.x_studio_equipo_por_nmero_de_serie and self.team_id.id != 8:
            dominio_ultimo_contador = [('serie', '=', self.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
            dominio_ultimo_contador = [('serie', '=', self.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
            ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
            _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

            if ultimo_contador_techra and ultimo_contador_odoo:
                if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                    if str(ultimo_contador_techra.x_studio_color_o_bn) == 'Color':
                        return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_techra.contadorColor)
                    if str(ultimo_contador_techra.x_studio_color_o_bn) == 'B/N':
                        return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono)
                else:
                    if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'Color':
                        return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_odoo.contadorColor)
                    if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'B/N':
                        return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono)
            elif ultimo_contador_techra and not ultimo_contador_odoo:
                if str(ultimo_contador_techra.x_studio_color_o_bn) == 'Color':
                        return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_techra.contadorColor)
                if str(ultimo_contador_techra.x_studio_color_o_bn) == 'B/N':
                    return 'Equipo B/N o Color: ' + str(ultimo_contador_techra.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_techra.contadorMono)
            elif ultimo_contador_odoo and not ultimo_contador_techra:
                if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'Color':
                        return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono) + '</br>Contador Color: ' + str(ultimo_contador_odoo.contadorColor)
                if str(ultimo_contador_odoo.x_studio_color_o_bn) == 'B/N':
                    return 'Equipo B/N o Color: ' + str(ultimo_contador_odoo.x_studio_color_o_bn) + '</br>Contador B/N: ' + str(ultimo_contador_odoo.contadorMono)
            else:
                return 'Equipo sin contador'


    datos_ticket_info = fields.Text(string = 'Datos ticket')

    @api.onchange('create_date', 'abiertoPor', 'ultimoDiagnosticoFecha', 'ultimoDiagnosticoUsuario', 'days_difference', 'x_studio_nmero_de_ticket_cliente', 'x_studio_tipo_de_vale', 'priority', 'serie_y_modelo', 'contadores_anteriores', 'datosCliente', 'x_studio_ultima_nota', 'x_studio_ultima_evidencia', 'team_id', 'stage_id', 'localidadContacto', 'contactoInterno', 'x_studio_nmero_de_guia_1', 'x_studio_tcnico', 'x_studio_field_nO7Xg')
    def datos_ticket(self):
        lista_datos = []
        fecha_creacion = self.mapped('create_date')
        ticket_abierto_por = self.mapped('abiertoPor')
        fecha_ultimo_cambio = self.mapped('ultimoDiagnosticoFecha')
        ultima_escritura = self.mapped('ultimoDiagnosticoUsuario')
        dias_de_atraso = self.mapped('days_difference')
        numero_ticket_cliente = self.mapped('x_studio_nmero_de_ticket_cliente')
        tipo_de_vale = self.mapped('x_studio_tipo_de_vale')
        prioridad = self.mapped('priority')
        serie_modelo = self.mapped('serie_y_modelo')
        contadores_anteriores = self.mapped('contadores_anteriores')
        datos_cliente = self.mapped('datosCliente')
        ultima_nota = self.mapped('x_studio_ultima_nota')
        ultima_evidencia = self.mapped('x_studio_ultima_evidencia')
        area_de_atencion = self.mapped('team_id.name')
        etapa = self.mapped('stage_id.name')
        localidad_contacto = self.mapped('localidadContacto.name')
        contacto_interno = self.mapped('contactoInterno')
        numero_guia = self.mapped('x_studio_nmero_de_guia_1')
        tecnico = self.mapped('x_studio_tcnico.name')
        #productos = self.mapped('x_studio_productos.name')
        pedido_de_venta = self.mapped('x_studio_field_nO7Xg.name')
        timezone = pytz.timezone('America/Mexico_City')

        """
        _logger.info('fecha_creacion: ' + str(fecha_creacion) + 
                    ' ticket_abierto_por: ' + str(ticket_abierto_por) + 
                    ' ticket_abierto_por: ' + str(ticket_abierto_por) + 
                    ' fecha_ultimo_cambio: ' + str(fecha_ultimo_cambio) + 
                    ' ultima_escritura: ' + str(ultima_escritura) + 
                    ' dias_de_atraso: ' + str(dias_de_atraso) + 
                    ' numero_ticket_cliente: ' + str(numero_ticket_cliente) + 
                    ' tipo_de_vale: ' + str(tipo_de_vale) + 
                    ' prioridad: ' + str(prioridad) + 
                    ' serie_modelo: ' + str(serie_modelo) + 
                    ' contadores_anteriores: ' + str(contadores_anteriores) + 
                    ' datos_cliente: ' + str(datos_cliente) + 
                    ' ultima_nota: ' + str(ultima_nota) + 
                    ' ultima_evidencia: ' + str(ultima_evidencia) + 
                    ' area_de_atencion: ' + str(area_de_atencion) + 
                    ' etapa: ' + str(etapa) + 
                    ' localidad_contacto: ' + str(localidad_contacto) + 
                    ' contacto_interno: ' + str(contacto_interno) + 
                    ' numero_guia: ' + str(numero_guia) + 
                    ' tecnico: ' + str(tecnico) + 
                    ' pedido_de_venta: ' + str(pedido_de_venta))
        """

        if fecha_creacion[0]:
            #_logger.info('fecha_creacion_region: ' + str(fecha_creacion[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S")  ))
            lista_datos.append(str( fecha_creacion[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S") ))  #str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        if ticket_abierto_por[0]:
            lista_datos.append(str(ticket_abierto_por))
        if fecha_ultimo_cambio[0]:
            lista_datos.append(str( fecha_ultimo_cambio[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S") ))
        if ultima_escritura[0]:
            lista_datos.append(str(ultima_escritura))
        if dias_de_atraso:
            lista_datos.append(str(dias_de_atraso))
        if numero_ticket_cliente[0]:
            lista_datos.append(str(numero_ticket_cliente))
        if tipo_de_vale[0]:
            lista_datos.append(str(tipo_de_vale))
        if prioridad:
            lista_datos.append(str(prioridad))
        if serie_modelo[0]:
            lista_datos.append(str(serie_modelo))
        if contadores_anteriores[0]:
            lista_datos.append(str(contadores_anteriores))
            #if str('Equipo sin contador') in str(contadores_anteriores):
            #    lista_datos.append(str(contadores_anteriores))
            #else:
            #    lista_datos.append(str(contadores_anteriores).split('Equipo B/N o Color: ')[1].split('</br>Contador')[0]  )
            #lista_datos.append(str(contadores_anteriores.split('Equipo BN o Color:')[1].split('</br></br> Contador')[0]  ))
        if datos_cliente:
            lista_datos.append(str(datos_cliente))
        if ultima_nota[0]:
            lista_datos.append(str(ultima_nota))
        if ultima_evidencia[0]:
            lista_datos.append(str(ultima_evidencia))
        if area_de_atencion:
            lista_datos.append(str(area_de_atencion))
        if etapa:
            lista_datos.append(str(etapa))
        if localidad_contacto:
            lista_datos.append(str(localidad_contacto))
        if contacto_interno:
            lista_datos.append(str(contacto_interno))
        if numero_guia[0]:
            lista_datos.append(str(numero_guia))
        if tecnico:
            lista_datos.append(str(tecnico))
        #if productos:
        #    lista_datos.append(str(productos))
        if pedido_de_venta:
            lista_datos.append(str(pedido_de_venta))

        if lista_datos:
            vals = {
                'datos_ticket_info': str(lista_datos)
            }
            if 'NewId' in str(self[0]):
                obj_ticket = self.env['helpdesk.ticket'].search([('id', '=', self._origin.id)])
                obj_ticket.write(vals)
            else:
                self.datos_ticket_info = str(lista_datos)



    def datos_ticket_2(self):
        id_a_buscar = 0
        if self and 'NewId' in str(self[0]):
            id_a_buscar = self._origin.id
        else:
            id_a_buscar = self.id

        obj_ticket = self.env['helpdesk.ticket'].search([('id', '=', id_a_buscar)])
        lista_datos = []
        fecha_creacion = obj_ticket.mapped('create_date')
        ticket_abierto_por = obj_ticket.mapped('abiertoPor')
        fecha_ultimo_cambio = obj_ticket.mapped('ultimoDiagnosticoFecha')
        ultima_escritura = obj_ticket.mapped('ultimoDiagnosticoUsuario')
        dias_de_atraso = obj_ticket.mapped('days_difference')
        numero_ticket_cliente = obj_ticket.mapped('x_studio_nmero_de_ticket_cliente')
        tipo_de_vale = obj_ticket.mapped('x_studio_tipo_de_vale')
        prioridad = obj_ticket.mapped('priority')
        serie_modelo = obj_ticket.mapped('serie_y_modelo')
        contadores_anteriores = obj_ticket.mapped('contadores_anteriores')
        datos_cliente = obj_ticket.mapped('datosCliente')
        ultima_nota = obj_ticket.mapped('x_studio_ultima_nota')
        ultima_evidencia = obj_ticket.mapped('x_studio_ultima_evidencia')
        area_de_atencion = obj_ticket.mapped('team_id.name')
        etapa = obj_ticket.mapped('stage_id.name')
        localidad_contacto = obj_ticket.mapped('localidadContacto.name')
        contacto_interno = obj_ticket.mapped('contactoInterno')
        numero_guia = obj_ticket.mapped('x_studio_nmero_de_guia_1')
        tecnico = obj_ticket.mapped('x_studio_tcnico.name')
        #productos = obj_ticket.mapped('x_studio_productos.name')
        pedido_de_venta = obj_ticket.mapped('x_studio_field_nO7Xg.name')
        timezone = pytz.timezone('America/Mexico_City')

        """
        _logger.info('fecha_creacion: ' + str(fecha_creacion) + 
                    ' ticket_abierto_por: ' + str(ticket_abierto_por) + 
                    ' ticket_abierto_por: ' + str(ticket_abierto_por) + 
                    ' fecha_ultimo_cambio: ' + str(fecha_ultimo_cambio) + 
                    ' ultima_escritura: ' + str(ultima_escritura) + 
                    ' dias_de_atraso: ' + str(dias_de_atraso) + 
                    ' numero_ticket_cliente: ' + str(numero_ticket_cliente) + 
                    ' tipo_de_vale: ' + str(tipo_de_vale) + 
                    ' prioridad: ' + str(prioridad) + 
                    ' serie_modelo: ' + str(serie_modelo) + 
                    ' contadores_anteriores: ' + str(contadores_anteriores) + 
                    ' datos_cliente: ' + str(datos_cliente) + 
                    ' ultima_nota: ' + str(ultima_nota) + 
                    ' ultima_evidencia: ' + str(ultima_evidencia) + 
                    ' area_de_atencion: ' + str(area_de_atencion) + 
                    ' etapa: ' + str(etapa) + 
                    ' localidad_contacto: ' + str(localidad_contacto) + 
                    ' contacto_interno: ' + str(contacto_interno) + 
                    ' numero_guia: ' + str(numero_guia) + 
                    ' tecnico: ' + str(tecnico) + 
                    ' pedido_de_venta: ' + str(pedido_de_venta))
        """

        if fecha_creacion[0]:
            #_logger.info('fecha_creacion_region: ' + str(fecha_creacion[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S")  ))
            lista_datos.append(str( fecha_creacion[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S") ))  #str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        if ticket_abierto_por[0]:
            lista_datos.append(str(ticket_abierto_por))
        if fecha_ultimo_cambio[0]:
            lista_datos.append(str( fecha_ultimo_cambio[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S") ))
        if ultima_escritura[0]:
            lista_datos.append(str(ultima_escritura))
        if dias_de_atraso:
            lista_datos.append(str(dias_de_atraso))
        if numero_ticket_cliente[0]:
            lista_datos.append(str(numero_ticket_cliente))
        if tipo_de_vale[0]:
            lista_datos.append(str(tipo_de_vale))
        if prioridad:
            lista_datos.append(str(prioridad))
        if serie_modelo[0]:
            lista_datos.append(str(serie_modelo))
        if contadores_anteriores[0]:
            lista_datos.append(str(contadores_anteriores))
            #if str('Equipo sin contador') in str(contadores_anteriores):
            #    lista_datos.append(str(contadores_anteriores))
            #else:
            #    lista_datos.append(str(contadores_anteriores).split('Equipo B/N o Color: ')[1].split('</br>Contador')[0]  )
            #lista_datos.append(str(contadores_anteriores.split('Equipo BN o Color:')[1].split('</br></br> Contador')[0]  ))
        if datos_cliente:
            lista_datos.append(str(datos_cliente))
        if ultima_nota[0]:
            lista_datos.append(str(ultima_nota))
        if ultima_evidencia[0]:
            lista_datos.append(str(ultima_evidencia))
        if area_de_atencion:
            lista_datos.append(str(area_de_atencion))
        if etapa:
            lista_datos.append(str(etapa))
        if localidad_contacto:
            lista_datos.append(str(localidad_contacto))
        if contacto_interno:
            lista_datos.append(str(contacto_interno))
        if numero_guia[0]:
            lista_datos.append(str(numero_guia))
        if tecnico:
            lista_datos.append(str(tecnico))
        #if productos:
        #    lista_datos.append(str(productos))
        if pedido_de_venta:
            lista_datos.append(str(pedido_de_venta))

        if lista_datos:
            vals = {
                'datos_ticket_info': str(lista_datos)
            }
            obj_ticket.write(vals)


    def datos_ticket_llenar_por_fuera(self):
        obj_ticket = self.env['helpdesk.ticket'].search([('id', '=', self.id)])
        lista_datos = []
        fecha_creacion = obj_ticket.mapped('create_date')
        ticket_abierto_por = obj_ticket.mapped('abiertoPor')
        fecha_ultimo_cambio = obj_ticket.mapped('ultimoDiagnosticoFecha')
        ultima_escritura = obj_ticket.mapped('ultimoDiagnosticoUsuario')
        dias_de_atraso = obj_ticket.mapped('days_difference')
        numero_ticket_cliente = obj_ticket.mapped('x_studio_nmero_de_ticket_cliente')
        tipo_de_vale = obj_ticket.mapped('x_studio_tipo_de_vale')
        prioridad = obj_ticket.mapped('priority')
        serie_modelo = obj_ticket.mapped('serie_y_modelo')
        contadores_anteriores = obj_ticket.mapped('contadores_anteriores')
        datos_cliente = obj_ticket.mapped('datosCliente')
        ultima_nota = obj_ticket.mapped('x_studio_ultima_nota')
        ultima_evidencia = obj_ticket.mapped('x_studio_ultima_evidencia')
        area_de_atencion = obj_ticket.mapped('team_id.name')
        etapa = obj_ticket.mapped('stage_id.name')
        localidad_contacto = obj_ticket.mapped('localidadContacto.name')
        contacto_interno = obj_ticket.mapped('contactoInterno')
        numero_guia = obj_ticket.mapped('x_studio_nmero_de_guia_1')
        tecnico = obj_ticket.mapped('x_studio_tcnico.name')
        #productos = obj_ticket.mapped('x_studio_productos.name')
        pedido_de_venta = obj_ticket.mapped('x_studio_field_nO7Xg.name')
        timezone = pytz.timezone('America/Mexico_City')

        """
        _logger.info('fecha_creacion: ' + str(fecha_creacion) + 
                    ' ticket_abierto_por: ' + str(ticket_abierto_por) + 
                    ' ticket_abierto_por: ' + str(ticket_abierto_por) + 
                    ' fecha_ultimo_cambio: ' + str(fecha_ultimo_cambio) + 
                    ' ultima_escritura: ' + str(ultima_escritura) + 
                    ' dias_de_atraso: ' + str(dias_de_atraso) + 
                    ' numero_ticket_cliente: ' + str(numero_ticket_cliente) + 
                    ' tipo_de_vale: ' + str(tipo_de_vale) + 
                    ' prioridad: ' + str(prioridad) + 
                    ' serie_modelo: ' + str(serie_modelo) + 
                    ' contadores_anteriores: ' + str(contadores_anteriores) + 
                    ' datos_cliente: ' + str(datos_cliente) + 
                    ' ultima_nota: ' + str(ultima_nota) + 
                    ' ultima_evidencia: ' + str(ultima_evidencia) + 
                    ' area_de_atencion: ' + str(area_de_atencion) + 
                    ' etapa: ' + str(etapa) + 
                    ' localidad_contacto: ' + str(localidad_contacto) + 
                    ' contacto_interno: ' + str(contacto_interno) + 
                    ' numero_guia: ' + str(numero_guia) + 
                    ' tecnico: ' + str(tecnico) + 
                    ' pedido_de_venta: ' + str(pedido_de_venta))
        """

        if fecha_creacion[0]:
            #_logger.info('fecha_creacion_region: ' + str(fecha_creacion[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S")  ))
            lista_datos.append(str( fecha_creacion[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S") ))  #str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        if ticket_abierto_por[0]:
            lista_datos.append(str(ticket_abierto_por))
        if fecha_ultimo_cambio[0]:
            lista_datos.append(str( fecha_ultimo_cambio[0].astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S") ))
        if ultima_escritura[0]:
            lista_datos.append(str(ultima_escritura))
        if dias_de_atraso:
            lista_datos.append(str(dias_de_atraso))
        if numero_ticket_cliente[0]:
            lista_datos.append(str(numero_ticket_cliente))
        if tipo_de_vale[0]:
            lista_datos.append(str(tipo_de_vale))
        if prioridad:
            lista_datos.append(str(prioridad))
        if serie_modelo[0]:
            lista_datos.append(str(serie_modelo))
        if contadores_anteriores[0]:
            lista_datos.append(str(contadores_anteriores))
            #if str('Equipo sin contador') in str(contadores_anteriores):
            #    lista_datos.append(str(contadores_anteriores))
            #else:
            #    lista_datos.append(str(contadores_anteriores).split('Equipo B/N o Color: ')[1].split('</br>Contador')[0]  )
            #lista_datos.append(str(contadores_anteriores.split('Equipo BN o Color:')[1].split('</br></br> Contador')[0]  ))
        if datos_cliente:
            lista_datos.append(str(datos_cliente))
        if ultima_nota[0]:
            lista_datos.append(str(ultima_nota))
        if ultima_evidencia[0]:
            lista_datos.append(str(ultima_evidencia))
        if area_de_atencion:
            lista_datos.append(str(area_de_atencion))
        if etapa:
            lista_datos.append(str(etapa))
        if localidad_contacto:
            lista_datos.append(str(localidad_contacto))
        if contacto_interno:
            lista_datos.append(str(contacto_interno))
        if numero_guia[0]:
            lista_datos.append(str(numero_guia))
        if tecnico:
            lista_datos.append(str(tecnico))
        #if productos:
        #    lista_datos.append(str(productos))
        if pedido_de_venta:
            lista_datos.append(str(pedido_de_venta))

        if lista_datos:
            vals = {
                'datos_ticket_info': str(lista_datos)
            }
            obj_ticket.write(vals)
            return 1
        return -1


    def agrega_refacciones_en_accesorios(self):
        if self.x_studio_productos and len(self.accesorios) == 0:
            lista = [[5,0,0]]
            #listaDeCantidades = []
            for refaccion in self.x_studio_productos:
                if refaccion.product_variant_id.id:
                    vals = {
                        'productos': refaccion.product_variant_id.id,
                        'cantidadPedida': refaccion.x_studio_cantidad_pedida
                    }
                    lista.append( [0, 0, vals] )
                    #listaDeCantidades.append(refaccion.cantidadPedida)
            #_logger.info('3312: lista2: ' + str(lista))
            self.write({'accesorios': lista})
            return 1
        return -1


    def selecciona_contacto_de_localidad(self):
        localidad = self.mapped('x_studio_empresas_relacionadas')
        localidad_contacto = self.mapped('localidadContacto')
        _logger.info('localidad: ' + str(localidad) + ' localidad_contacto: ' + str(localidad_contacto))
        if localidad and not localidad_contacto:
            dominio_localidad_contacto = self.cambiosParent_id()
            _logger.info('dominio_localidad_contacto: ' + str(dominio_localidad_contacto))
            if dominio_localidad_contacto:
                loc = localidad[0].id
                #idLoc = self.env['res.partner'].search([['parent_id', '=', loc],['x_studio_subtipo', '=', 'Contacto de localidad']], order='create_date desc', limit=1).id
                idLoc = self.env['res.partner'].search(dominio_localidad_contacto['domain']['localidadContacto'], order = 'create_date desc', limit = 1).id
                _logger.info('idLoc: ' + str(idLoc))
                if idLoc:
                    #query = "update helpdesk_ticket set \"localidadContacto\" = " + str(idLoc) + " where id = " + str(rec.x_studio_id_ticket) + ";"
                    #self.env.cr.execute(query)
                    #self.env.cr.commit()
                    self.write({'localidadContacto': idLoc})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('helpdesk_name')
        #vals['team_id'] = 8
        #_logger.info("Informacion 0.0: " + str(vals))

        ticket = super(helpdesk_update, self).create(vals)

        if ticket.x_studio_tipo_de_vale != 'Requerimiento' and not ticket.x_studio_equipo_por_nmero_de_serie:
            query = "select helpdesk_team_id from helpdesk_team_res_users_rel where res_users_id = " + str(self.env.user.id) + ";"
            self.env.cr.execute(query)
            resultadoQuery = self.env.cr.fetchall()
            puedoCrearSinSerie = False
            for resultado in resultadoQuery:
                if resultado[0] == 9:
                    puedoCrearSinSerie = True
                    break
            if not puedoCrearSinSerie:
                raise exceptions.ValidationError('El usuario no es de mesa de Servicio y no tiene los permisos para crear un ticket sin serie.')



        if ticket.x_studio_tipo_de_vale == 'Requerimiento' and not ticket.x_studio_equipo_por_nmero_de_serie_1:
            raise exceptions.ValidationError('No es posible registrar ticket de requerimiento sin serie.')

        if ticket.x_studio_tipo_de_vale == 'Requerimiento' and ticket.x_studio_equipo_por_nmero_de_serie_1:
            ticket.write({'stage_id': 89}) #estado abierto si tiene serie

        if ticket.x_studio_tipo_de_vale != 'Requerimiento' and ticket.x_studio_equipo_por_nmero_de_serie:
            ticket.write({'stage_id': 89})

        #ticket.sudo().actualiza_datos_cliente()

        #_logger.info("Informacion 1: " + str(ticket.x_studio_equipo_por_nmero_de_serie_1))
        #_logger.info("Informacion 2: " + str(ticket.x_studio_equipo_por_nmero_de_serie))
        ticket.x_studio_id_ticket = ticket.id
        ticket.abiertoPor = self.env.user.name
        ticket.user_id = self.env.user.id

        if self.x_studio_empresas_relacionadas:
            ticket.x_studio_field_6furK = ticket.x_studio_empresas_relacionadas.x_studio_field_SqU5B
            ticket.write({'x_studio_field_6furK': ticket.x_studio_empresas_relacionadas.x_studio_field_SqU5B})
        #_logger.info("Informacion 3: " + str(ticket))
        if ticket.x_studio_equipo_por_nmero_de_serie:
            if (ticket.team_id.id != 8 and ticket.team_id.id != 13) and len(ticket.x_studio_equipo_por_nmero_de_serie) == 1:
                #ticket.write({'contadores_anteriores': '</br>Equipo BN o Color: ' + str(ticket.x_studio_equipo_por_nmero_de_serie[0].x_studio_color_bn) + ' </br></br> Contador BN: ' + str(ticket.x_studio_equipo_por_nmero_de_serie[0].x_studio_contador_bn_mesa) + '</br></br> Contador Color: ' + str(ticket.x_studio_equipo_por_nmero_de_serie[0].x_studio_contador_color_mesa)})
                regresa = ticket.contadoresAnteriores()
                ticket.write({'contadores_anteriores': regresa})
        if ticket.x_studio_tipo_de_vale == 'Requerimiento' and ticket.team_id.id != 8 and ticket.team_id.id != 13:
            ticket.write({'team_id': 8})

        
        #Ultimo contacto para requerimiento
        #_logger.info('ticket.localidadContacto: ' + str(ticket.localidadContacto))
        if not ticket.localidadContacto:
            idContact=False
            if ticket.x_studio_empresas_relacionadas:
                idContact = self.env['res.partner'].search([['parent_id', '=', ticket.x_studio_empresas_relacionadas.id],['x_studio_ultimo_contacto', '=', True]], order='create_date desc', limit=1)
            #_logger.info('idContact: ' + str(idContact))
            if idContact:
                vals = {
                    'localidadContacto': idContact.id
                }
                ticket.write(vals)
            else:
                ticket.selecciona_contacto_de_localidad()


        ticket.actualiza_serie_texto()
        ticket.actualiza_todas_las_zonas()
        #ticket.cambiosParent_id()
        #ticket._get_dominio_localida_contacto()
        ticket.datos_ticket()
        return ticket


    
    def write(self, vals):

        #_logger.info('vals en write: ' + str(vals))
        #_logger.info('self en write:' +str(self) )

        if 'x_studio_tipo_de_vale' in vals:
            if (self.x_studio_tipo_de_vale != 'Requerimiento' and vals['x_studio_tipo_de_vale'] != 'Resurtido de Almacen' and vals['x_studio_tipo_de_vale'] != 'Conectividad') and not self.x_studio_equipo_por_nmero_de_serie:
                query = "select helpdesk_team_id from helpdesk_team_res_users_rel where res_users_id = " + str(self.env.user.id) + ";"
                self.env.cr.execute(query)
                resultadoQuery = self.env.cr.fetchall()
                puedoCrearSinSerie = False
                for resultado in resultadoQuery:
                    if resultado[0] == 9:
                        puedoCrearSinSerie = True
                        break
                if not puedoCrearSinSerie:
                    raise exceptions.ValidationError('El usuario no es de mesa de Servicio y no tiene los permisos para crear un ticket sin serie.')
       


        if self and 'NewId' in str(self[0]):
        #if not self.ids:
            result = super(helpdesk_update, self._origin).write(vals)
            #_logger.info('result en write: ' + str(result))
            return result

        result = super(helpdesk_update, self).write(vals)
        #_logger.info('result en write: ' + str(result))
        

        #if 'active' in vals:
        #    self.with_context(active_test=False).mapped('ticket_ids').write({'active': vals['active']})
        #self.sudo()._check_sla_group()
        #self.sudo()._check_modules_to_install()
        # If you plan to add something after this, use a new environment. The one above is no longer valid after the modules install.



        return result

    """
    @api.model
    def _compute_descripcion(self):

        return 'Ticket ' + str(self.x_studio_id_ticket)
    """
    

    def open_to_form_view(self):
 
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
            'res_id': self.id,
            'nodestroy': True
        }


    #contadorBNWizard = fields.Integer(string = 'Contador B/N generado desde wizard', default = 0)
    #contadorColorWizard = fields.Integer(string = 'Contador Color generado desde wizard', default = 0)


    #@api.onchange('x_studio_equipo_por_nmero_de_serie')
    #def actualiza_contadores_lista(self):
    #    if self.team_id != 8 and len(self.x_studio_equipo_por_nmero_de_serie) == 1:
    #        self.x_studio_contadores = '</br> Equipo BN o Color: ' + str(self.x_studio_equipo_por_nmero_de_serie[0].x_studio_color_bn) + ' </br></br> Contador BN: ' + str(self.x_studio_equipo_por_nmero_de_serie[0].x_studio_contador_bn_mesa) + '</br></br> Contador Color: ' + str(self.x_studio_equipo_por_nmero_de_serie[0].x_studio_contador_color_mesa)
            

    """
    @api.depends('x_studio_equipo_por_nmero_de_serie', 'x_studio_ultima_nota', 'contadorBNWizard', 'contadorColorWizard')
    def actualiza_contadores_lista(self):
        for r in self:
            if r.contadorBNWizard == 0 or r.contadorColorWizard == 0:
                if r.team_id != 8 and len(r.x_studio_equipo_por_nmero_de_serie) == 1:
                    r['x_studio_contadores'] = '</br> Equipo BN o Color: ' + str(r.x_studio_equipo_por_nmero_de_serie[0].x_studio_color_bn) + ' </br> Contador BN: ' + str(r.x_studio_equipo_por_nmero_de_serie[0].x_studio_contador_bn_mesa) + '</br> Contador Color: ' + str(r.x_studio_equipo_por_nmero_de_serie[0].x_studio_contador_color_mesa)
            else:
                if r.team_id != 8 and len(r.x_studio_equipo_por_nmero_de_serie) == 1:
                    r['x_studio_contadores'] = '</br> Equipo BN o Color: ' + str(r.x_studio_equipo_por_nmero_de_serie[0].x_studio_color_bn) + ' </br> Contador BN: ' + str(r.contadorBNWizard) + '</br> Contador Color: ' + str(r.contadorColorWizard)
                    r['contadorBNWizard'] = 0
                    r['contadorColorWizard'] = 0
    """

    telefonoClienteContacto = fields.Text(string = 'Telefono de contacto cliente', compute = '_compute_telefonoCliente')
    movilClienteContacto = fields.Text(string = 'Movil de contacto cliente', compute = '_compute_movilCliente')
    correoClienteContacto = fields.Text(string = 'Correo de contacto cliente', compute = '_compute_correoCliente')

    
    @api.depends('clienteContactos')
    def _compute_telefonoCliente(self):
        if self.clienteContactos:
            self.telefonoClienteContacto = self.clienteContactos.phone

    
    @api.depends('clienteContactos')
    def _compute_movilCliente(self):
        if self.clienteContactos:
            self.movilClienteContacto = self.clienteContactos.mobile

    
    @api.depends('clienteContactos')
    def _compute_correoCliente(self):
        if self.clienteContactos:
            self.correoClienteContacto = self.clienteContactos.email


    telefonoLocalidadContacto = fields.Text(string = 'Telefono de localidad', compute = '_compute_telefonoLocalidad')
    movilLocalidadContacto = fields.Text(string = 'Movil de localidad', compute = '_compute_movilLocalidad')
    correoLocalidadContacto = fields.Text(string = 'Correo de localidad', compute = '_compute_correoLocalidad')
    direccionLocalidadText = fields.Text(string = 'Dirección localidad', compute = '_compute_direccionLocalidad')

    #
    
    @api.depends('x_studio_empresas_relacionadas')
    def _compute_direccionLocalidad(self):
        for record in self:
            #_logger.info("test: " + str(record.x_studio_empresas_relacionadas.id))
            #localidadData = self.env['res.partner'].search([['id', '=', self.x_studio_empresas_relacionadas.id]])
            #_logger.info("test: " + str(localidadData))
            if record.x_studio_empresas_relacionadas:
                record.direccionLocalidadText = """
                                                <address>
                                                    Calle: """ + str(record.x_studio_empresas_relacionadas.street_name) + """
                                                    </br>
                                                    Número exterior: """ + str(record.x_studio_empresas_relacionadas.street_number) + """
                                                    </br>
                                                    Número interior: """ + str(record.x_studio_empresas_relacionadas.street_number2) + """
                                                    </br>
                                                    Colonia: """ + str(record.x_studio_empresas_relacionadas.l10n_mx_edi_colony) + """
                                                    </br>
                                                    Alcaldía: """ + str(record.x_studio_empresas_relacionadas.city) + """
                                                    </br>
                                                    Estado: """ + str(record.x_studio_empresas_relacionadas.state_id.name) + """
                                                    </br>
                                                    Código postal: """ + str(record.x_studio_empresas_relacionadas.zip) + """
                                                    </br>
                                                </address>
                                            """

    
    @api.depends('localidadContacto')
    def _compute_telefonoLocalidad(self):
        if self.localidadContacto:
            self.telefonoLocalidadContacto = self.localidadContacto.phone

    
    @api.depends('localidadContacto')
    def _compute_movilLocalidad(self):
        if self.localidadContacto:
            self.movilLocalidadContacto = self.localidadContacto.mobile

    
    @api.depends('localidadContacto')
    def _compute_correoLocalidad(self):
        if self.localidadContacto:
            self.correoLocalidadContacto = self.localidadContacto.email

    datosCliente = fields.Text(string="Cliente datos", compute='_compute_datosCliente')

    @api.depends('x_studio_equipo_por_nmero_de_serie','x_studio_equipo_por_nmero_de_serie_1', 'contactoInterno')
    def _compute_datosCliente(self):
        for rec in self:
            

            nombreCliente = str(rec.partner_id.name)
            if nombreCliente == 'False':
                nombreCliente = 'No disponible'
            
            localidad = str(rec.x_studio_empresas_relacionadas.name)
            if localidad == 'False':
                localidad = 'No disponible'
            
            contactoDeLocalidad = str(rec.localidadContacto.name)
            if contactoDeLocalidad == 'False':
                contactoDeLocalidad = 'No disponible'
            elif rec.contactoInterno:
                if rec.contactoInterno.name:
                    contactoDeLocalidad = rec.contactoInterno.name
                else:
                    contactoDeLocalidad = 'No disponible'
                

            estadoLocalidad = str(rec.x_studio_estado_de_localidad)
            if estadoLocalidad == 'False':
                estadoLocalidad = 'No disponible'

            zonaLocalidad = str(rec.x_studio_field_6furK)
            if zonaLocalidad == 'False':
                zonaLocalidad = 'No disponible'
            
            telefonoLocalidad = str(rec.telefonoLocalidadContacto)
            if telefonoLocalidad == 'False':
                telefonoLocalidad = 'No disponible'
            elif rec.contactoInterno:
                if rec.contactoInterno.phone:
                    telefonoLocalidad = rec.contactoInterno.phone
                else:
                    telefonoLocalidad = 'No disponible'

            movilLocalidad = str(rec.movilLocalidadContacto)
            if movilLocalidad == 'False':
                movilLocalidad = 'No disponible'
            elif rec.contactoInterno:
                if rec.contactoInterno.mobile:
                    movilLocalidad = rec.contactoInterno.mobile
                else:
                    movilLocalidad = 'No disponible'

            correoElectronicoLocalidad = str(rec.correoLocalidadContacto)
            if correoElectronicoLocalidad == 'False':
                correoElectronicoLocalidad = 'No disponible'
            elif rec.contactoInterno:
                if rec.contactoInterno.email:
                    correoElectronicoLocalidad = rec.contactoInterno.email
                else:
                    correoElectronicoLocalidad = 'No disponible'
            
            datos = 'Cliente: ' + nombreCliente + ' \nLocalidad: ' + localidad + ' \nLocalidad contacto: ' + contactoDeLocalidad + ' \nEstado de localidad: ' + estadoLocalidad + '\nZona localidad: ' + zonaLocalidad + ' \nTeléfono de localidad: ' + telefonoLocalidad + ' \nMóvil localidad contacto: ' + movilLocalidad + ' \nCorreo electrónico localidad contacto: ' + correoElectronicoLocalidad
            #datos = 'Cliente: ' + nombreCliente + ' \nLocalidad: ' + localidad + ' \nLocalidad contacto: ' + contactoDeLocalidad + ' \nEstado de localidad: ' + estadoLocalidad 

            rec.datosCliente = datos




    #ticketRelacion = fields.Char(string = "Ticket", related = self)


    #numeroDeGuiaDistribucion = fields.Char(string='Número de guía generado por distribución', store=True)
    
    """
    seriesDeEquipoPorNumeroDeSerie = fields.Selection(_compute_series,compute='_compute_series',string='Series agregadas', store=False)
    
    @api.depends('x_studio_equipo_por_nmero_de_serie')
    def _compute_series(self):
        listaDeSeries = []
        for record in self:
            if len(record.x_studio_equipo_por_nmero_de_serie) > 0:
                for serie in record.x_studio_equipo_por_nmero_de_serie:
                    listaDeSerie.append((str(serie.name),str(serie.name)))
        return listaDeSerie
    """


    backorderActivo = fields.Boolean(string = '¿Tiene backorder?', compute = '_compute_backorderActivo')
    mensajeBackOrder = fields.Text(string = 'Mensaje backorder', compute = '_compute_backorderActivo')

    #@api.depends('x_studio_backorders')
    def _compute_backorderActivo(self):
        for rec in self:
            if rec.x_studio_backorder:
            #if rec.x_studio_backorders:
                rec.backorderActivo = True
                #rec.write({'backorderActivo': True})
                rec.mensajeBackOrder = """
                                            <div class='row'>
                                                <div class='col-sm-12'>
                                                    <div class="alert alert-info" role="alert">
                                                        <h4 class="alert-heading">Existe backorder</h4>
                                                        <p>Advertencia, este ticket cuenta con solicitudes de almacen pendientes.</p>
                                                        <hr>
                                                        <p class="mb-0"> </p>
                                                    </div>
                                                </div>
                                            </div>
                                        """
                #rec.write({'mensajeBackOrder': mensajeBackOrder})
            else:
                rec.backorderActivo = False
                rec.mensajeBackOrder = """ """
                #rec.write({'backorderActivo': False})
                #rec.write({'mensajeBackOrder': ' '})
    
    
    @api.depends('x_studio_empresas_relacionadas')
    def _compute_id_localidad(self):
        for record in self:
            record['idLocalidadAyuda'] = record.x_studio_empresas_relacionadas.id
            
    @api.onchange('x_studio_empresas_relacionadas')
    def cambiar_direccion_entrega(self):
        
        sale = self.x_studio_field_nO7Xg
        #if self.x_studio_field_nO7Xg != False and (self.x_studio_empresas_relacionadas.id == False or self.x_studio_empresas_relacionadas.id != None or len(str(self.x_studio_empresas_relacionadas.id)) != 0 or str(self.x_studio_empresas_relacionadas.id) is 0 or not str(self.x_studio_empresas_relacionadas.id) or self.x_studio_empresas_relacionadas.id != []) and self.x_studio_field_nO7Xg.state != 'sale':
        if self.x_studio_field_nO7Xg.id != False and self.x_studio_id_ticket != 0 and self.x_studio_field_nO7Xg.state != 'sale':
            
            
            if self.x_studio_field_nO7Xg.id != False and self.x_studio_empresas_relacionadas:
                #self.env['sale.order'].write(['partner_shipping_id','=',''])
                self.env.cr.execute("update sale_order set partner_shipping_id = " + str(self.x_studio_empresas_relacionadas.id) + " where  id = " + str(sale.id) + ";")
                #raise Warning('Se cambio la dirreción de entrega del ticket: ' + str(self.id) + " dirección actualizada a: " + str(self.x_studio_empresas_relacionadas.name))
                #raise exceptions.Warning('Se cambio la dirreción de entrega del ticket: ' + str(self.x_studio_id_ticket) + " dirección actualizada a: " + str(self.x_studio_empresas_relacionadas.parent_id.name) + " " + str(self.x_studio_empresas_relacionadas.name))
                message = ('Se cambio la dirreción de entrega de la solicitud: ' + str(sale.name) + '  del ticket: ' + str(self.x_studio_id_ticket) + ". \nSe produjo el cambio al actualizar el campo 'Localidad'. \nLa dirección fue actualizada a: " + str(self.x_studio_empresas_relacionadas.parent_id.name) + " " + str(self.x_studio_empresas_relacionadas.name))
                mess= {
                        'title': _('Dirreción Actualizada!!!'),
                        'message' : message
                    }
                return {'warning': mess}
            else:
                raise exceptions.Warning('Se intento actualizar la dirrección de entrega, pero cocurrio un error debido a que no existe el campo "Pedido de venta" o no existe el campo "Localidad". \n\nFavor de verificar que no esten vacios estos campos.')
        else:
            if self.x_studio_id_ticket != 0 and self.x_studio_field_nO7Xg.id != False:
                raise exceptions.Warning('No se pudo actualizar la dirreción de la solicitud: ' + str(sale.name) + ' del ticket: ' + str(self.x_studio_id_ticket) + " debido a que ya fue validada la solicitud. \nIntento actualizar el campo 'Localidad' con la dirección: " + str(self.x_studio_empresas_relacionadas.parent_id.name) + " " + str(self.x_studio_empresas_relacionadas.name))
                
                
    
    def regresarAte(self):
        estado = self.stage_id.name
        #if estado == 'Atención':
        query="update helpdesk_ticket set stage_id = 13 where id = '" + str(self.x_studio_id_ticket) + "';" 
        self.env.cr.execute(query)
        self.env.cr.commit()
        message = ('Se cambio el estado ')
        mess= {
                'title': _('Estado  Actualizado a Atencion!!!'),
                'message' : message
              }
        return {'warning': mess}              
            
    
    def agregarContactoALocalidad(self):
        
        if self.x_studio_empresas_relacionadas.id != 0:
            contactoId = 0;
            
            titulo = ''
            if len(self.titulo) == 0: 
                titulo = '' 
            else: 
                titulo = self.titulo.id
                
            if self.tipoDeDireccion == "contact" and self.nombreDelContacto != False:
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.x_studio_empresas_relacionadas.id
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
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.x_studio_empresas_relacionadas.id
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
                contacto = self.sudo().env['res.partner'].create({'parent_id' : self.x_studio_empresas_relacionadas.id
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
                errorContactoSinNombre = "Contacto sin nombre"
                mensajeContactoSinNombre = "No es posible añadir un contacto sin nombre. Favor de indicar el nombre primero."
                raise exceptions.except_orm(_(errorContactoSinNombre), _(mensajeContactoSinNombre))
                
            self.env.cr.commit()
            if contactoId > 0:
                errorContactoGenerado = "Contacto agregado"
                mensajeContactoGenerado = "Contacto " + str(self.nombreDelContacto) + " agregado a la localidad " + str(self.x_studio_empresas_relacionadas.name)
                raise exceptions.except_orm(_(errorContactoGenerado), _(mensajeContactoGenerado))
                self.agregarContactoCheck = False
            else:
                errorContactoNoGenerado = "Contacto no agregado"
                mensajeContactoNoGenerado = "Contacto no agregado. Favor de verificar la información ingresada."
                raise exceptions.except_orm(_(errorContactoNoGenerado), _(mensajeContactoNoGenerado))
        else:
            errorContactoSinLocalidad = "Contacto sin localidad"
            mensajeContactoSinLocalidad = "No es posible añadir un contacto sin primero indicar la localidad. Favor de indicar la localidad primero."
            raise exceptions.except_orm(_(errorContactoSinLocalidad), _(mensajeContactoSinLocalidad))
    
    
    """
    def convert_timedelta(duration):
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return hours, minutes, seconds
    """
    
    # Ticket compuatado de tiempos

    def _compute_difference(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #rec.days_difference = (datetime.date.today()- rec.create_date).days
                #fe = ''
                fecha = str(rec.create_date).split(' ')[0]
                #fe = t[0]
                converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                #converted_date = datetime.datetime.strptime(str(rec.create_date), '%Y-%m-%d').date()
                rec.days_difference = (datetime.date.today() - converted_date).days
    

    hour_differenceTicket = fields.Integer(
                                                compute='_compute_difference_hour_ticket',
                                                string='Horas de atraso ticket'
                                            )
    def _compute_difference_hour_ticket(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                first_time = rec.create_date
                later_time = datetime.datetime.now()
                difference = later_time - first_time
                hours, minutes, seconds = convert_timedelta(difference)
                rec.hour_differenceTicket = hours

    minutes_differenceTicket = fields.Integer(
                                                compute='_compute_difference_minute_ticket',
                                                string='Minutos de atraso ticket'
                                            )
    def _compute_difference_minute_ticket(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                first_time = rec.create_date
                later_time = datetime.datetime.now()
                difference = later_time - first_time
                hours, minutes, seconds = convert_timedelta(difference)
                rec.minutes_differenceTicket = minutes

    seconds_differenceTicket = fields.Integer(
                                                compute='_compute_difference_second_ticket',
                                                string='Segundos de atraso ticket'
                                            )
    def _compute_difference_second_ticket(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                first_time = rec.create_date
                later_time = datetime.datetime.now()
                difference = later_time - first_time
                hours, minutes, seconds = convert_timedelta(difference)
                rec.seconds_differenceTicket = seconds


    tiempoDeAtrasoTicket = fields.Text(
                                            string = 'Tiempo de atraso ticket',
                                            compute = '_compute_tiempo_atraso_ticket'
                                        )
    def _compute_tiempo_atraso_ticket(self):
        self.tiempoDeAtrasoTicket = """
                                        <div class='row'>
                                            <div class='col-sm-12'>
                                                <p>
                                                """ + str(self.days_difference) + """ día(s) con 
                                                """ + str(self.hour_differenceTicket) + """: 
                                                """ + str(self.minutes_differenceTicket) + """:
                                                """ + str(self.seconds_differenceTicket) + """
                                                </p>
                                            </div>
                                        </div>
                                    """



    
    # Almacen compuatado de tiempos
    days_differenceAlmacen = fields.Integer(
                                                compute='_compute_difference_days_almacen',
                                                string='Días de atraso almacén'
                                            )
    def _compute_difference_days_almacen(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_nO7Xg and (rec.x_studio_field_up5pO == 'confirmed' or rec.x_studio_field_up5pO == 'assigned'):
                if rec.stage_id.id == 93 or rec.stage_id.id == 112:
                    fecha = str(rec.create_date).split(' ')[0]
                    #fe = t[0]
                    converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                    #converted_date = datetime.datetime.strptime(str(rec.create_date), '%Y-%m-%d').date()
                    rec.days_differenceAlmacen = (datetime.date.today() - converted_date).days

    hour_differenceAlmacen = fields.Integer(
                                                compute='_compute_difference_hour_almacen',
                                                string='Horas de atraso almacén'
                                            )
    def _compute_difference_hour_almacen(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_nO7Xg and (rec.x_studio_field_up5pO == 'confirmed' or rec.x_studio_field_up5pO == 'assigned'):
                if rec.stage_id.id == 93 or rec.stage_id.id == 112:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.hour_differenceAlmacen = hours

    minutes_differenceAlmacen = fields.Integer(
                                                compute='_compute_difference_minute_almacen',
                                                string='Minutos de atraso almacén'
                                            )
    def _compute_difference_minute_almacen(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_nO7Xg and (rec.x_studio_field_up5pO == 'confirmed' or rec.x_studio_field_up5pO == 'assigned'):
                if rec.stage_id.id == 93 or rec.stage_id.id == 112:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.minutes_differenceAlmacen = minutes

    seconds_differenceAlmacen = fields.Integer(
                                                compute='_compute_difference_second_almacen',
                                                string='Segundos de atraso almacén'
                                            )
    def _compute_difference_second_almacen(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_nO7Xg and (rec.x_studio_field_up5pO == 'confirmed' or rec.x_studio_field_up5pO == 'assigned'):
                if rec.stage_id.id == 93 or rec.stage_id.id == 112:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.seconds_differenceAlmacen = seconds


    tiempoDeAtrasoAlmacen = fields.Text(
                                            string = 'Tiempo de atraso almacén',
                                            compute = '_compute_tiempo_atraso_almacen'
                                        )
    def _compute_tiempo_atraso_almacen(self):
        self.tiempoDeAtrasoAlmacen = """
                                        <div class='row'>
                                            <div class='col-sm-12'>
                                                <p>
                                                """ + str(self.days_differenceAlmacen) + """ día(s) con 
                                                """ + str(self.hour_differenceAlmacen) + """:
                                                """ + str(self.minutes_differenceAlmacen) + """:
                                                """ + str(self.seconds_differenceAlmacen) + """:
                                                </p>
                                            </div>
                                        </div>
                                    """

    # Distribucion compuatado de tiempos
    days_differenceDistribucion = fields.Integer(
                                                compute='_compute_difference_days_distribucion',
                                                string='Días de atraso distibución'
                                            )
    def _compute_difference_days_distribucion(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_nO7Xg and (rec.x_studio_field_Le2tN == 'confirmed' or rec.x_studio_field_Le2tN == 'assigned' or rec.x_studio_field_Le2tN == 'distribucion'):
                if rec.stage_id.id == 112 or rec.stage_id.id == 94:
                    fecha = str(rec.create_date).split(' ')[0]
                    converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                    rec.days_differenceDistribucion = (datetime.date.today() - converted_date).days

    hour_differenceDistribucion = fields.Integer(
                                                compute='_compute_difference_hour_distribucion',
                                                string='Horas de atraso distribución'
                                            )
    def _compute_difference_hour_distribucion(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_nO7Xg and (rec.x_studio_field_Le2tN == 'confirmed' or rec.x_studio_field_Le2tN == 'assigned' or rec.x_studio_field_Le2tN == 'distribucion'):
                if rec.stage_id.id == 112 or rec.stage_id.id == 94:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.hour_differenceDistribucion = hours

    minutes_differenceDistribucion = fields.Integer(
                                                compute='_compute_difference_minute_distribucion',
                                                string='Minutos de atraso distribución'
                                            )
    def _compute_difference_minute_distribucion(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_nO7Xg and (rec.x_studio_field_Le2tN == 'confirmed' or rec.x_studio_field_Le2tN == 'assigned' or rec.x_studio_field_Le2tN == 'distribucion'):
                if rec.stage_id.id == 112 or rec.stage_id.id == 94:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.minutes_differenceDistribucion = minutes

    seconds_differenceDistribucion = fields.Integer(
                                                compute='_compute_difference_second_distribucion',
                                                string='Segundos de atraso distribución'
                                            )
    def _compute_difference_second_distribucion(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_nO7Xg and (rec.x_studio_field_Le2tN == 'confirmed' or rec.x_studio_field_Le2tN == 'assigned' or rec.x_studio_field_Le2tN == 'distribucion'):
                if rec.stage_id.id == 112 or rec.stage_id.id == 94:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.seconds_differenceDistribucion = seconds


    tiempoDeAtrasoDistribucion = fields.Text(
                                            string = 'Tiempo de atraso distribución',
                                            compute = '_compute_tiempo_atraso_distribucion'
                                        )
    def _compute_tiempo_atraso_distribucion(self):
        self.tiempoDeAtrasoDistribucion = """
                                        <div class='row'>
                                            <div class='col-sm-12'>
                                                <p>
                                                """ + str(self.days_differenceDistribucion) + """ día(s) con 
                                                """ + str(self.hour_differenceDistribucion) + """:
                                                """ + str(self.minutes_differenceDistribucion) + """:
                                                """ + str(self.seconds_differenceDistribucion) + """
                                                </p>
                                            </div>
                                        </div>
                                    """

    



    # Repartidor compuatado de tiempos
    
    days_differenceRepartidor = fields.Integer(
                                                    compute='_compute_difference_days_repartidor',
                                                    string='Días de atraso repatidor'
                                                )

    def _compute_difference_days_repartidor(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_up5pO == 'waiting' and rec.x_studio_field_nO7Xg:
                if rec.stage_id.id == 108:
                    fecha = str(rec.create_date).split(' ')[0]
                    converted_date = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                    rec.days_differenceRepartidor = (datetime.date.today() - converted_date).days

    hour_differenceRepartidor = fields.Integer(
                                                compute='_compute_difference_hour_repartidor',
                                                string='Horas de atraso repartidor'
                                            )
    def _compute_difference_hour_repartidor(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_up5pO == 'waiting' and rec.x_studio_field_nO7Xg:
                if rec.stage_id.id == 108:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.hour_differenceRepartidor = hours

    minutes_differenceRepartidor = fields.Integer(
                                                compute='_compute_difference_minute_repartidor',
                                                string='Minutos de atraso repartidor'
                                            )
    def _compute_difference_minute_repartidor(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_up5pO == 'waiting' and rec.x_studio_field_nO7Xg:
                if rec.stage_id.id == 108:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.minutes_differenceRepartidor = minutes

    seconds_differenceRepartidor = fields.Integer(
                                                compute='_compute_difference_second_repartidor',
                                                string='Segundos de atraso repartidor'
                                            )
    def _compute_difference_second_repartidor(self):
        for rec in self:
            if rec.stage_id.id != 18 or rec.stage_id.id != 3 or rec.stage_id.id != 4:
                #if rec.x_studio_field_up5pO == 'waiting' and rec.x_studio_field_nO7Xg:
                if rec.stage_id.id == 108:
                    first_time = rec.create_date
                    later_time = datetime.datetime.now()
                    difference = later_time - first_time
                    hours, minutes, seconds = convert_timedelta(difference)
                    rec.seconds_differenceRepartidor = seconds

    tiempoDeAtrasoRepartidor = fields.Text(
                                            string = 'Tiempo de atraso distribución',
                                            compute = '_compute_tiempo_atraso_repartidor'
                                        )
    def _compute_tiempo_atraso_repartidor(self):
        self.tiempoDeAtrasoRepartidor = """
                                        <div class='row'>
                                            <div class='col-sm-12'>
                                                <p>
                                                """ + str(self.days_differenceRepartidor) + """ día(s) con 
                                                """ + str(self.hour_differenceRepartidor) + """:
                                                """ + str(self.minutes_differenceRepartidor) + """:
                                                """ + str(self.seconds_differenceRepartidor) + """
                                                </p>
                                            </div>
                                        </div>
                                    """


    





    
    #_logger.info("el id xD Toner xD")            

    #@api.model           
    #@api.depends('productosSolicitud')
    #
    """
    def _productos_solicitud_filtro(self):
        res = {}    
        e=''
        g=str(self.x_studio_nombretmp)
        list = ast.literal_eval(g)
        idf = self.team_id.id
        if idf == 8:
            _logger.info("el id xD Toner"+g)            
            e  = str([('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)])
        if idf == 9:
            _logger.info("el id xD Reffacciones"+g)
            e = str([('categ_id', '=', 7),('x_studio_toner_compatible.id','=',list[0])])
        #if idf != 9 and idf != 8:
        #    _logger.info("Compatibles xD"+g)
        #    res['domain']={'productosSolicitud':[('x_studio_toner_compatible.id','=',list[0])]}
        _logger.info(" res :"+str(e))    
        return e

    productosSolicitud = fields.Many2many('product.product', string="Productos Solicitados",domain=_productos_solicitud_filtro)
    """
    
    """
    #@api.depends('historialCuatro')
    @api.onchange('historialCuatro')
    def recuperaUltimaNota(self):
        #for record in self:
        historial = self.historialCuatro
        ultimaFila = len(historial) - 1
        if ultimaFila >= 0:
            self.x_studio_ultima_nota = str(historial[ultimaFila].x_disgnostico)
            self.x_studio_fecha_nota = str(historial[ultimaFila].create_date)
            self.x_studio_tecnico = str(historial[ultimaFila].x_persona)
    """
    
    """
    #@api.depends('historialCuatro')
    @api.onchange('historialCuatro')
    def recuperaUltimaNota(self):
        for record in self:
            historial = record.historialCuatro
            ultimaFila = len(historial) - 1
            if ultimaFila >= 0:
                record['x_studio_ultima_nota'] = str(historial[ultimaFila].x_disgnostico)
                record['x_studio_fecha_nota'] = str(historial[ultimaFila].create_date)
                record['x_studio_tecnico'] = str(historial[ultimaFila].x_persona)
    """                
    
    """
    @api.onchange('x_studio_equipo_por_nmero_de_serie')
    def anadirProductosATabla(self):
        
            Añade productos y el numero de serie que se agregaron al equipor 
            numero de serie a la tabla de productos. 
        
        _logger.info("anadirProductosATabla")
        if len(self.x_studio_equipo_por_nmero_de_serie) > 0:
            data = []
            for numeroDeSerie in self.x_studio_equipo_por_nmero_de_serie:
                data.append({'x_studio_currentuser': 
                           , 'categ_id': 
                           , '':
                            })
                str(numeroDeSerie.name)
                numeroDeSerie.x_studio_field_lMCjm.id
    """                
    
    
    
    
    @api.onchange('x_studio_generar_cambio')
    def genera_registro_contadores(self):
        for record in self:
            if record.x_studio_generar_cambio == True:
                listaDeSeries = record.x_studio_equipo_por_nmero_de_serie
                for serie in listaDeSeries:
                    if serie.x_studio_cambiar == True:
                        contadorColor = serie.x_studio_contador_color
                        raise exceptions.ValidationError(str(contadorColor))
    
    """
    @api.onchange('x_studio_equipo_por_nmero_de_serie')
    def abierto(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo")
            #if self.stage_id.name != 'Abierto':
            if self.stage_id.name == 'Pre-ticket':
                _logger.info("Id ticket: " + str(self.id))
                #query = "update helpdesk_ticket set stage_id = 89 where id = " + str(self.id) + ";"
                query = "update helpdesk_ticket set stage_id = 89 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)
                _logger.info("**********fun: abierto(), estado: " + str(self.stage_id.name))
                #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.id ,'x_persona': self.env.user.name,'x_estado': "Abierto"})
    """
    
    estadoAbierto = fields.Boolean(string="Paso por estado abierto", default=False)
    


    
    @api.onchange('x_studio_equipo_por_nmero_de_serie','x_studio_equipo_por_nmero_de_serie_1')
    def abierto(self):
        #que pasa si hay mas de 1 ticket xD .i ->search([['name', '=', self.name]]).id
        #self.x_studio_id_ticket = self.env['helpdesk.ticket'].search([['name', '=', self.name]]).id
        #_logger.info("id ticket search: " + str(self.x_studio_id_ticket))
        
        #ticketActualiza = self.env['helpdesk.ticket'].search([('id', '=', self.id)])
        if (self.team_id.id == 8 or self.team_id.id == 13) and self.x_studio_tipo_de_vale == 'Requerimiento':
            tam = len(self.x_studio_equipo_por_nmero_de_serie_1)
        else:
            tam = int(self.x_studio_tamao_lista)
        
        
        
        if self.x_studio_id_ticket and tam < 2 and (self.team_id.id == 8 or self.team_id.id == 13) and self.x_studio_tipo_de_vale == 'Requerimiento':
            estadoAntes = str(self.stage_id.name)
            if self.stage_id.name == 'Pre-ticket' and self.x_studio_equipo_por_nmero_de_serie_1[0].serie.id != False and self.estadoAbierto == False:
                #ticketActualiza.write({'stage_id': '89'})
                query = "update helpdesk_ticket set stage_id = 89 where id = " + str(self.x_studio_id_ticket) + ";"
                ss = self.env.cr.execute(query)
                #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': "Abierto", 'write_uid':  self.env.user.name})
                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Abierto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                mess= {
                        'title': _('Estado de ticket actualizado!!!'),
                        'message' : message
                    }
                self.estadoAbierto = True
                #mensajeCuerpoGlobal = 'Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Abierto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página."
                return {'warning': mess}
        
        if self.x_studio_id_ticket and tam < 2 and (self.team_id != 8 and self.team_id.id != 13) and self.x_studio_tipo_de_vale != 'Requerimiento':
            estadoAntes = str(self.stage_id.name)
            if self.stage_id.name == 'Pre-ticket' and self.x_studio_equipo_por_nmero_de_serie.id != False and self.estadoAbierto == False:
                #ticketActualiza.write({'stage_id': '89'})
                query = "update helpdesk_ticket set stage_id = 89 where id = " + str(self.x_studio_id_ticket) + ";"
                ss = self.env.cr.execute(query)

                ultimaEvidenciaTec = []
                ultimoComentario = ''
                if self.diagnosticos:
                    if self.diagnosticos[-1].evidencia.ids:
                        ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                    ultimoComentario = self.diagnosticos[-1].comentario

                #self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.x_studio_id_ticket, 'comentario': ultimoComentario, 'estadoTicket': "Abierto", 'evidencia': [(0,0,ultimaEvidenciaTec)], 'write_uid':  self.env.user.name})

                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Abierto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                mess= {
                        'title': _('Estado de ticket actualizado!!!'),
                        'message' : message
                    }
                self.estadoAbierto = True
                #mensajeCuerpoGlobal = 'Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Abierto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página."
                return {'warning': mess}
                #USAR----
                #raise RedirectWarning('mensaje',400,_('Test'))
                #return objeto
                #return {'id':'24326','model':'helpdesk.ticket','view_type':'form','menu_id':'406'}

    
    
    
    
    
    """
    @api.onchange('team_id')
    def asignacion(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo")
            if self.stage_id.name != 'Asignado':
                query = "update helpdesk_ticket set stage_id = 2 where id = " + str(self.x_studio_id_ticket) + ";"
                _logger.info("lol: " + query)
                ss = self.env.cr.execute(query)             
                _logger.info("**********fun: asignacion(), estado: " + str(self.stage_id.name))                
                #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona':self.env.user.name ,'x_estado': "Asignado"})
        
        res = {}
        idEquipoDeAsistencia = self.team_id.id
        query = "select * from helpdesk_team_res_users_rel where helpdesk_team_id = " + str(idEquipoDeAsistencia) + ";"
        self.env.cr.execute(query)
        informacion = self.env.cr.fetchall()
        _logger.info("*********lol: " + str(informacion))
        listaUsuarios = []
        #res['domain']={'x_studio_productos':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
        for idUsuario in informacion:
            _logger.info("*********idUsuario: " + str(idUsuario))
            listaUsuarios.append(idUsuario[1])
        _logger.info(str(listaUsuarios))
        dominio = [('id', 'in', listaUsuarios)]
        res['domain'] = {'user_id': dominio}
        return res
    """
    #Añadir al XML 
    estadoAsignacion = fields.Boolean(string="Paso por estado asignación", default=False)
    
    def crearDiagnostico():
        if self.diagnosticos:
            #_logger.info("*********************************Entre")
            #_logger.info("*********************************Entre: " + str(self.diagnosticos[-1].evidencia))
            if self.diagnosticos[-1].evidencia.ids:
                ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
            ultimoComentario = self.diagnosticos[-1].comentario
            
            #if self.diagnosticos.evidencia:
            #    ultimaEvidenciaTec += self.diagnosticos.evidencia.ids
            _logger.info("*********************************Entre: " + str(ultimoComentario))

            #self.sudo().write({'diagnosticos': [(0, 0, {'ticketRelacion': self.x_studio_id_ticket, 'comentario': ultimoComentario, 'estadoTicket': "Asignado", 'write_uid':  self.env.user.name})]})
            #self.diagnosticos = [(0, 0, {'ticketRelacion': self.x_studio_id_ticket, 'comentario': ultimoComentario, 'estadoTicket': "Asignado", 'write_uid':  self.env.user.name})]
            diagnosticoCreado = self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.x_studio_id_ticket, 'comentario': ultimoComentario, 'estadoTicket': "Asignado", 'write_uid':  self.env.user.name})
            #for eviden in ultimaEvidenciaTec:
            #    diagnosticoCreado.write({'evidencia': [(4,eviden)] })
            #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': "Asignado", 'write_uid':  self.env.user.name})

    

    @api.onchange('team_id')
    def asignacion(self):
        _logger.info('self al iniciar funcion asignacion: ' + str(self._origin))

        if self._origin.stage_id.id == 3:
            comentarioGenerico = 'Se cambio de área de atención. Área de atención actual: ' + self.team_id.name + '. Seleccion realizada por ' + str(self.env.user.name) +'.'
            estado = 'Resuelto'
            self.creaDiagnosticoVistaLista(comentarioGenerico, estado)
            self.datos_ticket_2()
            mensajeTitulo = 'Cambio de área de atención!!!'
            mensajeCuerpo = 'Se cambiará el área de atención, pero no se permite cambiar al estado de asignación una vez que el ticket esta en el estado Resuelto.'
            mess = {
                    'title': _(mensajeTitulo),
                    'message' : mensajeCuerpo
                }
            return {'warning': mess}

        #for record in self:
        if self._origin.x_studio_id_ticket:
            estadoAntes = str(self._origin.stage_id.name)
            #if self.stage_id.name == 'Abierto' and self.estadoAsignacion == False and self.team_id.id != False:
            if self._origin.team_id.id != False:
                #query = "update helpdesk_ticket set stage_id = 2 where id = " + str(self._origin.x_studio_id_ticket) + ";"
                #ss = self._origin.env.cr.execute(query)
                self._origin.write({'stage_id': 2})

                comentarioGenerico = 'Cambio de estado al seleccionar ' + self._origin.team_id.name + ' como área de atención. Seleccion realizada por ' + str(self.env.user.name) +'.'
                estado = 'Asignado'
                _logger.info('self que envio a funcion creaDiagnosticoVistaLista: ' + str(self._origin))
                #self._origin.creaDiagnosticoVistaLista(comentarioGenerico, estado)
                

                valoresNuevoDiagnostico = {
                                            'ticketRelacion': int(self.x_studio_id_ticket),
                                            'estadoTicket': estado,
                                            'mostrarComentario': True,
                                            'write_uid':  self.env.user.id,
                                            'create_uid': self.env.user.id,
                                            'comentario': comentarioGenerico,
                                            'creadoPorSistema': True
                }
                ids_diagnosticos = self._origin.sudo().diagnosticos.ids
                nuevoDiagnostico = self._origin.env['helpdesk.diagnostico'].sudo().with_env(self.env(user=self.env.user.id)).create(valoresNuevoDiagnostico)
                _logger.info('nuevoDiagnostico: ' + str(nuevoDiagnostico))
                ids_diagnosticos.append(nuevoDiagnostico)
                self._origin.sudo().write({'diagnosticos': [(4, 0, nuevoDiagnostico.id)] })

                
                listaDiagnosticos = [(5, 0, 0)]
                listaDeFechas = []
                listaDeUsuariosCreadores = []
                for diagnostico in self._origin.sudo().diagnosticos:
                    listaDiagnosticos.append((0, 0, {
                                                        'ticketRelacion': int(diagnostico.ticketRelacion.x_studio_id_ticket),
                                                        'estadoTicket': diagnostico.estadoTicket,
                                                        'evidencia': [(6, 0, diagnostico.evidencia.ids)],
                                                        'mostrarComentario': diagnostico.mostrarComentario,
                                                        'write_uid':  diagnostico.write_uid.id,
                                                        'comentario': str(diagnostico.comentario),
                                                        'create_date': diagnostico.create_date,
                                                        'create_uid': diagnostico.create_uid.id,
                                                        'creadoPorSistema': diagnostico.creadoPorSistema
                                                    }))
                    listaDeFechas.append(diagnostico.create_date)
                    listaDeUsuariosCreadores.append(diagnostico.create_uid.id)
                self._origin.sudo().write({'diagnosticos': listaDiagnosticos})
                if listaDeFechas:
                    i = 0
                    for fecha in listaDeFechas:
                        query = "update helpdesk_diagnostico set create_date = '" + str(fecha.strftime('%Y-%m-%d %H:%M:%S')) + "' where id = " + str(self._origin.sudo().diagnosticos[i].id) + ";"
                        self._origin.env.cr.execute(query)
                        query = "update helpdesk_diagnostico set create_uid = " + str(listaDeUsuariosCreadores[i]) + " where id = " + str(self._origin.sudo().diagnosticos[i].id) + ";"
                        self._origin.env.cr.execute(query)
                        #query = "update helpdesk_diagnostico set \"creadoPorSistema\" = '" + 't' + "' where id = " + str(objTicket.diagnosticos[i].id) + ";"
                        #self.env.cr.execute(query)
                        self._origin.sudo().diagnosticos[i].create_date = fecha
                        i = i + 1
                
                self._origin.obten_ulimo_diagnostico_fecha_usuario()
                #for diagnostico in self._origin.sudo().diagnosticos:
                #_logger.info('self._origin.sudo().diagnosticos[-1].create_date: ' + str(self._origin.sudo().diagnosticos[-1].create_date))
                #_logger.info('self._origin.sudo().diagnosticos[-2].create_date: ' + str(self._origin.sudo().diagnosticos[-2].create_date))
                #_logger.info('self._origin.sudo().diagnosticos[-1].comentario: ' + str(self._origin.sudo().diagnosticos[-1].comentario))
                #_logger.info('not self._origin.sudo().diagnosticos[-1].comentario: ' + str(not self._origin.sudo().diagnosticos[-1].comentario))
                #if self._origin.sudo().diagnosticos[-1].create_date == self._origin.sudo().diagnosticos[-2].create_date and not self._origin.sudo().diagnosticos[-1].comentario:
                #    _logger.info('Se creo un diagnostico de mas y lo vohya borrar alv.')
                #    self._origin.sudo().write({'diagnosticos': [(3, self._origin.sudo().diagnosticos[-1].id)]})


                """
                ultimaEvidenciaTec = []
                ultimoComentario = ''
                if self.diagnosticos:
                    if self.diagnosticos[-1].evidencia.ids:
                        ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                    ultimoComentario = self.diagnosticos[-1].comentario
                    
                #_logger.info("*********************************Entre: " + str(ultimoComentario))
                lineas = [(5, 0, 0)]
                if ultimaEvidenciaTec != []:
                    for linea in self.diagnosticos:
                        val = {}
                        if linea.evidencia.ids != []:
                            val = {
                                'ticketRelacion': int(self.x_studio_id_ticket),
                                'comentario': linea.comentario,
                                'estadoTicket': linea.estadoTicket,
                                'evidencia': [(6,0,linea.evidencia.ids)],
                                'mostrarComentario': linea.mostrarComentario
                            }
                        else:
                            val = {
                                'ticketRelacion': int(self.x_studio_id_ticket),
                                'comentario': linea.comentario,
                                'estadoTicket': linea.estadoTicket,
                                'mostrarComentario': linea.mostrarComentario
                            }
                        lineas.append((0, 0, val))
                    lineas.append((0, 0, {'ticketRelacion': int(self.x_studio_id_ticket), 'comentario': ultimoComentario, 'estadoTicket': "Asignado", 'evidencia': [(6,0,ultimaEvidenciaTec)], 'write_uid':  self.env.user.id}))
                else:
                    for linea in self.diagnosticos:
                        val = {}
                        if linea.evidencia.ids != []:
                            val = {
                                'ticketRelacion': int(self.x_studio_id_ticket),
                                'comentario': linea.comentario,
                                'estadoTicket': linea.estadoTicket,
                                'evidencia': [(6,0,linea.evidencia.ids)],
                                'mostrarComentario': linea.mostrarComentario
                            }
                        else:
                            val = {
                                'ticketRelacion': int(self.x_studio_id_ticket),
                                'comentario': linea.comentario,
                                'estadoTicket': linea.estadoTicket,
                                'mostrarComentario': linea.mostrarComentario
                            }
                        lineas.append((0, 0, val))
                    lineas.append((0, 0, {'ticketRelacion': int(self.x_studio_id_ticket), 'comentario': ultimoComentario, 'estadoTicket': "Asignado", 'write_uid':  self.env.user.id}))
                """    
                
                #self.estadoAsignacion = True
                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Asignado' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                mess= {
                        'title': _('Estado de ticket actualizado!!!'),
                        'message' : message
                    }
                
                res = {}
                idEquipoDeAsistencia = self._origin.team_id.id
                query = "select * from helpdesk_team_res_users_rel where helpdesk_team_id = " + str(idEquipoDeAsistencia) + ";"
                self._origin.env.cr.execute(query)
                informacion = self._origin.env.cr.fetchall()
                listaUsuarios = []
                
                for idUsuario in informacion:
                    listaUsuarios.append(idUsuario[1])
                
                dominio = [('id', 'in', listaUsuarios)]
                #comentarioGenerico = 'Cambio de estado al seleccionar ' + self.team_id.name + ' como área de atención. Seleccion realizada por ' + str(self.env.user.name) +'.'
                #estado = 'Asignado'
                #self.creaDiagnosticoVistaLista(comentarioGenerico, estado)

                """
                objTicket = self.env['helpdesk.ticket'].search([['id', '=', self.x_studio_id_ticket]], order='create_date desc', limit=1)
                listaDiagnosticos = [(5, 0, 0)]
                listaDeFechas = []
                if record.diagnosticos:
                    for diagnostico in record.diagnosticos:
                        listaDiagnosticos.append((0, 0, {
                                                            'ticketRelacion': int(diagnostico.ticketRelacion.x_studio_id_ticket),
                                                            'estadoTicket': diagnostico.estadoTicket,
                                                            'evidencia': [(6, 0, diagnostico.evidencia.ids)],
                                                            'mostrarComentario': diagnostico.mostrarComentario,
                                                            'write_uid':  diagnostico.write_uid.id,
                                                            'comentario': str(diagnostico.comentario),
                                                            'create_date': diagnostico.create_date,
                                                            'create_uid': diagnostico.create_uid.id
                                                        }))
                        listaDeFechas.append(diagnostico.create_date)
                comentarioGenerico = 'Cambio de estado al seleccionar ' + self.team_id.name + ' como área de atención. Seleccion realizada por ' + str(self.env.user.name) +'.'
                listaDiagnosticos.append((0, 0, {
                                                    'ticketRelacion': int(self.x_studio_id_ticket),
                                                    'estadoTicket': 'Asignado',
                                                    'mostrarComentario': True,
                                                    'write_uid':  self.env.user.id,
                                                    'create_uid': self.env.user.id,
                                                    'comentario': comentarioGenerico
                                                }))
                objTicket.write({'diagnosticos': listaDiagnosticos})

                i = 0
                for fecha in listaDeFechas:
                    #fechaMX = (fecha - datetime.timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
                    #_logger.info('fechaMX: ' + str(fechaMX))
                    #_logger.info('3312 fecha: ' + str(fecha.strftime('%Y-%m-%d %H:%M:%S')))
                    query = "update helpdesk_diagnostico set create_date = '" + str(fecha.strftime('%Y-%m-%d %H:%M:%S')) + "' where id = " + str(objTicket.diagnosticos[i].id) + ";"
                    self.env.cr.execute(query)
                    objTicket.diagnosticos[i].create_date = fecha
                    i = i + 1
                """
                return {
                        'warning': mess, 
                        'domain': {'user_id': dominio},
                        'value': { 'stage_id': 2 }
                }
                
            #else:
                #reasingado
                
                
        if self._origin.team_id.id != False:
            res = {}
            idEquipoDeAsistencia = self._origin.team_id.id
            query = "select * from helpdesk_team_res_users_rel where helpdesk_team_id = " + str(idEquipoDeAsistencia) + ";"
            self._origin.env.cr.execute(query)
            informacion = self._origin.env.cr.fetchall()
            listaUsuarios = []
            #res['domain']={'x_studio_productos':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
            for idUsuario in informacion:
                listaUsuarios.append(idUsuario[1])
            dominio = [('id', 'in', listaUsuarios)]
            res['domain'] = {'user_id': dominio}
            return res
    
    


    
    """
    @api.onchange('x_studio_tcnico')
    def cambioEstadoAtencion(self):
        if self.x_studio_id_ticket:
            #raise exceptions.ValidationError("error gerardo: " + str(self.stage_id.name))
            #if self.stage_id.name == 'Asignado' and self.stage_id.name != 'Atención':
            query = "update helpdesk_ticket set stage_id = 13 where id = " + str(self.x_studio_id_ticket) + ";"
            _logger.info("lol: " + query)
            ss = self.env.cr.execute(query)
            _logger.info("**********fun: cambioEstadoAtencion(), estado: " + str(self.stage_id.name))
            ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.x_studio_tcnico.name,'x_estado': "Atención"})
    """
    
    
    #Añadir al XML 
    estadoAtencion = fields.Boolean(string="Paso por estado atención", default=False)
    
    @api.onchange('x_studio_tcnico')
    def cambioEstadoAtencion(self):
        if self.stage_id.id == 3:
            tecnicoActual = ''
            if self.x_studio_tcnico.name:
                tecnicoActual = str(self.x_studio_tcnico.name)
            else:
                tecnicoActual = 'Sin técnico asociado'
            comentarioGenerico = 'Se cambio de técnico. Técnico actual: ' + tecnicoActual + '. Seleccion realizada por ' + str(self.env.user.name) +'.'
            estado = 'Resuelto'
            self.creaDiagnosticoVistaLista(comentarioGenerico, estado)
            self.datos_ticket_2()
            mensajeTitulo = 'Cambio de técnico!!!'
            mensajeCuerpo = 'Se cambiará el técnico, pero no se permite cambiar al estado de atención una vez que el ticket esta en el estado Resuelto.'
            mess = {
                    'title': _(mensajeTitulo),
                    'message' : mensajeCuerpo
                }
            return {'warning': mess}


        if self.x_studio_id_ticket:
            estadoAntes = str(self.stage_id.name)
            if (self.stage_id.name == 'Asignado' or self.stage_id.name == 'Resuelto' or self.stage_id.name == 'Cerrado'):
                #query = "update helpdesk_ticket set stage_id = 13 where id = " + str(self.x_studio_id_ticket) + ";"
                #ss = self.env.cr.execute(query)
                self.write({'stage_id': 13})
                ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                ultimaEvidenciaTec = []
                ultimoComentario = ''
                if self.diagnosticos:
                    if self.diagnosticos[-1].evidencia.ids:
                        ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                    ultimoComentario = self.diagnosticos[-1].comentario

                tecnicoActual = ''
                if self.x_studio_tcnico.name:
                    tecnicoActual = str(self.x_studio_tcnico.name)
                else:
                    tecnicoActual = 'Sin técnico asociado'
                comentarioGenerico = 'Cambio de estado al seleccionar botón atención o al cambiar de técnico. Técnico actual: ' + tecnicoActual + '. Se cambio al estado Atención. Seleccion realizada por ' + str(self.env.user.name) +'.'
                
                estado = 'Atención'
                self.creaDiagnosticoVistaLista(comentarioGenerico, estado)
                self.datos_ticket_2()
                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Atención' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                mess= {
                        'title': _('Estado de ticket actualizado!!!'),
                        'message' : message
                    }
                self.estadoAtencion = True
                self.estadoResuelto = False
                return {'warning': mess}
    
    



    def cambioEstadoAtencionAccion(self):
        if self.x_studio_id_ticket:
            estadoAntes = str(self.stage_id.name)
            if (self.stage_id.name == 'Asignado' or self.stage_id.name == 'Resuelto' or self.stage_id.name == 'Cerrado'):
                self.write({'stage_id': 13})
                ultimaEvidenciaTec = []
                ultimoComentario = ''
                if self.diagnosticos:
                    if self.diagnosticos[-1].evidencia.ids:
                        ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                    ultimoComentario = self.diagnosticos[-1].comentario
                tecnicoActual = ''
                if self.x_studio_tcnico.name:
                    tecnicoActual = str(self.x_studio_tcnico.name)
                else:
                    tecnicoActual = 'Sin técnico asociado'
                comentarioGenerico = 'Cambio de estado al seleccionar botón atención o al cambiar de técnico. Técnico actual: ' + tecnicoActual + '. Se cambio al estado Atención. Seleccion realizada por ' + str(self.env.user.name) +'.'
                
                estado = 'Atención'
                self.creaDiagnosticoVistaLista(comentarioGenerico, estado)
                self.datos_ticket_2()
                self.estadoAtencion = True
                self.estadoResuelto = False
                mensajeTitulo = 'Estado de ticket actualizado!!!'
                mensajeCuerpo = 'Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Atención' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página."
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



    
    estadoResuelto = fields.Boolean(string="Paso por estado resuelto", default=False)
    
    #@api.onchange('stage_id')
    def cambioResuelto(self):
        estadoAntes = str(self.stage_id.name)
        if self.estadoResuelto == False or self.estadoResuelto == True :
            #query = "update helpdesk_ticket set stage_id = 3 where id = " + str(self.x_studio_id_ticket) + ";"
            #ss = self.env.cr.execute(query)
            self.write({'stage_id': 3})
            ultimaEvidenciaTec = []
            ultimoComentario = ''
            if self.diagnosticos:
                if self.diagnosticos[-1].evidencia.ids:
                    ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                ultimoComentario = self.diagnosticos[-1].comentario
            comentarioGenerico = 'Cambio de estado al seleccionar botón Resuelto. Se cambio al estado Resuelto. Seleccion realizada por ' + str(self.env.user.name) +'.'
            estado = 'Resuelto'
            self.creaDiagnosticoVistaLista(comentarioGenerico, estado)
            self.datos_ticket_2()
            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Resuelto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoResuelto = True
            self.estadoAtencion = False
            return {'warning': mess}

    estadoCotizacion = fields.Boolean(string="Paso por estado cotizacion", default=False)
    
    #@api.onchange('stage_id')
    def cambioCotizacion(self):
        if self.stage_id.id == 3:
            mensajeTitulo = 'Alerta!!!'
            mensajeCuerpo = 'No se permite cambiar al estado "cotización" una vez que el ticket esta en el estado "resuelto".'
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

        estadoAntes = str(self.stage_id.name)
        #if self.stage_id.name == 'Cotización' and str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id) and self.estadoCotizacion == False:
        #if str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id) and self.estadoCotizacion == False:
        if self.estadoCotizacion == False:
            #query = "update helpdesk_ticket set stage_id = 101 where id = " + str(self.x_studio_id_ticket) + ";"
            #ss = self.env.cr.execute(query)
            self.write({'stage_id': 101})
            ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            ultimaEvidenciaTec = []
            ultimoComentario = ''
            if self.diagnosticos:
                if self.diagnosticos[-1].evidencia.ids:
                    ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                ultimoComentario = self.diagnosticos[-1].comentario
                    
            comentarioGenerico = 'Cambio de estado al seleccionar botón Cotización. Se cambio al estado Cotización. Seleccion realizada por ' + str(self.env.user.name) +'.'
            estado = 'Cotización'
            self.creaDiagnosticoVistaLista(comentarioGenerico, estado)
            self.datos_ticket_2()
            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Cotización' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoCotizacion = True
            return {'warning': mess}
            
     
    estadoResueltoPorDocTecnico = fields.Boolean(string="Paso por estado resuelto", default=False)
    #Falta comprobar
    @api.onchange('documentosTecnico')
    def cambioResueltoPorDocTecnico(self):
        estadoAntes = str(self.stage_id.name)
        #if self.documentosTecnico.id != False and str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id):
        if str(self.env.user.id) == str(self.x_studio_tcnico.user_id.id) and self.estadoResueltoPorDocTecnico == False:
            query = "update helpdesk_ticket set stage_id = 3 where id = " + str(self.x_studio_id_ticket) + ";"
            ss = self.env.cr.execute(query)
            ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            ultimaEvidenciaTec = []
            ultimoComentario = ''
            if self.diagnosticos:
                if self.diagnosticos[-1].evidencia.ids:
                    ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                ultimoComentario = self.diagnosticos[-1].comentario
                
            comentarioGenerico = 'Cambio de estado al subir utlima evidencia como técnico. Se cambio al estado Resuelto. Cambio realizado por ' + str(self.env.user.name) +'.'
            estado = 'Resuelto'
            self.creaDiagnosticoVistaLista(comentarioGenerico, estado)

            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Resuelto' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoResueltoPorDocTecnico = True
            self.estadoAtencion = False
            return {'warning': mess}
            
            
    estadoCerrado = fields.Boolean(string="Paso por estado cerrado", default=False)
    #Falta comprobar
    #@api.onchange('stage_id')
    def cambioCerrado(self):
        estadoAntes = str(self.stage_id.name)
        if self.stage_id.name == 'Distribución' or self.stage_id.name == 'En Ruta' or self.stage_id.name == 'Resuelto' or self.stage_id.name == 'Abierto' or self.stage_id.name == 'Asignado' or self.stage_id.name == 'Atención' and self.estadoCerrado == False:
            query = "update helpdesk_ticket set stage_id = 18 where id = " + str(self.x_studio_id_ticket) + ";"
            ss = self.env.cr.execute(query)
            ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            ultimaEvidenciaTec = []
            ultimoComentario = ''
            if self.diagnosticos:
                if self.diagnosticos[-1].evidencia.ids:
                    ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                ultimoComentario = self.diagnosticos[-1].comentario
            
            comentarioGenerico = 'Cambio de estado al seleccionar botón Cerrar. Se cambio al estado Cerrado. Seleccion realizada por ' + str(self.env.user.name) +'.'
            estado = 'Cerrado'
            self.creaDiagnosticoVistaLista(comentarioGenerico, estado)

            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Cerrado' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }
            self.estadoResueltoPorDocTecnico = True
            self.estadoAtencion = True
            return {'warning': mess}
    
    
    estadoCancelado = fields.Boolean(string="Paso por estado cancelado", default=False)
    #Falta comprobar
    #@api.onchange('stage_id')
    def cambioCancelado(self):
        estadoAntes = str(self.stage_id.name)
        #if self.stage_id.name == 'Cancelado':
        if self.estadoCancelado == False:
            query = "update helpdesk_ticket set stage_id = 4 where id = " + str(self.x_studio_id_ticket) + ";"
            ss = self.env.cr.execute(query)
            ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
            ultimaEvidenciaTec = []
            ultimoComentario = ''
            if self.diagnosticos:
                if self.diagnosticos[-1].evidencia.ids:
                    ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                ultimoComentario = self.diagnosticos[-1].comentario
            
            comentarioGenerico = 'Cambio de estado al seleccionar botón Cancelar. Se cambio al estado Cancelado. Seleccion realizada por ' + str(self.env.user.name) +'.'
            estado = 'Cancelado'
            self.creaDiagnosticoVistaLista(comentarioGenerico, estado)    
            
            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Cancelado' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
            mess= {
                    'title': _('Estado de ticket actualizado!!!'),
                    'message' : message
                }

            #Cancelando contadores
            contadores = self.env['dcas.dcas'].search([['x_studio_tickett', '=', str(self.id)]])
            _logger.info('Contadores: ' + str(contadores))
            #contadores.unlink()
            for contador in contadores:
                contador.active = False


            #Cancelando el pedido de venta
            self.estadoCancelado = True
            pedidoDeVentaACancelar = self.x_studio_field_nO7Xg
            if pedidoDeVentaACancelar:
                regresa = self.env['stock.picking'].search([['sale_id', '=', int(pedidoDeVentaACancelar.id)], ['state', '=', 'done']])
                if len(regresa) == 0:
                    pedidoDeVentaACancelar.action_cancel()
            
            
            return {'warning': mess}
    
    
    


    def cambioEstadoSolicitudRefaccion(self):
        if self.stage_id.id == 3:
            mensajeTitulo = 'Alerta!!!'
            mensajeCuerpo = 'No se permite cambiar al estado "Pendiente por autorizar solicitud" una vez que el ticket esta en el estado "Resuelto".'
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

        if self.stage_id.id == 18 or self.stage_id.id == 4:
            mensajeTitulo = 'Estado no valido'
            mensajeCuerpo = 'No es posible agregar productos al ticket ' + str(self.id) + ' en el estado ' + str(self.stage_id.name) + '\nNo se permite añadir refacciones y/o accesorios a un ticket Cerrado o Cancelado.'
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
        else:
            estadoAntes = str(self.stage_id.name)
            query = "update helpdesk_ticket set stage_id = 91 where id = " + str(self.x_studio_id_ticket) + ";"
            ss = self.env.cr.execute(query)
            self.estadoSolicitudDeRefaccion = True
            comentarioGenerico = 'Cambio de ' + estadoAntes +' a solicitud de refacción. Cambio generado por ' + str(self.env.user.name) + '.\nEl día ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S")) + '.\n\n'
            self.env['helpdesk.diagnostico'].sudo().with_env(self.env(user=self.env.user.id)).create({
                                                                'ticketRelacion': self.id,
                                                                'comentario': comentarioGenerico,
                                                                'estadoTicket': 'Pendiente por autorizar solicitud',
                                                                'mostrarComentario': True,
                                                                'write_uid':  self.env.user.id,
                                                                'create_uid':  self.env.user.id,
                                                                'creadoPorSistema': True
                                                            })
            self.obten_ulimo_diagnostico_fecha_usuario()
            mensajeTitulo = 'Estado de ticket actualizado!!!'
            mensajeCuerpo = 'Se cambio el estado del ticket ' + str(self.x_studio_id_ticket) +'. \nEstado anterior: ' + estadoAntes + ' Estado actual:  Pendiente por autorizar solicitud' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página."
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
            
    def cambioEstadoSolicitudRefaccionApp(self):
        if self.stage_id.id == 3:
            mensajeTitulo = 'Alerta!!!'
            mensajeCuerpo = 'No se permite cambiar al estado "Pendiente por autorizar solicitud" una vez que el ticket esta en el estado "Resuelto".'
            return 1

        if self.stage_id.id == 18 or self.stage_id.id == 4:
            mensajeTitulo = 'Estado no valido'
            mensajeCuerpo = 'No es posible agregar productos al ticket ' + str(self.id) + ' en el estado ' + str(self.stage_id.name) + '\nNo se permite añadir refacciones y/o accesorios a un ticket Cerrado o Cancelado.'
            return 2

        else:
            estadoAntes = str(self.stage_id.name)
            query = "update helpdesk_ticket set stage_id = 91 where id = " + str(self.x_studio_id_ticket) + ";"
            ss = self.env.cr.execute(query)
            self.estadoSolicitudDeRefaccion = True
            comentarioGenerico = 'Cambio de ' + estadoAntes +' a solicitud de refacción. Cambio generado por ' + str(self.env.user.name) + '.\nEl día ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S")) + '.\n\n'
            self.env['helpdesk.diagnostico'].sudo().with_env(self.env(user=self.env.user.id)).create({
                                                                'ticketRelacion': self.id,
                                                                'comentario': comentarioGenerico,
                                                                'estadoTicket': 'Pendiente por autorizar solicitud',
                                                                'mostrarComentario': True,
                                                                'write_uid':  self.env.user.id,
                                                                'create_uid':  self.env.user.id,
                                                                'creadoPorSistema': True
                                                            })
            self.obten_ulimo_diagnostico_fecha_usuario()
            mensajeTitulo = 'Estado de ticket actualizado!!!'
            mensajeCuerpo = 'Se cambio el estado del ticket ' + str(self.x_studio_id_ticket) +'. \nEstado anterior: ' + estadoAntes + ' Estado actual:  Pendiente por autorizar solicitud' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página."
            return 3
    
    estadoSolicitudDeRefaccion = fields.Boolean(string="Paso por estado solicitud de refaccion", default=False)
    
    #@api.oncgange()
    
    def crear_solicitud_refaccion(self):
        for record in self:
            #if record.x_studio_id_ticket != 0:
            if len(record.x_studio_productos) > 0:
                if self.x_studio_field_nO7Xg.id != False and self.x_studio_field_nO7Xg.state == 'sale':
                    message = ('Existe una solicitud ya generada y esta fue validada. \n\nNo es posible realizar cambios a una solicitud ya validada.')
                    mess= {'title': _('Solicitud existente validada!!!')
                            , 'message' : message
                    }
                    return {'warning': mess}
                
                if self.x_studio_field_nO7Xg.id != False and self.x_studio_field_nO7Xg.state != 'sale':
                    sale = self.x_studio_field_nO7Xg
                    self.env.cr.execute("delete from sale_order_line where order_id = " + str(sale.id) +";")
                    for c in self.x_studio_productos:
                        datosr={'order_id' : sale.id, 'product_id' : c.id, 'product_uom_qty' : c.x_studio_cantidad_pedida, 'x_studio_field_9nQhR':self.x_studio_equipo_por_nmero_de_serie[0].id}
                        if(self.team_id.id==10 or self.team_id.id==11):
                            datosr['route_id']=22548
                        self.env['sale.order.line'].create(datosr)
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                        #self.env.cr.commit()
                
                else:
                    sale = self.env['sale.order'].create({'partner_id' : record.partner_id.id
                                                                 , 'origin' : "Ticket de refacción: " + str(record.x_studio_id_ticket)
                                                                 , 'x_studio_tipo_de_solicitud' : 'Venta'
                                                                 , 'x_studio_requiere_instalacin' : True
                                                                 , 'x_studio_field_RnhKr': self.localidadContacto.id
                                                                 , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id
                                                                 , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                                                 , 'warehouse_id' : 5865   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                                 , 'team_id' : 1
                                                                 , 'x_studio_field_bxHgp': int(record.x_studio_id_ticket) 
                                                                })
                    record['x_studio_field_nO7Xg'] = sale.id
                    for c in record.x_studio_productos:
                        datosr = {'order_id' : sale.id
                                , 'product_id' : c.id
                                , 'product_uom_qty' : c.x_studio_cantidad_pedida
                                ,'x_studio_field_9nQhR':self.x_studio_equipo_por_nmero_de_serie[0].id
                                , 'price_unit': 0}
                        if (self.team_id.id == 10 or self.team_id.id == 11):
                            datosr['route_id'] = 22548
                        self.env['sale.order.line'].create(datosr)
                        sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                        #sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta', 'validity_date' : sale.date_order + datetime.timedelta(days=30)})
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")



                    #if sale.id:
                    #    if self.x_studio_id_ticket:
                            #raise exceptions.ValidationError("error gerardo")
                            #if self.stage_id.name == 'Atención' and self.team_id.name == 'Equipo de hardware':
                    """
                    query = "update helpdesk_ticket set stage_id = 100 where id = " + str(self.x_studio_id_ticket) + ";"
                    _logger.info("lol: " + query)
                    ss = self.env.cr.execute(query)
                    _logger.info("**********fun: crear_solicitud_refaccion(), estado: " + str(self.stage_id.name))
                        ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                    #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Solicitud de refacción"})
                    """
                    
                saleTemp = self.x_studio_field_nO7Xg
                if saleTemp.id != False:
                    #if self.x_studio_id_ticket:
                        
                    estadoAntes = str(self.stage_id.name)
                    foraneoDistribuidor = 11
                    #if (self.stage_id.name == 'Atención' or self.stage_id.name == 'Solicitud de Refacción' or self.team_id.id == foraneoDistribuidor) and self.estadoSolicitudDeRefaccion == False:
                    if self.estadoSolicitudDeRefaccion == False:
                        query = "update helpdesk_ticket set stage_id = 100 where id = " + str(self.x_studio_id_ticket) + ";"
                        ss = self.env.cr.execute(query)
                            ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                        ultimaEvidenciaTec = []
                        ultimoComentario = ''
                        if self.diagnosticos:
                            if self.diagnosticos[-1].evidencia.ids:
                                ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                            ultimoComentario = self.diagnosticos[-1].comentario
                            
                        #self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.x_studio_id_ticket, 'comentario': ultimoComentario, 'estadoTicket': "Solicitud de refacción", 'evidencia': [(0,0,ultimaEvidenciaTec)], 'write_uid':  self.env.user.name})
                        #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': "Solicitud de refacción", 'write_uid':  self.env.user.name})
                        message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Solicitud de refacción' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                        mess= {
                                'title': _('Estado de ticket actualizado!!!'),
                                'message' : message
                              }
                        self.estadoSolicitudDeRefaccion = True
                        return {'warning': mess}
                    
                    """
                    if self.team_id.name == 'Equipo de hardware':
                        query = "update helpdesk_ticket set stage_id = 100 where id = " + str(self.x_studio_id_ticket) + ";"
                        _logger.info("lol: " + query)
                        ss = self.env.cr.execute(query)
                        _logger.info("**********fun: crear_solicitud_refaccion(), estado: " + str(self.stage_id.name))
                        ##self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': self.stage_id.name})
                        #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': self.env.user.name,'x_estado': "Solicitud de refacción"})
                    """
            
            #else:
            #    errorRefaccionNoGenerada = "Solicitud de refacción no generada"
            #    mensajeSolicitudRefaccionNoGenerada = "No es posible crear una solicitud de refacción sin guardar antes el ticket. Favor de guardar el ticket y posteriormente generar la solicitud"
            #    raise exceptions.except_orm(_(errorRefaccionNoGenerada), _(mensajeSolicitudRefaccionNoGenerada))
                
                
    #añadir XML
    estadoSolicitudDeRefaccionValidada = fields.Boolean(string="Paso por estado refaccion autorixada", default=False)
    
    #@api.onchange('x_studio_verificacin_de_refaccin')
    def validar_solicitud_refaccion(self):
        for record in self:
            sale = record.x_studio_field_nO7Xg
            if sale.id != 0 or record.x_studio_productos != []:
                if self.x_studio_field_nO7Xg.order_line:
                    self.sudo().env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                    sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
                    sale.action_confirm()
                    for lineas in sale.order_line:
                        st=self.env['stock.quant'].search([['location_id','in',(35204,12)],['product_id','=',lineas.product_id.id]]).sorted(key='quantity',reverse=True)
                        requisicion=False
                        if(len(st)>0):
                            if(st[0].quantity==0):
                                requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Refacción']]).sorted(key='create_date',reverse=True)
                        else:
                            requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Refacción']]).sorted(key='create_date',reverse=True)
                        if(requisicion!=False ):
                            re=self.env['requisicion.requisicion'].create({'origen':'Refacción','area':'Almacen','state':'draft'})
                            re.product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                        if(requisicion):
                            #prd=requisicion[0].product_rel.search([['product','=',lineas.product_id.id],['req_rel','=',requisicion[0].id]])
                            requisicion[0].product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                            #if(len(prd)>0):
                            #    prd.cantidad=prd.cantidad+lineas.product_uom_qty
                            #if(len(prd)==0):
                            #    requisicion[0].product_rel=[{'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]

                    
                    
                    estadoAntes = str(self.stage_id.name)
                    #if self.stage_id.name == 'Solicitud de refacción' and self.estadoSolicitudDeRefaccionValidada == False:
                    if (self.stage_id.name == 'Solicitud de Refacción' or self.stage_id.name == 'Cotización') and self.estadoSolicitudDeRefaccionValidada == False:
                        query = "update helpdesk_ticket set stage_id = 102 where id = " + str(self.x_studio_id_ticket) + ";"
                        ss = self.env.cr.execute(query)
                        ultimaEvidenciaTec = []
                        ultimoComentario = ''
                        if self.diagnosticos:
                            if self.diagnosticos[-1].evidencia.ids:
                                ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                            ultimoComentario = self.diagnosticos[-1].comentario
                            
                        #self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.x_studio_id_ticket, 'comentario': ultimoComentario, 'estadoTicket': "Refacción Autorizada", 'evidencia': [(0,0,ultimaEvidenciaTec)], 'write_uid':  self.env.user.name})
                        #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': "Refacción Autorizada", 'write_uid':  self.env.user.name})
                        
                        message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Refacción Autorizada' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                        mess= {
                                'title': _('Estado de ticket actualizado!!!'),
                                'message' : message
                              }
                        self.estadoSolicitudDeRefaccionValidada = True
                        return {'warning': mess}
                else:
                    message = ("No es posible validar una solicitud que no tiene productos.")
                    mess = {'title': _('Solicitud sin productos!!!')
                            , 'message' : message
                            }
                    return {'warning': mess}
            else:
                errorRefaccionNoValidada = "Solicitud de refacción no validada"
                mensajeSolicitudRefaccionNoValida = "No es posible validar una solicitud de refacción en el estado actual debido a falta de productos o porque no existe la solicitud."
                estadoActual = str(record.stage_id.name)
                raise exceptions.except_orm(_(errorRefaccionNoValidada), _(mensajeSolicitudRefaccionNoValida + " Estado: " + estadoActual))
    
    
    
    """
    @api.onchange('x_studio_localidad_destino')
    def cambio(self):
      _logger.info('************* haciendo algo xD ' )
      for record in self:  
        if record.team_id.id == 76 :
            sale = self.env['stock.picking'].create({'partner_id' : record.partner_id.id
                                             #,'almacenOrigen':record.x_studio_empresas_relacionadas.id
                                             #,'almacenDestino':record.x_studio_field_yPznZ.id        
                                             ,'location_id':12
                                             ,'location_dest_id':16
                                             ,'scheduled_date': record.x_studio_fecha_prevista
                                             ,'picking_type_id': 5
                                            #, 'origin' : "Ticket de tóner: " + str(record.ticket_type_id.id)
                                            #, 'x_studio_tipo_de_solicitud' : "Venta"
                                            #, 'x_studio_requiere_instalacin' : True
                                                     
                                            #, 'user_id' : record.user_id.id                                           
                                            #, 'x_studio_tcnico' : record.x_studio_tcnico.id
                                            #, 'warehouse_id' : 1   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                            #, 'team_id' : 1      
                                          })
            _logger.info('************* haciendo algo xD '+str(sale.id) )
            record['x_studio_transferencia'] = sale.id
            
            for c in record.x_studio_equipo_por_nmero_de_serie:
             # _logger.info('*************cantidad a solicitar: ' + str(c.x_studio_cantidad_a_solicitar))
              self.env['stock.move'].create({'picking_id' : sale.id
                                            , 'product_id' : c.product_id.id
                                             ,'name':"test"
                                             ,'product_uom':1
                                             ,'location_id':1
                                             ,'location_dest_id':1
                                            #, 'product_uom_qty' : c.x_studio_cantidad_pedida
                                          })
    """
    
    




    
    def crear_y_validar_solicitud_refaccion(self):
        record_ids = self.ids
        #_logger.info('record_ids: ' + str(record_ids))
        #_logger.info('self.env["helpdesk.ticket"].browse(record_ids): ' + str(self.env['helpdesk.ticket'].browse(record_ids)))
        for record in self.env['helpdesk.ticket'].browse(record_ids):
            ticket_id = record.mapped('id')
            estado_inicial_de_ticket_name = record.mapped('stage_id.name')
            diagnosticos_ticket = record.mapped('diagnosticos')
            serie_id = record.mapped('x_studio_equipo_por_nmero_de_serie.id')
            cliente_id = record.mapped('partner_id.id')
            contacto_de_localidad_id = record.mapped('localidadContacto.id')
            localidad_id = record.mapped('x_studio_empresas_relacionadas.id')
            area_de_atencion_id =  record.mapped('team_id.id')
            pedido_de_venta = record.mapped('x_studio_field_nO7Xg')
            pedido_de_venta_id = record.mapped('x_studio_field_nO7Xg.id')
            pedido_de_venta_estado = record.mapped('x_studio_field_nO7Xg.state')
            productos = record.mapped('accesorios')
            productos_ids = productos.mapped('productos.id')
            _logger.info('ticket_id: ' + str(ticket_id) + ' estado_inicial_de_ticket_name: ' + str(estado_inicial_de_ticket_name) + 'diagnosticos_ticket: ' + str(diagnosticos_ticket) + 'serie_id: ' + str(serie_id) + 'cliente_id: ' + str(cliente_id) + 'contacto_de_localidad_id: ' + str(contacto_de_localidad_id) + 'localidad_id: ' + str(localidad_id) + 'area_de_atencion_id: ' + str(area_de_atencion_id) + 'pedido_de_venta: ' + str(pedido_de_venta) + 'pedido_de_venta_id: ' + str(pedido_de_venta_id) + 'pedido_de_venta_estado: ' + str(pedido_de_venta_estado) + 'productos: ' + str(productos)  + 'productos_ids: ' + str(productos_ids) )
            if not pedido_de_venta:
                if productos:
                    if pedido_de_venta_id and pedido_de_venta_estado[0] == 'sale':
                        #message = ('Existe una solicitud ya generada y esta fue validada. \n\nNo es posible realizar cambios a una solicitud ya validada.')
                        return 'Solicitud ya generada y validada'
                    elif pedido_de_venta_id and pedido_de_venta_estado[0] != 'sale':
                        self.env.cr.execute("delete from sale_order_line where order_id = " + str(pedido_de_venta_id[0]) +";")
                        for refaccion in productos:
                            vals = {
                                'order_id': pedido_de_venta_id[0],
                                'product_id': refaccion.productos.id,
                                'product_uom_qty': refaccion.cantidadPedida,
                                'x_studio_field_9nQhR': serie_id[0]
                            }
                            self.env['sale.order.line'].create(vals)
                            self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(pedido_de_venta_id[0]) + ";")
                    else:
                        #Crear nuevo pedido de venta
                        if not cliente_id or not contacto_de_localidad_id or not localidad_id:
                            errorRefaccionNoValidada = "Solicitud de refacción no validada"
                            mensajeSolicitudRefaccionNoValida = "No es posible validar una solicitud de refacción debido a falta uno de los siguientes campos: \nCliente, localidad o contacto de la localidad."
                            #estadoActual = str(record.stage_id.name)
                            raise exceptions.except_orm(
                                _(errorRefaccionNoValidada), 
                                _(mensajeSolicitudRefaccionNoValida)
                            )
                        _logger.info('***** Inicio de creacion: creando pedido de venta ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ) + ' *****')
                        nuevo_pedido_de_venta = self.env['sale.order'].sudo().create({
                                                                                        'partner_id': cliente_id[0],
                                                                                        'origin': "Ticket de refacción: " + str(record.id),
                                                                                        'x_studio_tipo_de_solicitud': 'Venta',
                                                                                        'x_studio_requiere_instalacin': True,
                                                                                        'x_studio_field_RnhKr': contacto_de_localidad_id[0],
                                                                                        'partner_shipping_id': localidad_id[0],
                                                                                        'warehouse_id': 5865,   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                                                        'team_id': 1,
                                                                                        'x_studio_field_bxHgp': ticket_id[0]
                        })
                        #_logger.info('pase la creacion de la SO: ' + str(nuevo_pedido_de_venta) )
                        record.write({
                                        'x_studio_field_nO7Xg': nuevo_pedido_de_venta.id
                        })
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(nuevo_pedido_de_venta.id) + ";")
                        #Se cargan los procustos al pedio de venta
                        for refaccion in productos:
                            vals = {
                                'order_id': nuevo_pedido_de_venta.id,
                                'product_id': refaccion.productos.id,
                                'product_uom_qty': refaccion.cantidadPedida,
                                'x_studio_field_9nQhR': serie_id[0],
                                'price_unit': 0
                            }
                            #Si es foraneo-localidad o foranero-distribuidor
                            if area_de_atencion_id[0] == 10 or area_de_atencion_id[0] == 11:
                                vals['route_id'] = 22548
                            self.env['sale.order.line'].sudo().create(vals)
                            #self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                        if nuevo_pedido_de_venta or productos_ids:
                            lineas_de_pedido = nuevo_pedido_de_venta.mapped('order_line')
                            if lineas_de_pedido:
                                nuevo_pedido_de_venta.action_confirm()
                                query = "update helpdesk_ticket set stage_id = 102 where id = " + str(ticket_id[0]) + ";"
                                self.env.cr.execute(query)
                                ultimaEvidenciaTec = []
                                ultimoComentario = ''
                                if diagnosticos_ticket:
                                    if diagnosticos_ticket[-1].evidencia.ids:
                                        ultimaEvidenciaTec = diagnosticos_ticket[-1].evidencia.ids
                                    ultimoComentario = diagnosticos_ticket[-1].comentario
                                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + str(estado_inicial_de_ticket_name[0]) + ' Estado actual: Refacción Autorizada' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                                self.estadoSolicitudDeRefaccionValidada = True
                                _logger.info('***** Fin de creacion: creando pedido de venta ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ) + ' *****')
                                return 'OK'
                            else:
                                #No tiene lineas de pedido de venta
                                message = ("No es posible validar una solicitud que no tiene productos.")
                                return 'Sin refacciones y/o accesorios'
                        else:
                            #No existe un nuevo pedido de venta o no tiene productos en el ticket
                            errorRefaccionNoValidada = "Solicitud de refacción no validada"
                            mensajeSolicitudRefaccionNoValida = "No es posible validar una solicitud de refacción en el estado actual debido a falta de productos o porque no existe la solicitud."
                            #estadoActual = str(record.stage_id.name)
                            raise exceptions.except_orm(
                                _(errorRefaccionNoValidada), 
                                _(mensajeSolicitudRefaccionNoValida + " Estado: " + estado_inicial_de_ticket_name)
                            )
                else:
                    #No tiene productos
                    message = ('No existen productos para generar y validar la solicitud.')
                    return 'Sin refacciones y/o accesorios'
            else:
                #Si ya tiene pedido de venta
                message = ('Ya existe una solicitud, no es posible generan una solicitud.')
                return 'Solicitud existente.'





    def optimiza_lineas(self):
        _logger.info('3312: optimiza_lineas()')
        _logger.info('3312: llego a optimiza_lineas(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        sale = self.x_studio_field_nO7Xg
        if sale.id != 0 or self.x_studio_productos != []:
            if self.x_studio_field_nO7Xg.order_line:
                #self.sudo().env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                #sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
                #sale.action_confirm()

                for lineas in sale.order_line:
                    st=self.env['stock.quant'].search([['location_id','in',(35204,12)],['product_id','=',lineas.product_id.id]]).sorted(key='quantity',reverse=True)
                    requisicion=False
                    if(len(st)>0):
                        if(st[0].quantity==0):
                            requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Refacción']]).sorted(key='create_date',reverse=True)
                    else:
                        requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Refacción']]).sorted(key='create_date',reverse=True)
                    if(requisicion!=False ):
                        re=self.env['requisicion.requisicion'].sudo().create({'origen':'Refacción','area':'Almacen','state':'draft'})
                        re.product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                    if(requisicion):                                            
                        requisicion[0].product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                        
                estadoAntes = str(self.stage_id.name)
                #if (self.stage_id.name == 'Solicitud de Refacción' or self.stage_id.name == 'Cotización') and self.estadoSolicitudDeRefaccionValidada == False:
                query = "update helpdesk_ticket set stage_id = 102 where id = " + str(self.x_studio_id_ticket) + ";"
                ss = self.env.cr.execute(query)
                ultimaEvidenciaTec = []
                ultimoComentario = ''
                if self.diagnosticos:
                    if self.diagnosticos[-1].evidencia.ids:
                        ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                    ultimoComentario = self.diagnosticos[-1].comentario


                comentarioGenerico = 'Solicitud de refacción autorizada por ' + str(self.env.user.name) + '.\nEl día ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S")) + '.\n\n'
                #comentarioGenerico = comentarioGenerico + str(self.comentario)
                self.env['helpdesk.diagnostico'].sudo().create({
                                                                    'ticketRelacion': self.id,
                                                                    'comentario': comentarioGenerico,
                                                                    'estadoTicket': self.stage_id.name,
                                                                    #'evidencia': [(6,0,self.evidencia.ids)],
                                                                    'mostrarComentario': True,
                                                                    'creadoPorSistema': True
                                                                })
                self.obten_ulimo_diagnostico_fecha_usuario()

                message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Refacción Autorizada' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                mess= {
                        'title': _('Estado de ticket actualizado!!!'),
                        'message' : message
                      }
                self.estadoSolicitudDeRefaccionValidada = True
                _logger.info('3312: saliendo de optimiza_lineas(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
                #return {'warning': mess}
                return
            else:
                message = ("No es posible validar una solicitud que no tiene productos.")
                mess = {'title': _('Solicitud sin productos!!!')
                        , 'message' : message
                        }
                return {'warning': mess}
        else:
            errorRefaccionNoValidada = "Solicitud de refacción no validada"
            mensajeSolicitudRefaccionNoValida = "No es posible validar una solicitud de refacción en el estado actual debido a falta de productos o porque no existe la solicitud."
            estadoActual = str(self.stage_id.name)
            raise exceptions.except_orm(_(errorRefaccionNoValidada), _(mensajeSolicitudRefaccionNoValida + " Estado: " + estadoActual))


    def alerta(self):
        _logger.info('3312: creando mensaje de validación exitosa(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        mensajeTitulo = 'Creación y validación de refacción!!!'
        mensajeCuerpo = 'Se creo y valido la solicitud ' + str(self.x_studio_field_nO7Xg.name) + ' para el ticket ' + str(self.id) + '.'
        wiz = self.env['helpdesk.alerta'].sudo().create({'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        _logger.info('3312: wiz.id antes de irme: ' + str(wiz.id))
        _logger.info('3312: view.id antes de irme: ' + str(view.id))
        return {
                    'wizid': wiz.id,
                    'viewid': view.id
                    }


















    #@api.onchange('x_studio_captura_c')
    
    def capturandoMesa(self):
        for record in self:
            #if self.x_studio_field_nO7Xg.id != False and self.x_studio_field_nO7Xg.state == 'sale':
            if record.x_studio_equipo_por_nmero_de_serie:
                for c in record.x_studio_equipo_por_nmero_de_serie:
                    if self.team_id.id == 8 or self.team_id.id == 13:
                        q = 'helpdesk.ticket'
                    else:
                        q = 'stock.production.lot'
                    #if str(c.x_studio_field_A6PR9) =='Negro':
                    if str(c.x_studio_color_bn) == 'B/N':
                        if int(c.x_studio_contador_bn_a_capturar) >= int(c.x_studio_contador_bn):
                            if self.team_id.id == 8 or self.team_id.id == 13:
                                negrot = c.x_studio_contador_bn
                                colort = c.x_studio_contador_color
                            else:
                                negrot = c.x_studio_contador_bn_mesa
                                colort = c.x_studio_contador_color_mesa                        
                            rr = self.env['dcas.dcas'].create({'serie' : c.id
                                                            , 'contadorMono' : c.x_studio_contador_bn_a_capturar
                                                            , 'x_studio_contador_color_anterior':colort
                                                            , 'contadorColor' :c.x_studio_contador_color_a_capturar
                                                            , 'x_studio_contador_mono_anterior_1':negrot
                                                            , 'porcentajeNegro':c.x_studio__negro
                                                            , 'porcentajeCian':c.x_studio__cian      
                                                            , 'porcentajeAmarillo':c.x_studio__amarrillo      
                                                            , 'porcentajeMagenta':c.x_studio__magenta
                                                            , 'x_studio_descripcion':self.name
                                                            , 'x_studio_tickett':self.x_studio_id_ticket
                                                            , 'x_studio_hoja_de_estado':c.x_studio_evidencias
                                                            , 'x_studio_usuariocaptura':self.env.user.name
                                                            , 'fuente':q
                                                            , 'x_studio_rendimiento':int(c.x_studio_rendimiento)/abs(int(c.x_studio_contador_bn_a_capturar)-int(negrot))
                                                            , 'x_studio_rendimiento_color':int(c.x_studio_rendimiento)/abs(int(c.x_studio_contador_color_a_capturar)-int(colort))   
                                                            })                  
                            #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario':'capturas :' + str('Mono'+str(c.x_studio_contador_bn_a_capturar)+', Color '+str(c.x_studio_contador_color_a_capturar)+', Amarillo '+str(c.x_studio__amarrillo)+', Cian '+str(c.x_studio__cian)+', Negro '+str(c.x_studio__negro)+', Magenta '+str(c.x_studio__magenta)+', % de rendimiento '+str(rr.x_studio_rendimiento))})
                        else :
                            raise exceptions.ValidationError("Contador Monocromatico Menor")                     
                    #if str(c.x_studio_field_A6PR9) != 'Negro':       
                    if str(c.x_studio_color_bn) != 'B/N':
                        if int(c.x_studio_contador_color_a_capturar) >= int(c.x_studio_contador_color) and int(c.x_studio_contador_bn_a_capturar) >= int(c.x_studio_contador_bn):
                            if self.team_id.id == 8 or self.team_id.id == 13:
                                negrot = c.x_studio_contador_bn
                                colort = c.x_studio_contador_color
                            else:
                                negrot = c.x_studio_contador_bn_mesa
                                colort = c.x_studio_contador_color_mesa
                            rr=self.env['dcas.dcas'].create({'serie' : c.id
                                                        , 'contadorMono' : c.x_studio_contador_bn_a_capturar
                                                        ,'x_studio_contador_color_anterior':colort
                                                        , 'contadorColor' :c.x_studio_contador_color_a_capturar
                                                        ,'x_studio_contador_mono_anterior_1':negrot
                                                        ,'porcentajeNegro':c.x_studio__negro
                                                        ,'porcentajeCian':c.x_studio__cian      
                                                        ,'porcentajeAmarillo':c.x_studio__amarrillo      
                                                        ,'porcentajeMagenta':c.x_studio__magenta
                                                        ,'x_studio_descripcion':self.name
                                                        ,'x_studio_tickett':self.x_studio_id_ticket
                                                        ,'x_studio_hoja_de_estado':c.x_studio_evidencias
                                                        ,'x_studio_usuariocaptura':self.env.user.name
                                                        ,'fuente':q
                                                        ,'x_studio_rendimiento':int(c.x_studio_rendimiento)/abs(int(c.x_studio_contador_bn_a_capturar)-int(negrot))
                                                        ,'x_studio_rendimiento_color':int(c.x_studio_rendimiento)/abs(int(c.x_studio_contador_color_a_capturar)-int(colort))
       
                                                      })                  
                            #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': 'captura ', 'write_uid':  self.env.user.name, 'comentario':'capturas :' + str('Mono'+str(c.x_studio_contador_bn_a_capturar)+', Color '+str(c.x_studio_contador_color_a_capturar)+', Amarillo '+str(c.x_studio__amarrillo)+', Cian '+str(c.x_studio__cian)+', Negro '+str(c.x_studio__negro)+', Magenta '+str(c.x_studio__magenta)+', % de rendimiento '+str(rr.x_studio_rendimiento))})
                        else :
                            raise exceptions.ValidationError("Error al capturar debe ser mayor")
            else:
                raise exceptions.ValidationError("Error al capturar.")


    estadoSolicitudDeToner = fields.Boolean(string="Paso por estado pendiente por autorizar solicitud", default=False)
    
    #@api.onchange('x_studio_tipo_de_requerimiento')
    
    def toner(self):
      for record in self:
        jalaSolicitudes=''
        if self.x_studio_field_nO7Xg.id != False and self.x_studio_field_nO7Xg.state == 'sale':
            message = ('Existe una solicitud ya generada y esta fue validada. \n\nNo es posible realizar cambios a una solicitud ya validada.')
            mess = {'title': _('Solicitud existente validada!!!')
                    , 'message' : message
            }
            return {'warning': mess}
        if self.x_studio_field_nO7Xg.id != False and self.x_studio_field_nO7Xg.state != 'sale':
            self.env.cr.execute("delete from sale_order_line where order_id = " + str(self.x_studio_field_nO7Xg.id) +";")
            if record.team_id.id == 8 or record.team_id.id == 13:
                serieaca=''
                for c in record.x_studio_equipo_por_nmero_de_serie_1:
                    bn=''
                    amar=''
                    cian=''
                    magen=''
                    car=0
                    serieaca=c.serie.name
                    #Toner BN
                    c.write({'x_studio_tickett':self.x_studio_id_ticket})
                    c.write({'fuente':'helpdesk.ticket'})
                    
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
                        datos={'name': ' '
                               ,'order_id' : self.x_studio_field_nO7Xg.id
                               , 'product_id' : c.serie.x_studio_toner_compatible.id if(len(gen)==0) else gen.id
                               #, 'product_id' : c.x_studio_toner_compatible.id
                               , 'product_uom_qty' : 1
                               , 'x_studio_field_9nQhR': c.serie.id 
                               , 'price_unit': 0 
                               , 'customer_lead' : 0
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
                            datos['product_id']=c.serie.x_studio_toner_compatible.id
                        
                        self.env['sale.order.line'].create(datos)
                        bn=str(c.serie.x_studio_reftoner)+', '
                    #Toner Ama
                    if c.x_studio_cartucho_amarillo:
                        car=car+1
                        c.write({'x_studio_toner_amarillo':1})
                        pro = self.env['product.product'].search([['name','=',c.x_studio_cartucho_amarillo.name],['categ_id','=',5]])
                        gen = pro.sorted(key='qty_available',reverse=True)[0]
                        datos={'name': ' '
                               ,'order_id' : self.x_studio_field_nO7Xg.id
                               , 'product_id' : c.x_studio_cartucho_amarillo.id if(len(gen)==0) else gen.id
                               #, 'product_id' : c.x_studio_toner_compatible.id
                               , 'product_uom_qty' : 1
                               , 'x_studio_field_9nQhR': c.serie.id
                               , 'price_unit': 0 
                               , 'customer_lead' : 0
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
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
                               ,'order_id' : self.x_studio_field_nO7Xg.id
                               , 'product_id' : c.x_studio_cartucho_cian_1.id if(len(gen)==0) else gen.id
                               #, 'product_id' : c.x_studio_toner_compatible.id
                               , 'product_uom_qty' : 1
                               , 'x_studio_field_9nQhR': c.serie.id 
                               , 'price_unit': 0 
                               , 'customer_lead' : 0
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
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
                               ,'order_id' : self.x_studio_field_nO7Xg.id
                               , 'product_id' : c.x_studio_cartucho_magenta.id if(len(gen)==0) else gen.id
                               #, 'product_id' : c.x_studio_toner_compatible.id
                               , 'product_uom_qty' : 1
                               , 'x_studio_field_9nQhR': c.serie.id 
                               , 'price_unit': 0 
                               , 'customer_lead' : 0
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
                            datos['product_id']=c.x_studio_cartucho_magenta.id
                        
                        self.env['sale.order.line'].create(datos)
                        magen=str(c.x_studio_cartucho_magenta.name)
                    if car==0:
                       raise exceptions.ValidationError("Ningun cartucho selecionado, serie ."+str(c.serie.name))                     
                    
                    jalaSolicitudes='solicitud de toner '+self.x_studio_field_nO7Xg.name+' para la serie :'+serieaca +' '+bn+' '+amar+' '+cian+' '+magen
                    #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'comentario':jalaSolicitudes, 'estadoTicket': "solicitud por serie", 'write_uid':  self.env.user.name})
                if len(self.x_studio_field_nO7Xg.order_line)==0:
                   raise exceptions.ValidationError("Ningun cartucho selecionado, revisar series .")                     
                self.x_studio_field_nO7Xg.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                jalaSolicitudess='solicitud de toner '+self.x_studio_field_nO7Xg.name+' para la serie :'+serieaca
                #sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta', 'validity_date' : sale.date_order + datetime.timedelta(days=30)})
                self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(self.x_studio_field_nO7Xg.id) + ";")                
        else:                               
            if record.team_id.id == 8 or record.team_id.id == 13:
                sale = self.env['sale.order'].sudo().create({'partner_id' : record.partner_id.id
                                                , 'origin' : "Ticket de tóner: " + str(record.x_studio_id_ticket)
                                                , 'x_studio_tipo_de_solicitud' : "Venta"
                                                , 'x_studio_requiere_instalacin' : True                                       
                                                , 'user_id' : record.user_id.id                                           
                                                , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                                , 'x_studio_field_RnhKr': self.localidadContacto.id
                                                , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id
                                                , 'warehouse_id' : 1   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                , 'team_id' : 1
                                                , 'x_studio_comentario_adicional':self.x_studio_comentarios_de_localidad
                                                , 'x_studio_field_bxHgp': int(record.x_studio_id_ticket)
                                                ,'x_studio_corte':self.x_studio_corte     
                                              })
                record['x_studio_field_nO7Xg'] = sale.id
                serieaca=''
                
                for c in record.x_studio_equipo_por_nmero_de_serie_1:
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
                        
                    c.write({'x_studio_tickett':self.x_studio_id_ticket})
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
                        weirtihgone=c.serie.x_studio_toner_compatible.id if(len(gen)==0) else gen.id
                        datos={'name': ' '
                               ,'order_id' : sale.id
                               , 'product_id' : weirtihgone
                               #, 'product_id' : c.x_studio_toner_compatible.id
                               , 'product_uom_qty' : 1
                               , 'x_studio_field_9nQhR': c.serie.id 
                               , 'price_unit': 0 
                               , 'customer_lead' : 0
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
                            datos['product_id']=c.serie.x_studio_toner_compatible.id
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
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
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
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
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
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
                            datos['product_id']=c.x_studio_cartucho_magenta.id
                                                
                        self.env['sale.order.line'].create(datos)
                        magen=str(c.x_studio_cartucho_magenta.name)
                        
                    
                    if car==0:
                       raise exceptions.ValidationError("Ningun cartucho selecionado, serie ."+str(c.serie.name)) 
                    
                    jalaSolicitudes='solicitud de toner '+sale.name+' para la serie :'+serieaca +' '+bn+' '+amar+' '+cian+' '+magen
                    #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'comentario':jalaSolicitudes, 'estadoTicket': "solicitud por serie", 'write_uid':  self.env.user.name})
                if len(sale.order_line)==0:
                   raise exceptions.ValidationError("Ningun cartucho selecionado, revisar series .")                    
                sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                jalaSolicitudess='solicitud de toner '+sale.name+' para la serie :'+serieaca
                #sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta', 'validity_date' : sale.date_order + datetime.timedelta(days=30)})
                self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
            
            
            
            """
            if (record.team_id.id == 13 ) and record.x_studio_tipo_de_requerimiento == 'Tóner':
                sale = self.env['sale.order'].sudo().create({'partner_id' : record.partner_id.id
                                                , 'origin' : "Ticket de tfs: " + str(record.x_studio_id_ticket)
                                                , 'x_studio_tipo_de_solicitud' : "Venta"
                                                , 'x_studio_requiere_instalacin' : True                                       
                                                , 'user_id' : record.user_id.id                                           
                                                , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                                , 'x_studio_field_RnhKr': self.localidadContacto.id
                                                , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id
                                                , 'warehouse_id' : 1   ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                                                , 'team_id' : 1
                                                , 'x_studio_field_bxHgp': int(record.x_studio_id_ticket)
                                              })
                record['x_studio_field_nO7Xg'] = sale.id
                for c in record.x_studio_seriestoner:
                  self.env['sale.order.line'].create({'order_id' : sale.id
                                                , 'product_id' : c.id
                                                , 'product_uom_qty' : 1.0
                                                , 'x_studio_field_9nQhR' : self.env['stock.production.lot'].search([['name', '=', str(c.name)]]).id
                                                , 'customer_lead' : 0
                                              })
                sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")    
            """
            saleTemp = self.x_studio_field_nO7Xg
            if saleTemp.id != False:
                if self.x_studio_id_ticket:
                    estadoAntes = str(self.stage_id.name)
                    #if self.stage_id.name == 'Atención' and self.estadoSolicitudDeToner == False:
                    if self.estadoSolicitudDeToner == False:    
                        query = "update helpdesk_ticket set stage_id = 91 where id = " + str(self.x_studio_id_ticket) + ";"
                        ss = self.env.cr.execute(query)
                        #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'comentario':jalaSolicitudess, 'estadoTicket': "Pendiente por autorizar solicitud", 'write_uid':  self.env.user.name})
                        message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Pendiente por autorizar solicitud' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                        mess= {
                                'title': _('Estado de ticket actualizado!!!'),
                                'message' : message
                              }
                        self.estadoSolicitudDeToner = True
                        return {'warning': mess}


            #else:
            #    errorTonerNoGenerada = "Solicitud de tóner no generada"
            #    mensajeSolicitudTonerNoGenerada = "No es posible crear una solicitud de tóner sin guardar antes el ticket. Favor de guardar el ticket y posteriormente generar la solicitud"
            #    raise exceptions.except_orm(_(errorTonerNoGenerada), _(mensajeSolicitudTonerNoGenerada))

        
        
        
        
    estadoSolicitudDeTonerValidar = fields.Boolean(string="Paso por estado autorizado y almacen", default=False)    
        
        
        
    #@api.onchange('x_studio_verificacin_de_tner')
    def validar_solicitud_toner(self):
        for record in self:
            sale = record.x_studio_field_nO7Xg
            
            #if sale.id != 0 or record.x_studio_equipo_por_nmero_de_serie.x_studio_toner_compatible: lol xD
            if sale.id != 0:
                if self.x_studio_field_nO7Xg.order_line:
                    self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                    sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
                    sale.write({'x_studio_corte':self.x_studio_corte})
                    sale.write({'x_studio_comentario_adicional':self.x_studio_comentarios_de_localidad})      
                    x=0
                    if self.x_studio_almacen_1=='Agricola':
                       sale.write({'warehouse_id':1})
                       x=12
                    if self.x_studio_almacen_1=='Queretaro':
                       sale.write({'warehouse_id':18})
                       x=115
                    for lineas in sale.order_line:
                        st=self.env['stock.quant'].search([['location_id','=',x],['product_id','=',lineas.product_id.id]]).sorted(key='quantity',reverse=True)
                        requisicion=False
                        if(len(st)>0):
                            if(st[0].quantity==0):
                                requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']]).sorted(key='create_date',reverse=True)
                        else:
                            requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']]).sorted(key='create_date',reverse=True)
                        if(len(requisicion)==0):
                            re=self.env['requisicion.requisicion'].create({'origen':'Tóner','area':'Almacen','state':'draft'})
                            re.product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                        if(len(requisicion)>0):
                            requisicion[0].product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                            #prd=requisicion[0].product_rel.search([['product','=',lineas.product_id.id],['req_rel','=',requisicion[0].id]])
                            #if(len(prd)>0):
                            #    prd.cantidad=prd.cantidad+lineas.product_uom_qty
                            #if(len(prd)==0):
                                #requisicion[0].product_rel=[{'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]


                    sale.action_confirm()
                    
                    if self.estadoSolicitudDeTonerValidar == False:
                        query="update helpdesk_ticket set stage_id = 95 where id = " + str(self.x_studio_id_ticket) + ";" 
                        ss=self.env.cr.execute(query)
                        ultimaEvidenciaTec = []
                        ultimoComentario = ''
                        if self.diagnosticos:
                            if self.diagnosticos[-1].evidencia.ids:
                                ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                            ultimoComentario = self.diagnosticos[-1].comentario
                        

                        #En almacen
                        query="update helpdesk_ticket set stage_id = 93 where id = " + str(self.x_studio_id_ticket) + ";" 
                        ss=self.env.cr.execute(query)
                        ultimaEvidenciaTec = []
                        ultimoComentario = ''
                        if self.diagnosticos:
                            if self.diagnosticos[-1].evidencia.ids:
                                ultimaEvidenciaTec = self.diagnosticos[-1].evidencia.ids
                            ultimoComentario = self.diagnosticos[-1].comentario
                            
                        #self.env['helpdesk.diagnostico'].create({'ticketRelacion': self.x_studio_id_ticket, 'comentario': ultimoComentario, 'estadoTicket': "En almacén", 'evidencia': [(0,0,ultimaEvidenciaTec)], 'write_uid':  self.env.user.name})
                        #self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': "En almacén", 'write_uid':  self.env.user.name})

                        estadoAntes = str(self.stage_id.name)
                        message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: Almacen' + ". \n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                        mess= {
                                'title': _('Estado de ticket actualizado!!!'),
                                'message' : message
                              }
                        self.estadoSolicitudDeTonerValidar = True
                        return {'warning': mess}
                else:
                    message = ("No es posible validar una solicitud que no tiene productos.")
                    mess = {'title': _('Solicitud sin productos!!!')
                            , 'message' : message
                            }
                    return {'warning': mess}
            else:
                errorTonerNoValidado = "Solicitud de tóner no validada"
                mensajeSolicitudTonerNoValida = "No es posible validar una solicitud de tóner en el estado actual. Favor de verificar el estado del ticket, revisar que la solicitud se haya generado o verificar si agrego productos"
                estadoActual = str(record.stage_id.name)
                raise exceptions.except_orm(_(errorTonerNoValidado), _(mensajeSolicitudTonerNoValida + " Estado: " + estadoActual))
    

    
    def crearYValidarSolicitudDeToner(self):
        for record in self:
            if not record.x_studio_field_nO7Xg:
                jalaSolicitudes = ''
                if record.stage_id.id == 91 and record.x_studio_field_nO7Xg:
                    _logger.info("record.stage_id.id = " + str(record.stage_id.id))
                    _logger.info("record.x_studio_field_nO7Xg = " + str(record.x_studio_field_nO7Xg))
                    #self.stage_id.id = 93
                    
                    #query = "update helpdesk_ticket set stage_id = 93 where id = " + str(self.x_studio_id_ticket) + ";"
                    #ss = self.env.cr.execute(query)
                    break
                if record.team_id.id == 8 or record.team_id.id == 13:
                    x = 1 ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                    if self.almacenes:
                        #if self.x_studio_almacen_1=='Agricola':
                        if self.almacenes.id == 1:
                           #sale.write({'warehouse_id':1})
                           x = 12
                        #if self.x_studio_almacen_1=='Queretaro':
                        if self.almacenes.id == 18:
                           #sale.write({'warehouse_id':18})
                           x = 115
                    sale = self.env['sale.order'].sudo().create({'partner_id' : record.partner_id.id
                                                    , 'origin' : "Ticket de tóner: " + str(record.x_studio_id_ticket)
                                                    , 'x_studio_tipo_de_solicitud' : "Venta"
                                                    , 'x_studio_requiere_instalacin' : True                                       
                                                    , 'user_id' : record.user_id.id                                           
                                                    , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                                    , 'x_studio_field_RnhKr': self.localidadContacto.id
                                                    , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id
                                                    , 'warehouse_id' : self.almacenes.id  
                                                    , 'team_id' : 1
                                                    , 'x_studio_comentario_adicional':self.x_studio_comentarios_de_localidad
                                                    , 'x_studio_field_bxHgp': int(record.x_studio_id_ticket)
                                                    ,'x_studio_corte':self.x_studio_corte     
                                                  })
                    

                    #record['almacenes'] = self.almacenes.id
                    record['x_studio_field_nO7Xg'] = sale.id
                    serieaca = ''
                    
                    for c in record.x_studio_equipo_por_nmero_de_serie_1:
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
                            
                        c.write({'x_studio_tickett':self.x_studio_id_ticket})
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
                            pro = self.env['product.product'].search([['name','ilike',str(c.x_studio_cartuchonefro.name).replace(' ','').replace('-','')],['categ_id','=',5]])
                            q=self.env['stock.quant'].search([['location_id','=',self.almacenes.lot_stock_id.id],['product_id','in',pro.mapped('id')]],order="quantity desc")
                            #gen = pro.sorted(key='qty_available',reverse=True)[0]
                            weirtihgone=c.serie.x_studio_toner_compatible.id if(len(q)==0) else q[0].product_id.id
                            datos={'name': ' '
                                   ,'order_id' : sale.id
                                   , 'product_id' : weirtihgone
                                   #, 'product_id' : c.x_studio_toner_compatible.id
                                   , 'product_uom_qty' : 1
                                   , 'x_studio_field_9nQhR': c.serie.id 
                                   , 'price_unit': 0 
                                   , 'customer_lead' : 0
                                   , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                            if(len(q)>0 and q[0]['quantity']<=0):
                                datos['route_id']=1
                                datos['product_id']=c.serie.x_studio_toner_compatible.id
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
                                   , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                            if(gen['qty_available']<=0):
                                datos['route_id']=1
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
                                   , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                            if(gen['qty_available']<=0):
                                datos['route_id']=1
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
                                   , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                            if(gen['qty_available']<=0):
                                datos['route_id']=1
                                datos['product_id']=c.x_studio_cartucho_magenta.id
                                                    
                            self.env['sale.order.line'].create(datos)
                            magen=str(c.x_studio_cartucho_magenta.name)
                            
                        
                        if car==0:
                           raise exceptions.ValidationError("Ningun cartucho selecionado, serie ."+str(c.serie.name)) 
                        
                        jalaSolicitudes='solicitud de toner '+sale.name+' para la serie :'+serieaca +' '+bn+' '+amar+' '+cian+' '+magen
                    if len(sale.order_line)==0:
                       raise exceptions.ValidationError("Ningun cartucho selecionado, revisar series .")                    
                    sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                    jalaSolicitudess='solicitud de toner '+sale.name+' para la serie :'+serieaca
                    self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                


                    if self.x_studio_field_nO7Xg.order_line:
                        self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                        sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
                        sale.write({'x_studio_corte':self.x_studio_corte})
                        sale.write({'x_studio_comentario_adicional':self.x_studio_comentarios_de_localidad})      
                        x = 0
                        if self.almacenes:
                            #if self.x_studio_almacen_1 == 'Agricola':
                            if self.almacenes.id == 1:
                               #sale.write({'warehouse_id':1})
                               x = 12
                            #if self.x_studio_almacen_1=='Queretaro':
                            if self.almacenes.id == 18:
                               #sale.write({'warehouse_id':18})
                               x = 115
                        for lineas in sale.order_line:
                            st=self.env['stock.quant'].search([['location_id','=',x],['product_id','=',lineas.product_id.id]]).sorted(key='quantity',reverse=True)
                            requisicion=False
                            if(len(st)>0):
                                if(st[0].quantity==0):
                                    #requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']]).sorted(key='create_date',reverse=True)
                                    requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']], order='create_date desc')
                            else:
                                #requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']]).sorted(key='create_date',reverse=True)
                                requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']], order='create_date desc')
                            if requisicion:
                                if(len(requisicion)==0):
                                    re=self.env['requisicion.requisicion'].create({'origen':'Tóner','area':'Almacen','state':'draft'})
                                    re.product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                                if(len(requisicion)>0):
                                    requisicion[0].product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                        sale.action_confirm()

                    else:
                        message = ("No es posible validar una solicitud que no tiene productos.")
                        mess = {'title': _('Solicitud sin productos!!!')
                                , 'message' : message
                                }
                        return {'warning': mess}

                saleTemp = self.x_studio_field_nO7Xg
                if saleTemp.id != False:
                    if self.x_studio_id_ticket:
                        estadoAntes = str(self.stage_id.name)
                        if self.estadoSolicitudDeToner == False:    
                            #query = "update helpdesk_ticket set stage_id = 93 where id = " + str(self.x_studio_id_ticket) + ";"
                            #ss = self.env.cr.execute(query)
                            
                            _logger.info('3312: existe picking? ' + str(saleTemp.picking_ids))
                            estadoActual = ''
                            estadoActualId = 0
                            if saleTemp.picking_ids:
                                listaPickingsOrdenada = saleTemp.picking_ids.sorted(key = 'id')
                                _logger.info('3312: picking ordenados ' + str(listaPickingsOrdenada))
                                if listaPickingsOrdenada[0].state == 'assigned':
                                    estadoActual = 'En almacén'
                                    estadoActualId = 93
                                elif listaPickingsOrdenada[0].state == 'waiting':
                                    estadoActual = 'Sin stock'
                                    estadoActualId = 114
                            
                            query = "update helpdesk_ticket set stage_id = " + str(estadoActualId) + " where id = " + str(self.x_studio_id_ticket) + ";"
                            ss = self.env.cr.execute(query)
                            message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes +  ", Estado actual: " + estadoActual + ". " + "\n\nSolicitud " + str(saleTemp.name) + " generada" + "\n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                            mess= {
                                    'title': _('Estado de ticket actualizado!!!'),
                                    'message' : message
                                  }
                            self.estadoSolicitudDeToner = True
                            return {'warning': mess}
            else:
                message = ('Ya existe una solicitud de tóner. No es posible generar dos solicitudes.')
                mess= {
                        'title': _('Solicitud de tóner existente!!!'),
                        'message' : message
                      }
                return {'warning': mess}

    
    def crearYValidarSolicitudDeTonerTest(self):
        for record in self:
            jalaSolicitudes = ''
            if record.stage_id.id == 91 and record.x_studio_field_nO7Xg:
                _logger.info("record.stage_id.id = " + str(record.stage_id.id))
                _logger.info("record.x_studio_field_nO7Xg = " + str(record.x_studio_field_nO7Xg))
                #self.stage_id.id = 93
                query = "update helpdesk_ticket set stage_id = 93 where id = " + str(self.x_studio_id_ticket) + ";"
                ss = self.env.cr.execute(query)
                break
            if record.team_id.id == 8 or record.team_id.id == 13:
                x = 1 ##Id GENESIS AGRICOLA REFACCIONES  stock.warehouse
                if self.x_studio_almacen_1=='Agricola':
                   sale.write({'warehouse_id':1})
                   x = 12
                if self.x_studio_almacen_1=='Queretaro':
                   sale.write({'warehouse_id':18})
                   x = 115
                """
                sale = self.env['sale.order'].sudo().create({'partner_id' : record.partner_id.id
                                                , 'origin' : "Ticket de tóner: " + str(record.x_studio_id_ticket)
                                                , 'x_studio_tipo_de_solicitud' : "Venta"
                                                , 'x_studio_requiere_instalacin' : True                                       
                                                , 'user_id' : record.user_id.id                                           
                                                , 'x_studio_tcnico' : record.x_studio_tcnico.id
                                                , 'x_studio_field_RnhKr': self.localidadContacto.id
                                                , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id
                                                , 'warehouse_id' : x  
                                                , 'team_id' : 1
                                                , 'x_studio_comentario_adicional':self.x_studio_comentarios_de_localidad
                                                , 'x_studio_field_bxHgp': int(record.x_studio_id_ticket)
                                                ,'x_studio_corte':self.x_studio_corte     
                                              })
                """
                _logger.info("aaaa: " + str(self.x_studio_corte))
                corte = str(self.x_studio_corte)
                _logger.info("aaaa: " + corte)
                _logger.info("aaaa: " + str(record.x_studio_id_ticket))
                id_ticket = "Ticket de tóner: " + str(record.x_studio_id_ticket)
                if corte == 'False':
                    query = """insert into sale_order 
                                (picking_policy, pricelist_id, partner_invoice_id, date_order, name, partner_id, origin, \"x_studio_tipo_de_solicitud\", \"x_studio_requiere_instalacin\", user_id, \"x_studio_field_RnhKr\", partner_shipping_id, warehouse_id, team_id, \"x_studio_comentario_adicional\", \"x_studio_field_bxHgp\")
                                values ('""" + str("direct") + """'
                                        , '""" + str(1) + """'
                                        , '""" + str(self.partner_id.id) + """'
                                        , '""" + str(datetime.datetime.now()) + """'
                                        , '""" + str(self.env['ir.sequence'].next_by_code('sale.order')) + """'
                                        , '""" + str(record.partner_id.id) + """'
                                        , '""" + str(id_ticket) + """'
                                        , '""" + "Venta"  + """'
                                        , '""" + """t""" + """'
                                        , '""" + str(record.user_id.id) + """'
                                        , '""" + str(self.localidadContacto.id) + """'
                                        , '""" + str(self.x_studio_empresas_relacionadas.id) + """'
                                        , '""" + str(x) + """'
                                        , '""" + str(1) + """'
                                        , '""" + str(self.x_studio_comentarios_de_localidad) + """'
                                        , '""" + str(record.x_studio_id_ticket) + """');
                            """
                else:
                    query = """insert into sale_order 
                                (picking_policy, pricelist_id, partner_invoice_id, date_order, name, partner_id, origin, \"x_studio_tipo_de_solicitud\", \"x_studio_requiere_instalacin\", user_id, \"x_studio_field_RnhKr\", partner_shipping_id, warehouse_id, team_id, \"x_studio_comentario_adicional\", \"x_studio_field_bxHgp\", \"x_studio_corte\")
                                values ('""" + str("direct") + """'
                                        , '""" + str(1) + """'
                                        , '""" + str(self.partner_id.id) + """'
                                        , '"""+ str(datetime.datetime.now()) + """'
                                        , '""" + str(self.env['ir.sequence'].next_by_code('sale.order')) + """'
                                        , '""" + str(record.partner_id.id) + """'
                                        , '""" + str(id_ticket) + """'
                                        , '""" + "Venta"  + """'
                                        , '""" + """t""" + """'
                                        , '""" + str(record.user_id.id) + """'
                                        , '""" + str(self.localidadContacto.id) + """'
                                        , '""" + str(self.x_studio_empresas_relacionadas.id) + """'
                                        , '""" + str(x) + """'
                                        , '""" + str(1) + """'
                                        , '""" + str(self.x_studio_comentarios_de_localidad) + """'
                                        , '""" + str(record.x_studio_id_ticket) + """'
                                        , '""" + str(dict(self._fields['x_studio_corte']._description_selection(self.env)).get(self.x_studio_corte)) + """');
                            """
                datoSale = self.env.cr.execute(query)
                query = "select id from sale_order s where s.origin = 'Ticket de tóner: " + str(record.x_studio_id_ticket) + "';"
                self.env.cr.execute(query)
                informaciont = self.env.cr.fetchall()
                _logger.info("resultado query: " +str(informaciont))
                record['x_studio_field_nO7Xg'] = informaciont[0][0]
                sale = self.x_studio_field_nO7Xg
                
                #record['x_studio_field_nO7Xg'] = sale.id
                serieaca = ''
                
                for c in record.x_studio_equipo_por_nmero_de_serie_1:
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
                        
                    c.write({'x_studio_tickett':self.x_studio_id_ticket})
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
                        weirtihgone=c.serie.x_studio_toner_compatible.id if(len(gen)==0) else gen.id
                        datos={'name': ' '
                               ,'order_id' : sale.id
                               , 'product_id' : weirtihgone
                               #, 'product_id' : c.x_studio_toner_compatible.id
                               , 'product_uom_qty' : 1
                               , 'x_studio_field_9nQhR': c.serie.id 
                               , 'price_unit': 0 
                               , 'customer_lead' : 0
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
                            datos['product_id']=c.serie.x_studio_toner_compatible.id
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
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
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
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
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
                               , 'partner_shipping_id' : self.x_studio_empresas_relacionadas.id}
                        if(gen['qty_available']<=0):
                            datos['route_id']=1
                            datos['product_id']=c.x_studio_cartucho_magenta.id
                                                
                        self.env['sale.order.line'].create(datos)
                        magen=str(c.x_studio_cartucho_magenta.name)
                        
                    
                    if car==0:
                       raise exceptions.ValidationError("Ningun cartucho selecionado, serie ."+str(c.serie.name)) 
                    
                    jalaSolicitudes='solicitud de toner '+sale.name+' para la serie :'+serieaca +' '+bn+' '+amar+' '+cian+' '+magen
                if len(sale.order_line)==0:
                   raise exceptions.ValidationError("Ningun cartucho selecionado, revisar series .")                    
                sale.env['sale.order'].write({'x_studio_tipo_de_solicitud' : 'Venta'})
                jalaSolicitudess='solicitud de toner '+sale.name+' para la serie :'+serieaca
                self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
            


                if self.x_studio_field_nO7Xg.order_line:
                    self.env.cr.execute("update sale_order set x_studio_tipo_de_solicitud = 'Venta' where  id = " + str(sale.id) + ";")
                    sale.write({'x_studio_tipo_de_solicitud' : 'Venta'})
                    sale.write({'x_studio_corte':self.x_studio_corte})
                    sale.write({'x_studio_comentario_adicional':self.x_studio_comentarios_de_localidad})      
                    x=0
                    if self.x_studio_almacen_1=='Agricola':
                       sale.write({'warehouse_id':1})
                       x=12
                    if self.x_studio_almacen_1=='Queretaro':
                       sale.write({'warehouse_id':18})
                       x=115
                    for lineas in sale.order_line:
                        st=self.env['stock.quant'].search([['location_id','=',x],['product_id','=',lineas.product_id.id]]).sorted(key='quantity',reverse=True)
                        requisicion=False
                        if(len(st)>0):
                            if(st[0].quantity==0):
                                requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']]).sorted(key='create_date',reverse=True)
                        else:
                            requisicion=self.env['requisicion.requisicion'].search([['state','!=','done'],['create_date','<=',datetime.datetime.now()],['origen','=','Tóner']]).sorted(key='create_date',reverse=True)
                        if(len(requisicion)==0):
                            re=self.env['requisicion.requisicion'].create({'origen':'Tóner','area':'Almacen','state':'draft'})
                            re.product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                        if(len(requisicion)>0):
                            requisicion[0].product_rel=[{'cliente':sale.partner_shipping_id.id,'ticket':sale.x_studio_field_bxHgp.id,'cantidad':int(lineas.product_uom_qty),'product':lineas.product_id.id,'costo':0.00}]
                    sale.action_confirm()

                else:
                    message = ("No es posible validar una solicitud que no tiene productos.")
                    mess = {'title': _('Solicitud sin productos!!!')
                            , 'message' : message
                            }
                    return {'warning': mess}

            saleTemp = self.x_studio_field_nO7Xg
            if saleTemp.id != False:
                if self.x_studio_id_ticket:
                    estadoAntes = str(self.stage_id.name)
                    if self.estadoSolicitudDeToner == False:    
                        #query = "update helpdesk_ticket set stage_id = 93 where id = " + str(self.x_studio_id_ticket) + ";"
                        #ss = self.env.cr.execute(query)
                        
                        message = ('Se cambio el estado del ticket. \nEstado anterior: ' + estadoAntes + ' Estado actual: En almacén' + ". " + "\n\nSolicitud " + str(saleTemp.name) + " generada" + "\n\nNota: Si desea ver el cambio, favor de guardar el ticket. En caso de que el cambio no sea apreciado, favor de refrescar o recargar la página.")
                        mess= {
                                'title': _('Estado de ticket actualizado!!!'),
                                'message' : message
                              }
                        self.estadoSolicitudDeToner = True
                        return {'warning': mess}







    @api.onchange('x_studio_desactivar_zona')
    def desactivar_datos_zona(self):
        res = {}
        if self.x_studio_desactivar_zona :
           res['domain']={'x_studio_responsable_de_equipo':[('x_studio_zona', '!=', False)]}
        return res
       
    #@api.model            
    @api.onchange('x_studio_activar_compatibilidad')
    #
    def productos_filtro(self):
        res = {}             
        g = str(self.x_studio_nombretmp)
        
        if self.x_studio_activar_compatibilidad:
            if g !='False':
                list = ast.literal_eval(g)        
                idf = self.team_id.id
                tam = len(list)
                if idf == 8 or idf == 13 :  
                   res['domain']={'x_studio_productos':[('categ_id', '=', 5),('x_studio_toner_compatible.id','in',list)]}
                if idf == 9:
                   res['domain']={'x_studio_productos':[('categ_id', '=', 7),('x_studio_toner_compatible.id','=',list[0])]}
                if idf != 9 and idf != 8:
                   res['domain']={'x_studio_productos':[('categ_id', '!=', 5),('x_studio_toner_compatible.id','=',list[0])]}
                #if idf 55:
                #   _logger.info("Cotizacion xD" + g)
                #   res['domain'] = {'x_studio_productos':[('x_studio_toner_compatible.id', '=', list[0]),('x_studio_toner_compatible.property_stock_inventory.id', '=', 121),('x_studio_toner_compatible.id property_stock_inventory.id', '=', 121)] }
                #   _logger.info("res"+str(res))
        else:
            res['domain']={'x_studio_productos':[('categ_id', '=', 7)]}

        return res
     

    



    @api.onchange('x_studio_zona')
    def actualiza_datos_zona_responsable_tecnico(self):
        res = {}
        #raise exceptions.ValidationError("test " + self.x_studio_zona)
        if self.x_studio_zona :
            res['domain']={'x_studio_tcnico':[('x_studio_zona', '=', self.x_studio_zona)]}
            #res['domain'] = {'x_studio_tcnico':['|',('x_studio_zona', '=', self.x_studio_zona),('x_studio_zona', '=', self.zona_estados)]}
        return res
    
    @api.onchange('x_studio_zona')
    def actualiza_datos_zona_responsable(self):
        res = {}
        #raise exceptions.ValidationError("test " + self.x_studio_zona)
        if self.x_studio_zona :
            res['domain']={'x_studio_responsable_de_equipo':[('x_studio_zona', '=', self.x_studio_zona)]}
        return res
   
   
   
    
    
    
    #@api.onchange('stage_id')
    #def actualiza_datos_estado(self):
    #    self.env['helpdesk.diagnostico'].create({'ticketRelacion':self.x_studio_id_ticket, 'estadoTicket': self.stage_id.name, 'write_uid':  self.env.user.name})
    #    objTicket.obten_ulimo_diagnostico_fecha_usuario()
    
    
    
    @api.onchange('x_studio_responsable_de_equipo')
    def actualiza_datos_zona_dos(self):
        s = self.stage_id.name
        #raise exceptions.ValidationError("No son vacios : "+str(s))
        res = self.x_studio_responsable_de_equipo.name
        team = self.team_id.name
        
        if s=='Abierto' :
        #if s == 'New' :
            if self.x_studio_id_ticket :
               query="update helpdesk_ticket set stage_id = 2 where id = " + str(self.x_studio_id_ticket) + ";" 
               #raise exceptions.ValidationError("No son vacios : "+str(query))
               ss=self.env.cr.execute(query)
    """
    @api.onchange('x_studio_fecha_de_visita')
    def actualiza_datos_tecnico(self):
        s = self.stage_id.name
        #raise exceptions.ValidationError("No son vacios : "+str(s))
        if s=='Asignado' :
            if self.x_studio_tcnico :
               query="update helpdesk_ticket set stage_id = 3 where id = " + str(self.x_studio_id_ticket) + ";" 
               ss=self.env.cr.execute(query)
    """     
    """       
    @api.onchange('x_studio_tcnico')
    def actualiza_datos_zona(self):
        s = self.x_studio_tcnico.name
        b = self.stage_id.name
        #self.env['x_historial_helpdesk'].create({'x_id_ticket':self.x_studio_id_ticket ,'x_persona': s,'x_estado': b })
    """
    
    @api.depends('x_studio_equipo_por_nmero_de_serie.x_studio_field_B7uLt')
    def obtener_contadores(self):        
        for record in self.x_studio_equipo_por_nmero_de_serie:
            if len(record)>0:
                f = record.x_studio_dcas_ultimo
                raise exceptions.ValidationError("No son vacios : "+str(f))
    
    
    #
    #@api.depends('team_id', 'x_studio_responsable_de_equipo')
    """
    @api.model
    @api.onchange('team_id', 'x_studio_responsable_de_equipo')
    def cambiar_seguidores(self):
        _logger.info("cambiar_github porfinV2   ***********************************()")
        _logger.info("cambiar_seguidores()")
        _logger.info("self._origin: " + str(self._origin) + ' self._origin.id: ' + str(self._origin.id))
        
        #https://www.odoo.com/es_ES/forum/ayuda-1/question/when-a-po-requires-approval-the-follower-of-the-warehouse-receipt-is-the-approver-i-need-it-to-be-the-user-who-created-the-po-136450
        #log(str(self.message_follower_ids), level='info')
        
        #self._origin.id
        
        ##Busanco subscriptores de modelo helpdesk con id especifico
        #log("id: " + str(record.x_studio_id_ticket), level='info')
        ids = self.env['mail.followers'].search_read(['&', ('res_model', '=', 'helpdesk.ticket'), ('res_id', '=',self.x_studio_id_ticket)], ['partner_id'])
        #log(str(ids), level='info')
        lista_followers_borrar = []
        id_cliente = self.partner_id.id
        #log('id_cliente: ' + str(id_cliente), level='info')
        for id_partner in ids:
            #log(str(id_partner['partner_id'][0]))
            id_guardar = id_partner['partner_id'][0]
            if id_guardar != id_cliente:
                #lista_followers_borrar.append(id_guardar)
                lista_followers_borrar.append(id_partner['id'])
            
        #log(str(lista_followers_borrar), level='info')


        #record.message_subscribe([9978])

        # Diamel Luna Chavelas
        id_test = 826   #Id de Diamel Luna Chavelas
        id_test_res_partner = 10528  #Id de res_partner.name = Test


        equipo_de_atencion_al_cliente = 1
        equipo_de_almacen = 2
        equipo_de_distribucion = 3
        equipo_de_finanzas = 4
        equipo_de_hardware = 5
        equipo_de_lecturas = 6
        equipo_de_sistemas = 7
        equipo_de_toner = 8


        responsable_atencion_al_cliente = id_test
        responsable_equipo_de_toner = id_test
        responsable_equipo_de_sistemas = id_test
        responsable_equipo_de_hardware = id_test
        responsable_equipo_de_finanzas = id_test
        responsable_equipo_de_lecturas = id_test
        responsable_equipo_de_distribucion = id_test
        responsable_equipo_de_almacen = id_test

        x_studio_responsable_de_equipo = 'x_studio_responsable_de_equipo'


        ## Por cada caso añadir el id de cada responsable de equipo y modificar para añadir a estos
        ## al seguimiento de los ticket's
        subscritor_temporal = id_test_res_partner


        #record.write({'x_studio_responsable_de_equipo' : responsable_atencion_al_cliente})


        equipo = self.team_id.id

        if equipo == equipo_de_atencion_al_cliente:
            _logger.info("Entrando a if equipo_de_atencion_al_cliente.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            
            #record.message_subscribe([responsable_atencion_al_cliente])                           ##Añade seguidores
            #self._origin.id
            
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_atencion_al_cliente})      ##Asigna responsable de equipo
            _logger.info("regresa: " + str(regresa))
            _logger.info("Saliendo de if equipo_de_atencion_al_cliente............................................................. ")
            
          
          
        if equipo == equipo_de_toner:
            
            _logger.info("Entrando a if equipo_de_toner.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
              
        
            #record.message_subscribe([responsable_equipo_de_toner])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_toner})
            
            _logger.info("Saliendo de if equipo_de_toner............................................................. ")
          

        if equipo == equipo_de_sistemas:
            _logger.info("Entrando a if equipo_de_sistemas.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_sistemas])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_sistemas})
            
            _logger.info("Saliendo de if equipo_de_sistemas............................................................. ")
          
          
        if equipo == equipo_de_hardware:
            _logger.info("Entrando a if equipo_de_hardware.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_hardware])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_hardware})
            _logger.info("Saliendo de if equipo_de_hardware............................................................. ")
          

        if equipo == equipo_de_finanzas:
            _logger.info("Entrando a if equipo_de_finanzas.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_finanzas])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_finanzas})
            _logger.info("Saliendo de if equipo_de_finanzas............................................................. ")
          
        if equipo == equipo_de_lecturas:
            _logger.info("Entrando a if equipo_de_lecturas.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_lecturas])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_lecturas})
            _logger.info("Saliendo de if equipo_de_lecturas............................................................. ")
          

        if equipo == equipo_de_distribucion:
            _logger.info("Entrando a if equipo_de_distribucion.............................................................. " )
            
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            #record.message_subscribe([responsable_equipo_de_distribucion])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_distribucion})
            _logger.info("Saliendo de if equipo_de_distribucion............................................................. ")
          

        if equipo == equipo_de_almacen:
            _logger.info("Entrando a if equipo_de_almacen............................................................................ ")
            #id del seguidor(marco)
            #ids_partner =11
            
            
            #for r in self.message_follower_ids:
             #   if(r.partner_id.id!=7219):
              #      ids_partner.append(r.partner_id.id)
               #     _logger.info('hi'+str(r.partner_id.id))
            #self['message_follower_ids']=[(3,11,0)]
            #hasta que se guarda borra el registro
            
            #self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id="+str(self.x_studio_id_ticket)+" and partner_id="+str(ids_partner)+";")
            
            #self['message_follower_ids']=[(6,0,ids_partner)]
            #unsubs = self.message_unsubscribe(partner_ids = [826], channel_ids = None)
            #unsubs=self.env['mail.followers'].sudo().search([('res_model', '=','helpdesk.ticket'),('res_id', '=', self.x_studio_id_ticket),('partner_id', '=', 826)]).unlink()
            #_logger.info('Unsubs: ' + str('hola')+str(self.x_studio_id_ticket))
            
            
            #raise Warning('Entrando a if equipo_de_almacen... ')
            #log("Entrando a if equipo_de_almacen... ", level='info')
            #unsubs = record.sudo().message_unsubscribe(lista_followers_borrar)
            unsubs = False
            for follower in self.message_follower_ids:    
                #record.message_unsubscribe([follower.partner_id.id])
                for follower_borrar in lista_followers_borrar:
                    #log(str(follower.id), level = 'info')
                    #log(str(follower_borrar), level = 'info')
                    if follower_borrar == follower.id:
                        #log(str([follower.partner_id.id]), level = 'info')
                        #log('entro if:', level = 'info')
                        _logger.info('partner_ids: ' + str(follower.partner_id.id) + ' ' + str(follower.partner_id.name))
                        #unsubs = self._origin.sudo().message_unsubscribe(partner_ids = list([follower.partner_id.id]), channel_ids = None)
                        
                        #unsubs = self.sudo().message_unsubscribe_users(partner_ids = [follower.partner_id.id])
                        
                        unsubs = self.env.cr.execute("delete from mail_followers where res_model='helpdesk.ticket' and res_id=" + str(self.x_studio_id_ticket) + " and partner_id=" +  str(follower.partner_id.id) + ";")
                        
                        
                        _logger.info('Unsubs: ' + str(unsubs))
            
            
            
            #record.message_subscribe([responsable_equipo_de_almacen])
            regresa = self._origin.sudo()._message_subscribe(partner_ids=[subscritor_temporal], channel_ids=None, subtype_ids=None)
            #regresa = self.env.cr.execute("insert into mail_followers (res_model, res_id, partner_id) values ('helpdesk.ticket', " + str(self._origin.id) + ", " +  str(subscritor_temporal) + ");")
            _logger.info("regresa: " + str(regresa))
            
            self._origin.sudo().write({x_studio_responsable_de_equipo : responsable_equipo_de_almacen})
            _logger.info('Saliendo de if equipo_de_almacen................................................................................. unsubs = ' + str(unsubs))
    """
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    @api.onchange('partner_id', 'x_studio_empresas_relacionadas')
    def actualiza_dominio_en_numeros_de_serie(self):
        for record in self:
            zero = 0
            dominio = []
            dominioT = []
            
            #for record in self:
            id_cliente = record.partner_id.id
            #id_cliente = record.x_studio_id_cliente
            id_localidad = record.x_studio_empresas_relacionadas.id

            record['x_studio_id_cliente'] = id_cliente# + " , " + str(id_cliente)
            record['x_studio_filtro_numeros_de_serie'] = id_localidad

            if id_cliente != zero:
              #raise Warning('entro1')
              dominio = ['&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]
              dominioT = ['&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]  
                
            else:
              #raise Warning('entro2')
              dominio = [('x_studio_categoria_de_producto_3.name','=','Equipo')]
              dominioT = [('serie.x_studio_categoria_de_producto_3.name','=','Equipo')]
              record['partner_name'] = ''
              record['partner_email'] = ''
              record['x_studio_nivel_del_cliente'] = ''
              record['x_studio_telefono'] = ''
              record['x_studio_movil'] = ''
              record['x_studio_empresas_relacionadas'] = ''
              if self.team_id.id == 8 or self.team_id.id == 13:
                 record['x_studio_equipo_por_nmero_de_serie'] = ''
                 record['x_studio_equipo_por_nmero_de_serie_1'] = ''                    
              if self.team_id.id != 8 and self.team_id.id != 13:
                 record['x_studio_equipo_por_nmero_de_serie'] = ''
                 record['x_studio_equipo_por_nmero_de_serie_1'] = ''   

            if id_cliente != zero  and id_localidad != zero:
              #raise Warning('entro3')
              dominio = ['&', '&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente),('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id','=',id_localidad)]
              dominioT = ['&', '&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente),('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.id','=',id_localidad)]  

            if id_localidad == zero and id_cliente != zero:
              #raise Warning('entro4')
              dominio = ['&', ('x_studio_categoria_de_producto_3.name','=','Equipo'), ('x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]
              dominioT = ['&', ('serie.x_studio_categoria_de_producto_3.name','=','Equipo'), ('serie.x_studio_move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id', '=', id_cliente)]  

            if id_cliente == zero and id_localidad == zero:
              #raise Warning('entro5')
              dominio = [('x_studio_categoria_de_producto_3.name','=','Equipo')]
              dominio = [('serie.x_studio_categoria_de_producto_3.name','=','Equipo')]  
              record['partner_name'] = ''
              record['partner_email'] = ''
              record['x_studio_nivel_del_cliente'] = ''
              record['x_studio_telefono'] = ''
              record['x_studio_movil'] = ''
            if self.team_id.id == 8 or self.team_id.id == 13:
               action = {'domain':{'x_studio_equipo_por_nmero_de_serie':dominio}}
               action = {'domain':{'x_studio_equipo_por_nmero_de_serie_1':dominioT}}
               #raise Warning('este es el dominio xD ' +str(dominio)) 
            if self.team_id.id != 8 and self.team_id.id != 13:
               action = {'domain':{'x_studio_equipo_por_nmero_de_serie':dominio}}    
               action = {'domain':{'x_studio_equipo_por_nmero_de_serie_1':dominioT}}
            return action
    
    



    serie_y_modelo = fields.Text(string = 'Serie(s)')
    @api.onchange('x_studio_equipo_por_nmero_de_serie', 'x_studio_equipo_por_nmero_de_serie_1')
    def actualiza_serie_texto(self):
        #dominio_busqueda_ticket = [('id', '=', self._origin.id)]
        #obj_ticket = self.env['helpdesk.ticket'].search(dominio_busqueda_ticket)
        series_toner = self.mapped('x_studio_equipo_por_nmero_de_serie_1.serie.name')
        serie_mesa = self.mapped('x_studio_equipo_por_nmero_de_serie.name')

        tipo_de_vale = self.mapped('x_studio_tipo_de_vale')

        series_modelo_toner = []
        series_modelo_toner_mapped = self.mapped('x_studio_equipo_por_nmero_de_serie_1')
        for modelo in series_modelo_toner_mapped:
            series_modelo_toner.append(modelo.serie.product_id.name)
        serie_modelo_mesa = []
        serie_modelo_mesa_mapped = self.mapped('x_studio_equipo_por_nmero_de_serie')
        for modelo in serie_modelo_mesa_mapped:
            serie_modelo_mesa.append(modelo.product_id.name)

        _logger.info('tipo_de_vale' + str(tipo_de_vale) +'series_toner: ' + str(series_toner) + ' serie_mesa: ' + str(serie_mesa))
        _logger.info('series_modelo_toner:  ' + str(series_modelo_toner) + ' serie_modelo_mesa: ' + str(serie_modelo_mesa))

        serie_modelo = ''
        if tipo_de_vale and tipo_de_vale[0] == 'Requerimiento':
            if series_toner:
                i = 0
                for serie in series_toner:
                    serie_modelo = serie_modelo + '[' + str(serie) + '] ' + str(series_modelo_toner[i]) + ', '
                    i = i + 1
            else:
                serie_modelo = 'Sin serie'
        elif tipo_de_vale and tipo_de_vale[0] != 'Requerimiento':
            if serie_mesa:
                i = 0
                for serie in serie_mesa:
                    serie_modelo = serie_modelo + '[' + str(serie) + '] ' + str(serie_modelo_mesa[i]) + ', '
                    i = i + 1
            else:
                serie_modelo = 'Sin serie'
        
        texto = """
                    <div class='row' >
                        <div class='col-sm-12'>
                            <p>""" + serie_modelo + """</p>
                        </div>
                    </div>
                """
        self.write({'serie_y_modelo': texto})


    def actualiza_serie_texto_2(self):
        dominio_busqueda_ticket = [('id', '=', self.id)]
        obj_ticket = self.env['helpdesk.ticket'].search(dominio_busqueda_ticket)
        series_toner = obj_ticket.mapped('x_studio_equipo_por_nmero_de_serie_1.serie.name')
        serie_mesa = obj_ticket.mapped('x_studio_equipo_por_nmero_de_serie.name')

        tipo_de_vale = obj_ticket.mapped('x_studio_tipo_de_vale')

        series_modelo_toner = []
        series_modelo_toner_mapped = obj_ticket.mapped('x_studio_equipo_por_nmero_de_serie_1.serie')
        for modelo in series_modelo_toner_mapped:
            series_modelo_toner.append(modelo.product_id.name)
        serie_modelo_mesa = []
        serie_modelo_mesa_mapped = obj_ticket.mapped('x_studio_equipo_por_nmero_de_serie')
        for modelo in serie_modelo_mesa_mapped:
            serie_modelo_mesa.append(modelo.product_id.name)

        _logger.info('tipo_de_vale' + str(tipo_de_vale) +'series_toner: ' + str(series_toner) + ' serie_mesa: ' + str(serie_mesa))
        _logger.info('series_modelo_toner:  ' + str(series_modelo_toner) + ' serie_modelo_mesa: ' + str(serie_modelo_mesa))

        serie_modelo = ''
        if tipo_de_vale and tipo_de_vale[0] == 'Requerimiento':
            if series_toner:
                i = 0
                for serie in series_toner:
                    serie_modelo = serie_modelo + '[' + str(serie) + '] ' + str(series_modelo_toner[i]) + ', '
                    i = i + 1
            else:
                serie_modelo = 'Sin serie'
        elif tipo_de_vale and tipo_de_vale[0] != 'Requerimiento':
            if serie_mesa:
                i = 0
                for serie in serie_mesa:
                    serie_modelo = serie_modelo + '[' + str(serie) + '] ' + str(serie_modelo_mesa[i]) + ', '
                    i = i + 1
            else:
                serie_modelo = 'Sin serie'
        
        texto = """
                    <div class='row' >
                        <div class='col-sm-12'>
                            <p>""" + serie_modelo + """</p>
                        </div>
                    </div>
                """
        obj_ticket.write({'serie_y_modelo': texto})

        if obj_ticket.serie_y_modelo:
            return True
        else:
            return False


    ultimoDiagnosticoFecha = fields.Datetime(string = 'Fecha último cambio')
    ultimoDiagnosticoUsuario = fields.Text(string = 'Ultima escritura')
    @api.onchange('diagnosticos')
    def obten_ulimo_diagnostico_fecha_usuario(self):
        if self.diagnosticos:
            self.write({'ultimoDiagnosticoFecha': self.diagnosticos[-1].create_date})
            self.write({'ultimoDiagnosticoUsuario': self.diagnosticos[-1].create_uid.name})

    
    def obten_ulimo_diagnostico_fecha_usuario_2(self):
        if self.diagnosticos:
            self.write({'ultimoDiagnosticoFecha': self.diagnosticos[-1].create_date})
            self.write({'ultimoDiagnosticoUsuario': self.diagnosticos[-1].create_uid.name})
            return self.id
        else:
            return -1
            

    #@api.model
    #
    @api.onchange('x_studio_equipo_por_nmero_de_serie','x_studio_equipo_por_nmero_de_serie_1.serie','x_studio_equipo_por_nmero_de_serie_1')
    #@api.depends('x_studio_equipo_por_nmero_de_serie')
    def actualiza_datos_cliente(self):

        todasLasAlertas = ""


        """
            Cargando la información de cliente
        """
        v = {}
        ids = []
        localidad = []


        cantidad_numeros_serie = self.x_studio_tamao_lista
        #if record.team_id.id != 8 and record.team_id.id != 13:
        if self.x_studio_tipo_de_vale != 'Requerimiento':
            if int(cantidad_numeros_serie) < 2 :
                for numeros_serie in self.x_studio_equipo_por_nmero_de_serie:
                    ids.append(numeros_serie.id)
                        
                    #cliente = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                    cliente = numeros_serie.x_studio_cliente
                    #self._origin.sudo().write({'partner_id' : cliente.id})
                    #self.partner_id = cliente.id
                    idM = self._origin.id
                    
                    if idM:
                        if cliente:
                            self.env.cr.execute("update helpdesk_ticket set partner_id = " + str(cliente.id) + "  where  id = " + str(idM) + ";")
                        v['partner_id'] = cliente.id
                        cliente_telefono = cliente.phone
                        self._origin.sudo().write({'x_studio_telefono' : cliente_telefono})
                        self.x_studio_telefono = cliente_telefono
                        if cliente_telefono != []:
                            srtt = "update helpdesk_ticket set x_studio_telefono = '" + str(cliente_telefono) + "' where  id = " + str(idM) + ";"                                
                        v['x_studio_telefono'] = cliente_telefono
                        cliente_movil = cliente.mobile
                        self._origin.sudo().write({'x_studio_movil' : cliente_movil})
                        self.x_studio_movil = cliente_movil
                        if cliente_movil == []:
                            self.env.cr.execute("update helpdesk_ticket set x_studio_movil = '" + str(cliente_movil) + "' where  id = " +idM + ";")
                        v['x_studio_movil'] = cliente_movil
                        
                        cliente_nivel = cliente.x_studio_nivel_del_cliente
                        self._origin.sudo().write({'x_studio_nivel_del_cliente' : cliente_nivel})
                        self.x_studio_nivel_del_cliente = cliente_nivel
                        if cliente_nivel == []:
                            self.env.cr.execute("update helpdesk_ticket set x_studio_nivel_del_cliente = '" + str(cliente_nivel) + "' where  id = " + idM + ";")
                        v['x_studio_nivel_del_cliente'] = cliente_nivel


                        localidad = numeros_serie.x_studio_localidad_2

                        self._origin.sudo().write({'x_studio_empresas_relacionadas' : localidad.id})
                        self.x_studio_empresas_relacionadas = localidad.id

                        if self.x_studio_empresas_relacionadas.id != False:
                            self.env.cr.execute("select * from res_partner where id = " + str(self.x_studio_empresas_relacionadas.id) + ";")
                            localidad_tempo = self.env.cr.fetchall()
                            if str(localidad_tempo[0][80]) != 'None':
                                self.x_studio_field_29UYL = str(localidad_tempo[0][80])

                            #self._origin.sudo().write({'x_studio_field_6furK' : self._origin.sudo().write({'x_studio_field_6furK' : move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.x_studio_field_SqU5B})})
                        lista_ids = []
                        for id in ids:
                            lista_ids.append((4,id))
                        
                        v['x_studio_equipo_por_nmero_de_serie'] = lista_ids
                        self._origin.sudo().write({'x_studio_equipo_por_nmero_de_serie' : lista_ids})
                        self.x_studio_equipo_por_nmero_de_serie = lista_ids
                    else:
                        self.partner_id = cliente.id
                        self.x_studio_nivel_del_cliente = cliente.x_studio_nivel_del_cliente
                        #Localidad
                        localidadTemp = numeros_serie.x_studio_localidad_2
                        self.x_studio_empresas_relacionadas = localidadTemp.id
                        self.x_studio_field_6furK = localidadTemp.x_studio_field_SqU5B
                        self.x_studio_zona = localidadTemp.x_studio_field_SqU5B
                        self.zona_estados = localidadTemp.state_id.name
                        #self.localidadContacto = 
                        self.x_studio_estado_de_localidad = localidadTemp.state_id.name
                        self.telefonoLocalidadContacto = localidadTemp.phone
                        self.movilLocalidadContacto = localidadTemp.mobile
                        self.correoLocalidadContacto = localidadTemp.email

                        v['partner_id'] = cliente.id
                        v['x_studio_telefono'] = localidadTemp.phone
                        v['x_studio_movil'] = localidadTemp.mobile
                        
                        v['x_studio_nivel_del_cliente'] = cliente.x_studio_nivel_del_cliente

                        if self.x_studio_empresas_relacionadas.id != False:
                            self.env.cr.execute("select * from res_partner where id = " + str(self.x_studio_empresas_relacionadas.id) + ";")
                            localidad_tempo = self.env.cr.fetchall()
                            if str(localidad_tempo[0][80]) != 'None':
                                self.x_studio_field_29UYL = str(localidad_tempo[0][80])

                            #self._origin.sudo().write({'x_studio_field_6furK' : self._origin.sudo().write({'x_studio_field_6furK' : move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.x_studio_field_SqU5B})})
                        lista_ids = []
                        for id in ids:
                            lista_ids.append((4,id))
                        
                        v['x_studio_equipo_por_nmero_de_serie'] = lista_ids
                        self._origin.sudo().write({'x_studio_equipo_por_nmero_de_serie' : lista_ids})
                        self.x_studio_equipo_por_nmero_de_serie = lista_ids

            else:
                raise exceptions.ValidationError("No es posible registrar más de un número de serie")
        #if record.team_id.id == 8 or record.team_id.id == 13:
        if self.x_studio_tipo_de_vale == 'Requerimiento':
            _my_object = self.env['helpdesk.ticket']

            for numeros_serie in self.x_studio_equipo_por_nmero_de_serie_1:
                ids.append(numeros_serie.serie.id)

                #Cliente
                clienteId = numeros_serie.serie.x_studio_cliente
                self.partner_id = clienteId.id
                self.x_studio_nivel_del_cliente = clienteId.x_studio_nivel_del_cliente
                #Localidad
                localidadTemp = numeros_serie.serie.x_studio_localidad_2
                self.x_studio_empresas_relacionadas = localidadTemp.id
                self.x_studio_field_6furK = localidadTemp.x_studio_field_SqU5B
                self.x_studio_zona = localidadTemp.x_studio_field_SqU5B
                self.zona_estados = localidadTemp.state_id.name
                #self.localidadContacto = 
                self.x_studio_estado_de_localidad = localidadTemp.state_id.name
                self.telefonoLocalidadContacto = localidadTemp.phone
                self.movilLocalidadContacto = localidadTemp.mobile
                self.correoLocalidadContacto = localidadTemp.email

                
                if not self.localidadContacto:
                    idContact = self.env['res.partner'].search([['parent_id', '=', localidadTemp.id],['x_studio_ultimo_contacto', '=', True]], order='create_date desc', limit=1).id
                    self.localidadContacto = idContact
                    _logger.info("Entre por toner idContact: " + str(idContact))
                #if idContact:
                #    query = "update helpdesk_ticket set \"localidadContacto\" = " + str(idContact) + ", \"x_studio_field_6furK\" = '" + str(self.x_studio_empresas_relacionadas.x_studio_field_SqU5B) + "' where id = " + str(self.x_studio_id_ticket) + ";"
                #    self.env.cr.execute(query)
                #    self.env.cr.commit()



                lista_ids = []
                for id in ids:
                    lista_ids.append((4,id))


        """
            Verificando que no exista un ticket con la misma serie
        """
        #_logger.info('len(self.x_studio_equipo_por_nmero_de_serie_1): ' + str(len(self.x_studio_equipo_por_nmero_de_serie_1)))
        #_logger.info('self.x_studio_tipo_de_vale: ' + str(self.x_studio_tipo_de_vale))
        if len(self.x_studio_equipo_por_nmero_de_serie_1) > 0 and (self.x_studio_tipo_de_vale == 'Requerimiento'):
            if len(self.x_studio_equipo_por_nmero_de_serie_1) > 1:
                for localidades in self.x_studio_equipo_por_nmero_de_serie_1:
                    if self.x_studio_equipo_por_nmero_de_serie_1[0].ultimaUbicacion != localidades.ultimaUbicacion:
                       raise exceptions.ValidationError("Error "+str(self.x_studio_equipo_por_nmero_de_serie_1[0].ultimaUbicacion)+' deben ser la misma localidad '+localidades.ultimaUbicacion)
                #raise exceptions.ValidationError("tamaño "+str(len(self.x_studio_equipo_por_nmero_de_serie_1))+' ids '+ str(self.x_studio_equipo_por_nmero_de_serie_1.ids)+' serie '+str(self.x_studio_equipo_por_nmero_de_serie_1[len(self.x_studio_equipo_por_nmero_de_serie_1)-1].serie.name))
                se=0
                for serie in self.x_studio_equipo_por_nmero_de_serie_1:                    
                    if serie.serie.id == self.x_studio_equipo_por_nmero_de_serie_1[len(self.x_studio_equipo_por_nmero_de_serie_1)-1].serie.id and se != len(self.x_studio_equipo_por_nmero_de_serie_1)-1:
                       raise exceptions.ValidationError("Error serie ya agregada"+str(serie.serie.name))
                    se=se+1
                
            #queryt="select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!="+str(self.x_studio_id_ticket)+"  and h.stage_id!=18 and h.team_id=8 and  h.active='t' and stock_production_lot_id = "+str(self.x_studio_equipo_por_nmero_de_serie_1[0].serie.id)+" limit 1;"            
            #self.env.cr.execute(queryt)                        
            #informaciont = self.env.cr.fetchall()
            #_logger.info('informaciont: ' + str(informaciont))
            #Obtengo los
            serieExistente = False 
            for equipo in self.x_studio_equipo_por_nmero_de_serie_1:
                ticketsToner = self.env['helpdesk.ticket'].search([ ('x_studio_tipo_de_vale', '=', 'Requerimiento'), ('stage_id', '!=', 18), ('stage_id', '!=', 4) ])
                for ticket in ticketsToner:
                    listaDeSeriesEnTicketActual = []
                    for dca in ticket.x_studio_equipo_por_nmero_de_serie_1:
                        if dca.serie.id == equipo.serie.id:
                            listaDeSeriesEnTicketActual.append(dca.serie.id)
                            break
                    if listaDeSeriesEnTicketActual:
                        todasLasAlertas = todasLasAlertas + 'Estas agregando una serie de un ticket ya en proceso en equipo de toner. Ticket con misma serie: ' + str(ticket.id)
                        serieExistente = True
                        break
                        


        """
            verificando que el dca tenga la información suficiente con respecto a los cartuchos y verificando que no sea de minialmacen.
        """
        if self.team_id.id == 8 or self.x_studio_tipo_de_vale == 'Requerimiento':
            for dca in self.x_studio_equipo_por_nmero_de_serie_1:
                if dca.colorEquipo == 'Color':
                    if not dca.x_studio_cartuchonefro and not dca.x_studio_cartucho_amarillo and not dca.x_studio_cartucho_cian_1 and not dca.x_studio_cartucho_magenta:
                        self.noCrearTicket = True
                        mensajeTitulo = "Alerta!!!"
                        mensajeCuerpo = "Crearas un ticket sin cartucho seleccionado. Selecciona al menos uno para la serie " + str(dca.serie.name)
                        todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo
                elif dca.colorEquipo == 'B/N':
                    if not dca.x_studio_cartuchonefro:
                        self.noCrearTicket = True
                        mensajeTitulo = "Alerta!!!"
                        mensajeCuerpo = "Crearas un ticket sin cartucho seleccionado. Selecciona al menos uno para la serie " + str(dca.serie.name)
                        
                        todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo
                       
                if dca.serie.x_studio_mini:
                    self.x_studio_equipo_por_nmero_de_serie_1 = [(5,0,0)]
                    mensajeTitulo = "Alerta!!!"
                    mensajeCuerpo = "La serie " + str(dca.serie.name) + " pertenece a un mini almacén, no es posible crear el ticket de un mini almacén."
                    
                    todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo
                    




        """
        for record in self:
            cantidad_numeros_serie = record.x_studio_tamao_lista
            #if record.team_id.id != 8 and record.team_id.id != 13:
            if record.x_studio_tipo_de_vale != 'Requerimiento':
                if int(cantidad_numeros_serie) < 2 :
                    for numeros_serie in record.x_studio_equipo_por_nmero_de_serie:
                        ids.append(numeros_serie.id)
                        
                        #for move_line in numeros_serie.x_studio_move_line:
                            
                        #cliente = move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.parent_id.id
                        cliente = numeros_serie.x_studio_cliente
                        self._origin.sudo().write({'partner_id' : cliente.id})
                        record.partner_id = cliente.id
                        idM=self._origin.id
                        
                        if cliente:
                            self.env.cr.execute("update helpdesk_ticket set partner_id = " + str(cliente.id) + "  where  id = " + str(idM) + ";")
                        v['partner_id'] = cliente.id
                        cliente_telefono = cliente.phone
                        self._origin.sudo().write({'x_studio_telefono' : cliente_telefono})
                        record.x_studio_telefono = cliente_telefono
                        if cliente_telefono != []:
                            srtt="update helpdesk_ticket set x_studio_telefono = '" + str(cliente_telefono) + "' where  id = " + str(idM) + ";"                                
                        v['x_studio_telefono'] = cliente_telefono
                        cliente_movil = cliente.mobile
                        self._origin.sudo().write({'x_studio_movil' : cliente_movil})
                        record.x_studio_movil = cliente_movil
                        if cliente_movil == []:
                            self.env.cr.execute("update helpdesk_ticket set x_studio_movil = '" + str(cliente_movil) + "' where  id = " +idM + ";")
                        v['x_studio_movil'] = cliente_movil
                        
                        cliente_nivel = cliente.x_studio_nivel_del_cliente
                        self._origin.sudo().write({'x_studio_nivel_del_cliente' : cliente_nivel})
                        record.x_studio_nivel_del_cliente = cliente_nivel
                        if cliente_nivel == []:
                            self.env.cr.execute("update helpdesk_ticket set x_studio_nivel_del_cliente = '" + str(cliente_nivel) + "' where  id = " + idM + ";")
                        v['x_studio_nivel_del_cliente'] = cliente_nivel


                        localidad = numeros_serie.x_studio_localidad_2

                        self._origin.sudo().write({'x_studio_empresas_relacionadas' : localidad.id})
                        record.x_studio_empresas_relacionadas = localidad.id

                        if record.x_studio_empresas_relacionadas.id != False:
                            self.env.cr.execute("select * from res_partner where id = " + str(record.x_studio_empresas_relacionadas.id) + ";")
                            localidad_tempo = self.env.cr.fetchall()
                            if str(localidad_tempo[0][80]) != 'None':
                                record.x_studio_field_29UYL = str(localidad_tempo[0][80])

                            #self._origin.sudo().write({'x_studio_field_6furK' : self._origin.sudo().write({'x_studio_field_6furK' : move_line.location_dest_id.x_studio_field_JoD2k.x_studio_field_E0H1Z.x_studio_field_SqU5B})})
                        lista_ids = []
                        for id in ids:
                            lista_ids.append((4,id))
                        
                        v['x_studio_equipo_por_nmero_de_serie'] = lista_ids
                        self._origin.sudo().write({'x_studio_equipo_por_nmero_de_serie' : lista_ids})
                        record.x_studio_equipo_por_nmero_de_serie = lista_ids
                else:
                    raise exceptions.ValidationError("No es posible registrar más de un número de serie")
            #if record.team_id.id == 8 or record.team_id.id == 13:
            if record.x_studio_tipo_de_vale == 'Requerimiento':
                _my_object = self.env['helpdesk.ticket']

                for numeros_serie in record.x_studio_equipo_por_nmero_de_serie_1:
                    ids.append(numeros_serie.serie.id)

                    #Cliente
                    clienteId = numeros_serie.serie.x_studio_cliente
                    self.partner_id = clienteId.id
                    self.x_studio_nivel_del_cliente = clienteId.x_studio_nivel_del_cliente
                    #Localidad
                    localidadTemp = numeros_serie.serie.x_studio_localidad_2
                    self.x_studio_empresas_relacionadas = localidadTemp.id
                    self.x_studio_field_6furK = localidadTemp.x_studio_field_SqU5B
                    self.x_studio_zona = localidadTemp.x_studio_field_SqU5B
                    self.zona_estados = localidadTemp.state_id.name
                    #self.localidadContacto = 
                    self.x_studio_estado_de_localidad = localidadTemp.state_id.name
                    self.telefonoLocalidadContacto = localidadTemp.phone
                    self.movilLocalidadContacto = localidadTemp.mobile
                    self.correoLocalidadContacto = localidadTemp.email

                    lista_ids = []
                    for id in ids:
                        lista_ids.append((4,id))
                    
        
        """

        #if int(self.x_studio_tamao_lista) > 0 and (self.team_id.id != 8 and self.team_id.id != 13):
        if int(self.x_studio_tamao_lista) > 0 and (self.x_studio_tipo_de_vale != 'Requerimiento'):
            
            query="select h.id from helpdesk_ticket_stock_production_lot_rel s, helpdesk_ticket h where h.id=s.helpdesk_ticket_id and h.id!="+str(self.x_studio_id_ticket)+"  and h.stage_id!=18 and h.team_id!=8 and  h.active='t' and stock_production_lot_id = "+str(self.x_studio_equipo_por_nmero_de_serie[0].id)+" limit 1;"            
            
            self.env.cr.execute(query)                        
            informacion = self.env.cr.fetchall()
            if len(informacion) > 0:
                message = 'Estas agregando una serie de un ticket ya en proceso. Ticket: ' + str(informacion[0][0]) + '\n '
                
                todasLasAlertas = todasLasAlertas + '\n\n' + message
                
                #raise exceptions.ValidationError("No es posible registrar número de serie, primero cerrar el ticket con el id  "+str(informacion[0][0]))
        #if len(self.x_studio_equipo_por_nmero_de_serie_1) > 0 and (self.team_id.id == 8 or self.team_id.id == 13):
        

        """
            Verificando que los equipos tengan servicio
        """
        if self.x_studio_tipo_de_vale == 'Requerimiento' and self.x_studio_equipo_por_nmero_de_serie_1:
            equipoSinServicio = False
            mensajeCuerpo = 'No se puede agregar un equipo sin servicio.\nLos equipos que no tienen servicio son:\n\n'
            for equipo in self.x_studio_equipo_por_nmero_de_serie_1:
                if not equipo.serie.servicio:
                    mensajeCuerpo = mensajeCuerpo + 'Equipo: ' + str(equipo.serie.product_id.name) + ' Serie: ' + str(equipo.serie.name) + '\n'
                    equipoSinServicio = True
                    self.x_studio_equipo_por_nmero_de_serie_1 = ''
            if equipoSinServicio:
                mensajeTitulo = 'Alerta ticket sin servicio creado'
                todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo

        if self.x_studio_tipo_de_vale != 'Requerimiento' and self.x_studio_equipo_por_nmero_de_serie:
            equipoSinServicio = False
            mensajeCuerpo = 'No se puede agregar un equipo sin servicio.\nLos equipos que no tienen servicio son:\n\n'
            for equipo in self.x_studio_equipo_por_nmero_de_serie:
                if not equipo.servicio:
                    mensajeCuerpo = mensajeCuerpo + 'Equipo: ' + str(equipo.product_id.name) + ' Serie: ' + str(equipo.name) + '\n'
                    equipoSinServicio = True
                    self.x_studio_equipo_por_nmero_de_serie = ''
            if equipoSinServicio:
                mensajeTitulo = 'Alerta ticket sin servicio creado'
                todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo

        """
            Verificando que los equipos no sean de venta directa
        """
        if self.x_studio_tipo_de_vale == 'Requerimiento' and self.x_studio_equipo_por_nmero_de_serie_1:
            equipoSinServicio = False
            mensajeCuerpo = 'No se puede agregar un equipo de venta directa.\nLos equipos en venta directa son:\n\n'
            for equipo in self.x_studio_equipo_por_nmero_de_serie_1:
                if equipo.serie.x_studio_venta:
                    mensajeCuerpo = mensajeCuerpo + 'Equipo: ' + str(equipo.serie.product_id.name) + ' Serie: ' + str(equipo.serie.name) + '\n'
                    equipoSinServicio = True
                    self.x_studio_equipo_por_nmero_de_serie_1 = ''
            if equipoSinServicio:
                mensajeTitulo = 'Alerta ticket sin servicio creado'
                todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo

        if self.x_studio_tipo_de_vale != 'Requerimiento' and self.x_studio_equipo_por_nmero_de_serie:
            equipoSinServicio = False
            mensajeCuerpo = 'No se puede agregar un equipo de venta directa.\nLos equipos en venta directa son:\n\n'
            for equipo in self.x_studio_equipo_por_nmero_de_serie:
                if equipo.x_studio_venta:
                    mensajeCuerpo = mensajeCuerpo + 'Equipo: ' + str(equipo.product_id.name) + ' Serie: ' + str(equipo.name) + '\n'
                    equipoSinServicio = True
                    self.x_studio_equipo_por_nmero_de_serie = ''
            if equipoSinServicio:
                mensajeTitulo = 'Alerta ticket sin servicio creado'
                todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo


        """
            Verificando que los equipos no sean demos
        """
        if self.x_studio_tipo_de_vale == 'Requerimiento' and self.x_studio_equipo_por_nmero_de_serie_1:
            equipoSinServicio = False
            mensajeCuerpo = 'Se agregará un equipo que esta en demostración.\nLos equipos en demostración son:\n\n'
            for equipo in self.x_studio_equipo_por_nmero_de_serie_1:
                if equipo.serie.x_studio_demo:
                    mensajeCuerpo = mensajeCuerpo + 'Equipo: ' + str(equipo.serie.product_id.name) + ' Serie: ' + str(equipo.serie.name) + '\n'
                    equipoSinServicio = True
                    #self.x_studio_equipo_por_nmero_de_serie_1 = ''
            if equipoSinServicio:
                mensajeTitulo = 'Alerta ticket sin servicio creado'
                todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo

        if self.x_studio_tipo_de_vale != 'Requerimiento' and self.x_studio_equipo_por_nmero_de_serie:
            equipoSinServicio = False
            mensajeCuerpo = 'Se agregará un equipo que esta en demostración.\nLos equipos en demostración son:\n\n'
            for equipo in self.x_studio_equipo_por_nmero_de_serie:
                if equipo.x_studio_demo:
                    mensajeCuerpo = mensajeCuerpo + 'Equipo: ' + str(equipo.product_id.name) + ' Serie: ' + str(equipo.name) + '\n'
                    equipoSinServicio = True
                    #self.x_studio_equipo_por_nmero_de_serie = ''
            if equipoSinServicio:
                mensajeTitulo = 'Alerta ticket sin servicio creado'
                todasLasAlertas = todasLasAlertas + '\n\n' + mensajeCuerpo




        if todasLasAlertas:
            mensajeTitulo = 'Alertas generadas durante la asignación del equipo !!!'
            warning = {
                                'title': _(mensajeTitulo), 
                                'message': _(todasLasAlertas)
                    }
            return {'warning': warning}


    cambioDespuesDeCierre = fields.Boolean(string = '¿Cambio despues de cierre?', default = False)

    def comprobar_cerrados(self):
        if self.stage_id.id != 18 or self.stage_id.id != 4:
            for diagnostico in self.diagnosticos:
                if diagnostico.estadoTicket == 'Cerrado' and self.diagnosticos[-1].estadoTicket != 'Cerrado':
                    self.cambioDespuesDeCierre = True
                    break


    @api.onchange('x_studio_tipo_de_vale')
    def registrarTipoDeReporte(self):
        if self.x_studio_tipo_de_vale:
            comentarioGenerico = 'Se seleccionó ' + self.x_studio_tipo_de_vale + ' como tipo de reporte. Seleccion realizada por ' + str(self.env.user.name) +'.'
            estado = self.stage_id.name
            self.creaDiagnosticoVistaLista(comentarioGenerico, estado)

    
    @api.onchange('x_studio_field_6furK', 'x_studio_estado_de_localidad', 'x_studio_zona', 'zona_estados')
    def actualiza_todas_las_zonas(self):
        lista_zonas = []
        if self.x_studio_field_6furK:
            lista_zonas.append(str(self.x_studio_field_6furK))
        if self.x_studio_zona:
            lista_zonas.append(str(self.x_studio_zona))
        if self.zona_estados:
            lista_zonas.append(str(self.zona_estados))
        if self.x_studio_zona_cliente:
            lista_zonas.append(str(self.x_studio_zona_cliente))
        vals = {
            'x_todas_las_zonas': str(lista_zonas)
        }
        if lista_zonas:
            self.write(vals)


    
    @api.model
    def message_new(self, msg, custom_values=None):
        values = dict(custom_values or {}, partner_email=msg.get('from'), partner_id=msg.get('author_id'))

        
        if(("gnsys.mx" in str(msg.get('from'))) or ("scgenesis.mx" in str(msg.get('from')))):
            return 0
        ticket = super(helpdesk_update, self).message_new(msg, custom_values=values)

        partner_ids = [x for x in ticket._find_partner_from_emails(self._ticket_email_split(msg)) if x]
        customer_ids = ticket._find_partner_from_emails(tools.email_split(values['partner_email']))
        partner_ids += customer_ids

        if customer_ids and not values.get('partner_id'):
            ticket.partner_id = customer_ids[0]
        if partner_ids:
            ticket.message_subscribe(partner_ids)
        return ticket
   
          
    def actualizaHistorialComponentes(self):
        _logger.info('------ Inicio actualizaHistorialComponentes ------ inicio hora: ' + str( datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        #tickets = self.env['helpdesk.ticket'].search([('id', '=', 32166)], limit = 1)
        tickets = self.env['helpdesk.ticket'].search([('create_date', '>=', '2020-07-24'), ('x_studio_tipo_de_vale', '!=', 'Requerimiento'), ('x_studio_tipo_de_vale', '!=', 'Resurtido de Almacen'), ('x_studio_field_nO7Xg', '!=', None)], order = 'create_date desc')
        _logger.info('tickets: ' + str(len(tickets)) + ' tickets[0]: ' + str(tickets[0]))
        

        for ticket in tickets:
            _logger.info('------Inicio creacion de componente ticket ' + str(ticket.id) + ' ------ inicio hora: ' + str( datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
            fuenteDca = 'stock.production.lot'
            dcaObj = self.env['dcas.dcas'].search([('serie', '=', ticket.x_studio_equipo_por_nmero_de_serie[0].name),('fuente', '=', fuenteDca), ('x_studio_tickett','=',str(ticket.id))], order = 'create_date desc', limit = 1)
            if not dcaObj:
                dcaObj = self.env['dcas.dcas'].search([('serie', '=', ticket.x_studio_equipo_por_nmero_de_serie[0].name),('fuente', '=', fuenteDca)], order = 'x_studio_fecha desc', limit = 1)
            _logger.info('dcaObj: ' + str(dcaObj))
            
            saleOrder = ticket.x_studio_field_nO7Xg
            _logger.info('saleOrder: ' + str(saleOrder))

            saleOrderLine = saleOrder.order_line
            _logger.info('saleOrderLine: ' + str(saleOrderLine))



            for linea in saleOrderLine:
                _logger.info('linea.: ' + str(linea.product_uom_qty))
                if linea.product_uom_qty > 0:
                    crear = True
                    refaccionesTextTemp = 'Refacción y/o accesorio: ' + str(linea.product_id.display_name) + '. Descripción: ' + str(linea.product_id.description) + '.'
                    componentesPrevios = self.env['x_studio_historico_de_componentes'].search([('x_studio_ticket', '=', str(saleOrder.x_studio_field_bxHgp.id)) ] )
                    for componente in componentesPrevios:
                        if componente.x_studio_modelo == refaccionesTextTemp:
                            crear = False
                            break
                    if crear:
                        idComponenteCreado = self.env['x_studio_historico_de_componentes'].create({
                                                                                                    'x_studio_cantidad': linea.product_uom_qty,
                                                                                                    'x_studio_field_MH4DO': linea.x_studio_field_9nQhR.id,
                                                                                                    #'x_studio_ticket': str(saleOrder.x_studio_field_bxHgp.id),
                                                                                                    'x_studio_ticket': str(ticket.id),
                                                                                                    'x_studio_contador_color': dcaObj.contadorColor if (dcaObj) else 0,
                                                                                                    'x_studio_fecha_de_entrega': linea.write_date,
                                                                                                    'x_studio_modelo': refaccionesTextTemp,
                                                                                                    'x_studio_contador_bn': dcaObj.contadorMono if (dcaObj) else 0,
                                                                                                    'x_studio_creado_por_script': True
                                                                                                })
                        _logger.info('historico de componente creado idComponenteCreado: ' + str(idComponenteCreado.id))
            _logger.info('------Fin creacion de componente ticket ' + str(ticket.id) + ' ------ fin hora: '+ str( datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
        _logger.info('------ Fin actualizaHistorialComponentes ------ fin hora: ' + str( datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))



    diagnosticos = fields.One2many('helpdesk.diagnostico', 'ticketRelacion', string = 'Diagnostico', track_visibility = 'onchange', copy=True)

    validacionesRefaccion = fields.One2many('helpdesk.validacion.so', 'ticketRelacion', string = 'Validaciones de refacciones', store = True)


    accesorios = fields.One2many('helpdesk.refacciones', 'ticketRela', string = 'Accesorios')


    """
    en produccion
    ordenes = fields.One2many('sale.order', 'x_studio_field_bxHgp', string = 'Ordenes')
    """

    
    #order_line = fields.One2many('helpdesk.lines','ticket',string='Order Lines')
    
    def cambio_wizard(self):
        wiz = self.env['helpdesk.comentario'].create({'ticket_id':self.id })
        view = self.env.ref('helpdesk_update.view_helpdesk_comentario')
        return {
            'name': _('Diagnostico'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.comentario',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }


    
    def no_validar_con_comentario_wizard(self):
        wiz = self.env['helpdesk.comentario.no.validar'].create({'ticket_id':self.id })
        view = self.env.ref('helpdesk_update.view_helpdesk_no_validar_con_comentario')
        return {
            'name': _('No validar'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.comentario.no.validar',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    
    def resuelto_con_comentario_wizard(self):
        wiz = self.env['helpdesk.comentario.resuelto'].create({'ticket_id':self.id })
        view = self.env.ref('helpdesk_update.view_helpdesk_resuleto_con_comentario')
        return {
            'name': _('Resuelto'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.comentario.resuelto',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    
    def cerrar_con_comentario_wizard(self):
        wiz = self.env['helpdesk.comentario.cerrar'].create({'ticket_id':self.id })
        view = self.env.ref('helpdesk_update.view_helpdesk_cerrar_con_comentario')
        return {
            'name': _('Cerrar'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.comentario.cerrar',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    
    def cancelar_con_comentario_wizard(self):
        wiz = self.env['helpdesk.comentario.cancelar'].create({'ticket_id':self.id })
        view = self.env.ref('helpdesk_update.view_helpdesk_cancelar_con_comentario')
        return {
            'name': _('Cancelar'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.comentario.cancelar',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    
    def contadores_wizard(self):
        wiz = self.env['helpdesk.contadores'].create({'ticket_id':self.id})
        view = self.env.ref('helpdesk_update.view_helpdesk_contadores')
        return {
            'name': _('Contadores'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.contadores',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    
    def contacto_wizard(self):
        wiz = self.env['helpdesk.contacto'].create({'ticket_id':self.id})
        view = self.env.ref('helpdesk_update.view_helpdesk_contacto')
        return {
            'name': _('Agregar contacto a localidad'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.contacto',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    
    def detalle_serie_wizard(self):
        wiz = self.env['helpdesk.detalle.serie'].create({'ticket_id':self.id})
        view = self.env.ref('helpdesk_update.view_helpdesk_bitacora')
        return {
            'name': _('Bitacora'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.detalle.serie',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }        

    
    def reincidencia_wizard(self):
        wiz = self.env['helpdesk.reincidencia'].create({'ticket_id':self.id})
        view = self.env.ref('helpdesk_update.view_helpdesk_reincidencia')
        return {
            'name': _('Generar reincidencia'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.reincidencia',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }   


    
    def detalle_toner_wizard(self):
        wiz = self.env['helpdesk.datos.toner'].create({
                                                        'ticket_id': self.id
                                                    })
        idExterno = 'studio_customization.tiquete_del_servicio_e501a40f-0bd7-4726-b219-50085c31c177'
        idExternoToner = 'studio_customization.tiquete_del_servicio_8a770195-f5a2-4b6c-b905-fc0ff46c1258'
        pdf = self.env.ref(idExternoToner).sudo().render_qweb_pdf([self.id])[0]
        wiz.pdfToner = base64.encodestring(pdf)
        view = self.env.ref('helpdesk_update.view_helpdesk_detalle_toner')
        return {
            'name': _('Datos tóner'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.datos.toner',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    
    def detalle_mesa_wizard(self):

        wiz = self.env['helpdesk.datos.mesa'].search([('ticket_id', '=', self.id)], order = 'create_date desc', limit = 1 )
        _logger.info('3312: wizar existente? : ' + str(wiz))
        if not wiz:
            wiz = self.env['helpdesk.datos.mesa'].create({
                                                            'ticket_id': self.id
                                                        })
        if self.x_studio_equipo_por_nmero_de_serie:
            #wiz.series = [(6, 0, self.x_studio_equipo_por_nmero_de_serie.ids)]
            seriesDatos = ''
            #serieTextoInicial = ''
            #for serie in self.x_studio_equipo_por_nmero_de_serie:
            seriesDatos = seriesDatos + """
                                        <tr>
                                            <td>""" + str(self.x_studio_equipo_por_nmero_de_serie[0].name) + """</td>
                                            <td>""" + str(self.x_studio_equipo_por_nmero_de_serie[0].product_id.display_name) + """</td>
                                            <td>""" + str(self.x_studio_equipo_por_nmero_de_serie[0].x_studio_ultima_ubicacin) + """</td>
                                            <td>""" + str(self.x_studio_equipo_por_nmero_de_serie[0].x_studio_color_bn) + """</td>
                                        </tr>
                                    """
                #if serieTextoInicial:
                #    serieTextoInicial = str(serieTextoInicial) + ', ' + str(serie.name)
                #else:
                #    serieTextoInicial = str(x_studio_equipo_por_nmero_de_serie[0].name) + ', '
            wiz.seriesText = """
                                    <table class='table table-bordered table-secondary text-black'>
                                        <thead>
                                            <tr>
                                                <th scope='col'>Número de serie</th>
                                                <th scope='col'>Producto</th>
                                                <th scope='col'>Ultima unicación</th>
                                                <th scope='col'>Color o B/N</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            """ + seriesDatos +"""
                                        </tbody>
                                    </table>
                                """
            wiz.serie = str(self.x_studio_equipo_por_nmero_de_serie[0].name)
            
        if self.accesorios:
            #wiz.refacciones = [(6, 0, self.x_studio_productos.ids)]
            refaccionesDatos = ''
            for refaccion in self.accesorios:
                refaccionesDatos = refaccionesDatos + """
                                        <tr>
                                            <td>""" + str(refaccion.productos.display_name) + """</td>
                                            <td>""" + str(refaccion.cantidadPedida) + """</td>
                                        </tr>
                                    """

            wiz.refaccionesText = """
                                    <table class='table table-bordered table-secondary text-black'>
                                        <thead>
                                            <tr>
                                                <th scope='col'>Producto</th>
                                                <th scope='col'>Cantidad a pedir</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            """ + refaccionesDatos +"""
                                        </tbody>
                                    </table>
                                """
        if self.partner_id:
            wiz.cliente = self.partner_id.name
        if self.x_studio_nivel_del_cliente:
            wiz.tipoCliente = self.x_studio_nivel_del_cliente
        if self.x_studio_empresas_relacionadas:
            wiz.localidad = self.x_studio_empresas_relacionadas.name
        if self.x_studio_field_6furK:
            wiz.zonaLocalidad = self.x_studio_field_6furK
        if self.localidadContacto:
            wiz.localidadContacto = self.localidadContacto.name
        if self.x_studio_estado_de_localidad:
            wiz.estadoLocalidad = self.x_studio_estado_de_localidad
        if self.telefonoLocalidadContacto:
            wiz.telefonoContactoLocalidad = self.telefonoLocalidadContacto
        if self.movilLocalidadContacto:
            wiz.movilContactoLocalidad = self.movilLocalidadContacto
        if self.correoLocalidadContacto:
            wiz.correoContactoLocalidad = self.correoLocalidadContacto
        if self.direccionLocalidadText:
            wiz.direccionLocalidad = self.direccionLocalidadText
        if self.create_date:
            timezone = pytz.timezone('America/Mexico_City')
            wiz.creadoEl = str(self.create_date.astimezone(timezone).strftime("%d/%m/%Y %H:%M:%S")) #str(pytz.utc.localize(self.create_date, is_dst=None).astimezone(pytz.timezone('America/Mexico_City')).strftime("%Y/%m/%d %H:%M:%S"))  #str(self.create_date.strftime("%d/%m/%Y %H:%M:%S"))
        #str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") )
        if self.days_difference:
            wiz.diasAtraso = self.days_difference
        if self.priority:
            wiz.prioridad = self.priority
        if self.x_studio_zona:
            wiz.zona = self.x_studio_zona
        if self.zona_estados:
            wiz.zonaEstados = self.zona_estados
        if self.x_studio_nmero_de_ticket_cliente:
            wiz.numeroTicketCliente = self.x_studio_nmero_de_ticket_cliente
        if self.x_studio_nmero_ticket_distribuidor_1:
            wiz.numeroTicketDistribuidor = self.x_studio_nmero_ticket_distribuidor_1
        if self.x_studio_nmero_de_guia_1:
            wiz.numeroTicketGuia = self.x_studio_nmero_de_guia_1
        if self.x_studio_comentarios_de_localidad:
            wiz.comentarioLocalidad = self.x_studio_comentarios_de_localidad
        if self.tiempoDeAtrasoTicket:
            wiz.tiempoAtrasoTicket = self.tiempoDeAtrasoTicket
        if self.tiempoDeAtrasoAlmacen:
            wiz.tiempoAtrasoAlmacen = self.tiempoDeAtrasoAlmacen
        if self.tiempoDeAtrasoDistribucion:
            wiz.tiempoAtrasoDistribucion = self.tiempoDeAtrasoDistribucion


        if self.stage_id:
            wiz.etapa = self.stage_id.name
        if self.x_studio_tipo_de_vale:
            wiz.tipoDeReporte = self.x_studio_tipo_de_vale
        #if self.diagnosticos:
        #    wiz.diagnostico_id = [(6, 0, self.diagnosticos.ids)]

        idExternoToner = 'studio_customization.tiquete_del_servicio_e501a40f-0bd7-4726-b219-50085c31c177'
        pdf = self.env.ref(idExternoToner).sudo().render_qweb_pdf([self.id])[0]
        wiz.pdfToner = base64.encodestring(pdf)
        view = self.env.ref('helpdesk_update.view_helpdesk_detalle_mesa')
        return {
            'name': _('Más información'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.datos.mesa',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }


    
    def detalle_serie_toner_wizard(self):
        ids = []
        for dca in self.x_studio_equipo_por_nmero_de_serie_1:
            ids.append(dca.serie.id)
        _logger.info('hola1: ' + str(ids))
        wiz = self.env['helpdesk.detalle.serie.toner'].create({'ticket_id':self.id})
        view = self.env.ref('helpdesk_update.view_helpdesk_bitacora_toner')
        return {
            'name': _('Bitacora'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.detalle.serie.toner',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'domain': [["series", "=", ids]],
            #'context': self.env.context,
            'context': {'dominioTest': str(ids)},
        }


    #
    def agregar_productos_wizard(self):
        if self.stage_id.id == 18 or self.stage_id.id == 4:
            mensajeTitulo = 'Estado no valido'
            mensajeCuerpo = 'No es posible agregar productos al ticket ' + str(self.id) + ' en el estado ' + str(self.stage_id.name) + '\nSolo se permite añadir productos si el ticket no esta Cerrado o Cancelado.'
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
        else:
            wiz = self.env['helpdesk.agregar.productos'].create({'ticket_id':self.id})
            lista = [[5, 0, 0]]
            if self.accesorios:
                for refaccion in self.accesorios:
                    lista.append( [0, 0, {
                                            'productos': refaccion.productos.product_variant_id.id,
                                            'cantidadPedida': refaccion.cantidadPedida,
                                            'wizRela': wiz.id
                                }])
                _logger.info('3312: lista: ' + str(lista) )
                wiz.write({'accesorios': lista})
            #wiz.accesorios = lista
            #wiz.productos = [(6, 0, self.x_studio_productos.ids)]
            if self.x_studio_field_nO7Xg:
                wiz.estadoSolicitud = str(self.x_studio_field_nO7Xg.state)
            else:
                wiz.estadoSolicitud = 'No existe una SO.'
            view = self.env.ref('helpdesk_update.view_helpdesk_agregar_productos')
            return {
                'name': _('Agregar productos'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'helpdesk.agregar.productos',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                #'domain': [["series", "=", ids]],
                #'context': self.env.context,
                'context': self.env.context,
            }


    #
    def helpdesk_confirmar_validar_refacciones_wizard(self):
        _logger.info('***** Inicio de helpdesk_confirmar_validar_refacciones_wizard: ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ) + ' *****')
        wiz = self.env['helpdesk.confirmar.validar.refacciones'].create({'ticket_id':self.id})
        wiz_id = wiz.mapped('id')
        #wiz.productos = [(6, 0, self.x_studio_productos.ids)]
        productos = self.mapped('accesorios')
        pedido_de_venta_id = self.mapped('x_studio_field_nO7Xg.id')
        pedido_de_venta_estado = self.mapped('x_studio_field_nO7Xg.state')
        pedido_de_venta_lineas_pedido = self.mapped('x_studio_field_nO7Xg.order_line')
        productos_en_liean_de_pedido = []
        for linea in pedido_de_venta_lineas_pedido:
            productos_en_liean_de_pedido.append(linea.product_id.id)

        #pedido_de_venta_lineas_pedido_default_code = self.mapped('x_studio_field_nO7Xg.order_line.product_id.default_code')
        _logger.info('productos_en_liean_de_pedido: ' + str(productos_en_liean_de_pedido))
        estado_ticket_name = self.mapped('stage_id.name')
        diagnosticos = self.mapped('diagnosticos')

        equipos = self.mapped('x_studio_equipo_por_nmero_de_serie')

        vals_wiz = {}
        """
        if productos:
            for refaccion in productos:
                lista.append( [0, 0, {
                                        'productos': refaccion.product_variant_id.id,
                                        'cantidadPedida': refaccion.x_studio_cantidad_pedida,
                                        'wizRelaVal': wiz.id,
                                        'referenciaInterna': refaccion.default_code,
                                        'nombreProducto': refaccion.name,
                                        'descripcion': refaccion.description,
                                        'cantidadAMano': refaccion.qty_available
                            }])
            _logger.info('3312: lista: ' + str(lista) )
            wiz.write({'accesorios': lista})
        """
        vals_wiz['contadoresAnterioresText'] = self.contadoresAnteriores()
        if productos:
            refaccionesEnCero = ''
            lista = [[5, 0, 0]]
            for refaccion in productos:
                cantidad_pedidad = refaccion.mapped('cantidadPedida')
                _logger.info('refaccion.productos.id: ' + str(refaccion.productos.id))
                if not refaccion.productos.id in productos_en_liean_de_pedido: #and not refaccion.default_code in pedido_de_venta_lineas_pedido_default_code:
                    lista.append( [0, 0, {
                                            'productos': refaccion.productos.id,
                                            'cantidadPedida': cantidad_pedidad[0],
                                            'wizRelaVal': wiz_id[0]
                                }])
                if not cantidad_pedidad[0]:
                    refaccionesEnCero = refaccionesEnCero + """
                                                                <tr>
                                                                    <td>""" + str(refaccion.productos.categ_id.name) + """</td>
                                                                    <td>""" + str(refaccion.productos.product_variant_id.display_name) + """</td>
                                                                    <td>""" + str(cantidad_pedidad) + """</td>
                                                                </tr>
                                                            """
            _logger.info('3312: lista: ' + str(lista) )
            
            #wiz.write({'accesorios': lista})
            vals_wiz['accesorios'] = lista
            mensajesAlerta = ''
            if refaccionesEnCero != '':
                mensajesAlerta = """
                                        <div class='alert alert-info' role='alert'>
                                            <h4 class="alert-heading">Validación de refaciones y/o accesorios en cero !!!</h4>

                                            <p>Se validaran refacciones y/o accesorios con cantidad en cero. Los equipos son los siguientes: </p>
                                            <br/>
                                            <div class='row'>
                                                <table class='table table-bordered table-warning text-black'>
                                                    <thead >
                                                        <tr>
                                                            <th scope='col'>Categoría del producto</th>
                                                            <th scope='col'>Refacción y/o accesorio</th>
                                                            <th scope='col'>Cantidad a pedir</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        """ + refaccionesEnCero + """
                                                    </tbody>
                                                </table>
                                            </div>    
                                        </div>      
                                    """
            else:
                mensajesAlerta = ''
            vals_wiz['mensajesAlerta'] = mensajesAlerta

        
        if pedido_de_venta_id:
            vals_wiz['solicitud'] = pedido_de_venta_id[0]
            if pedido_de_venta_estado[0] == 'sale':
                vals_wiz['estadoSolicitud'] = 'Solicitud validada'
            else:
                vals_wiz['estadoSolicitud'] = 'Solicitud no validada'

        else:
            vals_wiz['estadoSolicitud'] = 'No hay solicitud'

        vals_wiz['estado'] = estado_ticket_name

        lista_diagnosticos = [[5, 0, 0]]
        for diagnostico in diagnosticos:
            #evidencias = diagnostico.mapped('evidencia.ids')
            """
            vals_diagnostico = {
                #'ticketRelacion': diagnostico.ticketRelacion.id,
                #'ticket_techra': diagnostico.ticket_techra.id,
                'create_date': diagnostico.create_date,
                'ticket_techra_text': diagnostico.ticket_techra_text,
                'estadoTicket': diagnostico.estadoTicket,
                'comentario': diagnostico.comentario,
                'evidencia': [(6, 0, diagnostico.evidencia.ids)],
                'mostrarComentario': diagnostico.mostrarComentario,
                'creadoPorSistema': diagnostico.creadoPorSistema,
                'fechaDiagnosticoTechra': diagnostico.fechaDiagnosticoTechra,
                'tipoSolucionTechra': diagnostico.tipoSolucionTechra,
                'tecnicoTechra': diagnostico.tecnicoTechra,
                'creado_por_techra': diagnostico.creado_por_techra,
                'href_diagnostico_ticket_techra': diagnostico.href_diagnostico_ticket_techra,
                'fecha_diagnostico_techra_text': diagnostico.fecha_diagnostico_techra_text
            }
            
            lista_diagnosticos.append([0, 0, vals_diagnostico])
            """
            lista_diagnosticos.append([4, diagnostico.id])

        vals_wiz['diagnostico_id'] = lista_diagnosticos




        if equipos:
            #self.serie = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name
            vals_wiz['serie'] = """
                            <table class='table table-bordered table-dark text-white'>
                                <thead >
                                    <tr>
                                        <th scope='col'>Número de serie</th>
                                        <th scope='col'>Modelo</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>""" + str(equipos[0].name) + """</td>
                                        <td>""" + str(equipos[0].x_studio_modelo_equipo) + """</td>
                                        
                                    </tr>
                                </tbody>
                            </table>
                        """
        #if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            
            componentes = self.env['x_studio_historico_de_componentes'].search([ '&', '|', ('x_ultimaCargaRefacciones', '=', True), ('x_studio_modelo', 'ilike', 'Refacción y/o accesorio:'), ('x_studio_field_MH4DO', '=', equipos[0].id) ])
            #_logger.info('len:    ' + str(componentes))
           # query = """ selec id from x_studio_historico_de_componentes where "x_studio_modelo" = 'f' and  "x_ultimaCargaRefacciones" = 't' or """ 
            #_logger.info('**** componentes: ' + str(componentes))
            #self.historicoDeComponentes = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_histrico_de_componentes.ids
            componentes = componentes.filtered(lambda componente:  componente.x_studio_field_MH4DO.name == str(equipos[0].name) and (componente.x_ultimaCargaRefacciones == True or 'Refacción y/o accesorio:' in componente.x_studio_modelo) )
            #lista_componentes = [(5, 0, 0)]
            lista_componentes = []
            if componentes:
                for componente in componentes:
                    """
                    vals_componente = {
                        'create_date': componente.create_date,
                        'write_uid': componente.write_uid,
                        'write_date': componente.write_date,
                        'create_uid': componente.create_uid,
                        'x_studio_creado_por_script': componente.x_studio_creado_por_script,
                        'x_ultimaCargaRefacciones': componente.x_ultimaCargaRefacciones,
                        'x_studio_field_MH4DO': componente.x_studio_field_MH4DO.id,
                        'x_tipo': componente.x_tipo,
                        'x_studio_modelo': componente.x_studio_modelo,
                        'x_studio_cantidad': componente.x_studio_cantidad,
                        'x_studio_fecha_de_entrega': componente.x_studio_fecha_de_entrega,
                        'x_studio_ticket': componente.x_studio_ticket,
                        'x_studio_contador_bn': componente.x_studio_contador_bn,
                        'x_studio_color': componente.x_studio_color
                    }
                    """

                    lista_componentes.append([4, componente.id])

                vals_wiz['historicoDeComponentes'] = lista_componentes



        #_logger.info(vals_wiz)
        wiz.write(vals_wiz)

        _logger.info('***** Fin de helpdesk_confirmar_validar_refacciones_wizard: ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ) + ' *****')

        view = self.env.ref('helpdesk_update.view_helpdesk_crear_y_validar_refacciones')
        view_id = view.mapped('id')
        return {
            'name': _('Crear y validar solicitud de refacciones'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.confirmar.validar.refacciones',
            'views': [(view_id[0], 'form')],
            'view_id': view_id[0],
            'target': 'new',
            'res_id': wiz_id[0],
            #'domain': [["series", "=", ids]],
            #'context': self.env.context,
            'context': self.env.context,
        }

    
    def reiniciar_contadores_wizard(self):
        wiz = self.env['helpdesk.contadores.reiniciar.mesa'].create({'ticket_id': self.id})
        #wiz.productos = [(6, 0, self.x_studio_productos.ids)]
        view = self.env.ref('helpdesk_update.view_helpdesk_reiniciar_contadores')
        return {
            'name': _('Reiniciar contadores'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.contadores.reiniciar.mesa',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            #'domain': [["series", "=", ids]],
            #'context': self.env.context,
            'context': self.env.context,
        }

    
    def editar_contadores_wizard(self):
        wiz = self.env['helpdesk.contadores.editar.mesa'].create({'ticket_id': self.id})
        #wiz.productos = [(6, 0, self.x_studio_productos.ids)]
        view = self.env.ref('helpdesk_update.view_helpdesk_editar_contadores')
        return {
            'name': _('Editar contadores'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.contadores.editar.mesa',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            #'domain': [["series", "=", ids]],
            #'context': self.env.context,
            'context': self.env.context,
        }
#AGrego CEsar
    @api.onchange('partner_id')
    def cambiosParent_id(self):
        res = {}
        for record in self:
            if record.partner_id.id:
                hijos = self.env['res.partner'].search([['parent_id', '=', record.partner_id.id], ['x_studio_cobranza_o_facturacin', '=', False] ])
                hijosarr = hijos.mapped('id')
                nietos = self.env['res.partner'].search([['parent_id', 'in', hijosarr],['type', '=', 'contact'], ['x_studio_cobranza_o_facturacin', '=', False]]).mapped('id')
                hijosF = hijos.filtered(lambda x: x.type == 'contact').mapped('id')
                final = nietos + hijosF
                res['domain'] = {
                    'localidadContacto': [('id', 'in', final)]
                }
        return res
        
    


    

#EN DESAROLLO
class helpdesk_refacciones(models.Model):
    _name = 'helpdesk.refacciones'
    _description = 'Refacciones modelo temporal'

    #ticketRelacion = fields.Many2one(
    #                                    'helpdesk.ticket', 
    #                                    string = 'Ticket realcionado a diagnostico'
    #                                )
    productos = fields.Many2one(
                                    'product.product',
                                    string = 'Refacciones y accesorios'
                                )
    detalleDeProducto = fields.Text(
                                        string = 'Información de refacción o accesorio',
                                        #compute = '_compute_detalle'
                                    )
    referenciaInterna = fields.Text(
                                        string = 'Referencia interna',
                                        compute = 'agrgarInfoProducto'
                                    )
    nombreProducto = fields.Text(
                                    string = 'Nombre',
                                        compute = 'agrgarInfoProducto'
                                )
    descripcion = fields.Text(
                                string = 'Descripción',
                                        compute = 'agrgarInfoProducto'
                            )
    cantidadAMano = fields.Text(
                                string = 'Cantidad a mano',
                                        compute = 'agrgarInfoProducto'
                            )
    cantidadPedida = fields.Integer(
                                        string = 'Cantidad a pedir'
                                    )
    wizRela = fields.Many2one(
                                'helpdesk.agregar.productos'
    )
    wizRelaVal = fields.Many2one(
                                'helpdesk.confirmar.validar.refacciones'
    )
    ticketRela = fields.Many2one(
                                'helpdesk.ticket'
    )


    @api.depends('productos')
    def agrgarInfoProducto(self):
        for rec in self:
            if rec.productos:
                rec.referenciaInterna = rec.productos.default_code
                rec.nombreProducto = rec.productos.name
                rec.descripcion = rec.productos.description
                rec.cantidadAMano = rec.productos.qty_available
    #@api.depends('productos')
    def _compute_detalle(self):
        for rec in self:
            if rec.productos:
                rec.detalleDeProducto = """
                                            <table class='table table-bordered table-dark text-white'>
                                                <thead >
                                                    <tr>
                                                        <th scope='col'>Categoría del producto</th>
                                                        <th scope='col'>Referencia interna</th>
                                                        <th scope='col'>Nombre</th>
                                                        <th scope='col'>Descripción</th>
                                                        <th scope='col'>Cantidad a mano</th>
                                                        <th scope='col'>Cantidad prevista</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>""" + str(rec.productos.categ_id.name) + """</td>
                                                        <td>""" + str(rec.productos.default_code) + """</td>
                                                        <td>""" + str(rec.productos.name) + """</td>
                                                        <td>""" + str(rec.productos.description) + """</td>
                                                        <td>""" + str(rec.productos.qty_available) + """</td>
                                                        <td>""" + str(rec.productos.virtual_available) + """</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        """

class helpdesk_agregar_productos(models.Model):
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
                                    help = """
                                                Estado en el que se encuentra la solicitud de refacción y/o accesorios.
                                                En caso de que no exista se muestra el mensaje 'No existe un SO'.
                                            """
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
        _logger.info('entro')
        #self.ticket_id.x_studio_productos = [(6, 0, self.productos.ids)]
        lista = [[5,0,0]]
        listaDeCantidades = []
        for refaccion in self.accesorios:
            if refaccion.productos.id:
                vals = {
                    'productos': refaccion.productos.id,
                    'cantidadPedida': refaccion.cantidadPedida
                }
                lista.append( [0, 0, vals] )
                listaDeCantidades.append(refaccion.cantidadPedida)
            """
            lista.append( [0, 0, {
                                    'product_tmpl_id': refaccion.productos.product_tmpl_id.id,
                                    'x_studio_cantidad_pedida': refaccion.cantidadPedida,
                                    'name': refaccion.productos.name,
                                    'categ_id': refaccion.productos.categ_id.id,
                                    'default_code': refaccion.productos.default_code,
                                    'description': refaccion.productos.description,
                                    'qty_available': refaccion.productos.qty_available,
                                    'virtual_available': refaccion.productos.virtual_available

                        }])
            """
        #_logger.info('3312: lista2: ' + str(lista))
        self.ticket_id.write({'accesorios': lista})

        lista = []
        productos_en_wizard = self.mapped('accesorios')
        productos_en_wizard_ids = self.mapped('accesorios.productos.id')
        #_logger.info('productos_en_wizard: ' + str(productos_en_wizard))
        #_logger.info('productos_en_wizard_ids: ' + str(productos_en_wizard_ids))
        prodcutos_en_ticket_ids = self.ticket_id.mapped('accesorios.productos.id')
        #_logger.info('prodcutos_en_ticket_ids: ' + str(prodcutos_en_ticket_ids))
        prodcutos_en_ticket = self.ticket_id.accesorios #self.ticket_id.mapped('x_studio_productos')
        #_logger.info('prodcutos_en_ticket: ' + str(prodcutos_en_ticket))
        indice = 0
        for refaccion in self.accesorios:
            producto_en_wizard = refaccion.productos.id
            #producto_en_ticket = prodcutos_en_ticket[indice]
            for producto_en_ticket in prodcutos_en_ticket:
                if producto_en_wizard == producto_en_ticket.id:
                    vals = {
                            'cantidadPedida': refaccion.cantidadPedida
                    }
                    lista.append( [1, producto_en_wizard, vals] )
                    break
            indice = indice + 1
        #_logger.info('3312: lista actualiza cantidades: ' + str(lista))
        self.ticket_id.write({'accesorios': lista})
        #indice = 0
        #for refaccion in self.ticket_id.x_studio_productos:
        #    refaccion.x_studio_cantidad_pedida = listaDeCantidades[indice]
        #    indice = indice + 1
        self.ticket_id.datos_ticket_2()

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





class helpdesk_crearToner(models.Model):
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

    """
    def contacto_toner_wizard(self):
        wiz = self.env['helpdesk.contacto.toner'].create({
                                                            #'dca': self.dca.ids,
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
                
            #wiz.dca = 
        view = self.env.ref('helpdesk_update.view_helpdesk_contacto_toner')
        return {
            'name': _('Agregar contacto a localidad'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.contacto.toner',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    """
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






class helpdesk_validacion_de_solicitud(models.Model):
    _name = 'helpdesk.validacion.so'
    _description = 'Registro de las validaciónes de solicitudes'
    ticketRelacion = fields.Many2one('helpdesk.ticket', string = 'Ticket realcionado a diagnostico',copied=True)
    fechaDeValidacionSo = fields.Datetime(string = 'Fecha de validación de la solicitud')
    refaccionesValidadas = fields.Text(string = 'Lo que se valido')
    listaRefaccionesValidadas = fields.Text(string = 'Lista de lo que se valido')
    listaIdsRefaccionesValidadas = fields.Text(string = 'Lista de ids de productos que se valido')
    
    

class helpdes_diagnostico(models.Model):
    _name = "helpdesk.diagnostico"
    _description = "Historial de diagnostico"
    ticketRelacion = fields.Many2one('helpdesk.ticket', string = 'Ticket realcionado a diagnostico',copied=True)

    ticketRelacion_refacciones = fields.Many2one('helpdesk.confirmar.validar.refacciones', string = 'Ticket realcionado a diagnostico',copied=True)

    #ticket_techra = fields.Many2one('helpdesk.ticket.techra', string = 'Ticket techra relacionado al diagnostico')
    ticket_techra_text = fields.Text(string = 'Ticket techra texto')


    estadoTicket = fields.Char(string='Estado de ticket',copied=True)
    comentario = fields.Text(string='Diagnostico / comentario',copied=True)
    evidencia = fields.Many2many('ir.attachment', string="Evidencias",copied=True)
    mostrarComentario = fields.Boolean(string = "Mostrar comentario en documento impreso", default = False,copied=True)
    creadoPorSistema = fields.Boolean(string = "Creado por sistema", default = False,copied=True)
    fechaDiagnosticoTechra = fields.Datetime(
                                    string = 'Fecha techra',
                                    store = True,copied=True
                                )
    tipoSolucionTechra = fields.Text(
                                    string = 'Tipo de solución',copied=True
                                )
    tecnicoTechra = fields.Text(
                                    string = 'Tecnico techra',copied=True
                                )
    creado_por_techra = fields.Boolean(string = "Creado por techra", default = False)
    href_diagnostico_ticket_techra = fields.Text(
                                                    string = 'href'
                                    )
    fecha_diagnostico_techra_text = fields.Text(
                                                string = 'Fecha techra text'
                                            )

    def mostrarComentarioFun(self):
        self.mostrarComentario = True
        ticketTemp = self.env['helpdesk.ticket'].search([('id', '=', self.ticketRelacion.id)], limit = 1 )
        if ticketTemp.x_studio_equipo_por_nmero_de_serie:
            wiz = self.env['helpdesk.datos.mesa'].search([('ticket_id', '=', self.ticketRelacion.id)], order = 'create_date desc', limit = 1 )
            seriesDatos = ''
            if not ticketTemp.x_studio_equipo_por_nmero_de_serie_1:
                #caso mesa
                for serie in ticketTemp.x_studio_equipo_por_nmero_de_serie:
                    seriesDatos = seriesDatos + """
                                            <tr>
                                                <td>""" + str(serie.name) + """</td>
                                                <td>""" + str(serie.product_id.display_name) + """</td>
                                                <td>""" + str(serie.x_studio_ultima_ubicacin) + """</td>
                                                <td>""" + str(serie.x_studio_color_bn) + """</td>
                                            </tr>
                                        """

                wiz.seriesText = """
                                        <table class='table table-bordered table-secondary text-black'>
                                            <thead>
                                                <tr>
                                                    <th scope='col'>Número de serie</th>
                                                    <th scope='col'>Producto</th>
                                                    <th scope='col'>Ultima unicación</th>
                                                    <th scope='col'>Color o B/N</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                """ + seriesDatos +"""
                                            </tbody>
                                        </table>
                                    """
            #idExternoToner = 'studio_customization.tiquete_del_servicio_e501a40f-0bd7-4726-b219-50085c31c177'
            #pdf = self.env.ref(idExternoToner).sudo().render_qweb_pdf([self.id])[0]
            #wiz.pdfToner = base64.encodestring(pdf)
            view = self.env.ref('helpdesk_update.view_helpdesk_detalle_mesa')
            return {
                    'name': _('Más información'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'helpdesk.datos.mesa',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }
        else:
            #caso toner
            wiz = self.env['helpdesk.datos.toner'].search([('ticket_id', '=', self.ticketRelacion.id)], order = 'create_date desc', limit = 1 )
            #idExternoToner = 'studio_customization.tiquete_del_servicio_8a770195-f5a2-4b6c-b905-fc0ff46c1258'
            #pdf = self.env.ref(idExternoToner).sudo().render_qweb_pdf([self.id])[0]
            #wiz.pdfToner = base64.encodestring(pdf)
            view = self.env.ref('helpdesk_update.view_helpdesk_detalle_toner')
            return {
                        'name': _('Datos tóner'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'helpdesk.datos.toner',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': self.env.context,
                    }

    def noMostrarComentario(self):
        self.mostrarComentario = False
        ticketTemp = self.env['helpdesk.ticket'].search([('id', '=', self.ticketRelacion.id)], limit = 1 )
        if ticketTemp.x_studio_equipo_por_nmero_de_serie:
            wiz = self.env['helpdesk.datos.mesa'].search([('ticket_id', '=', self.ticketRelacion.id)], order = 'create_date desc', limit = 1 )
            seriesDatos = ''
            if not ticketTemp.x_studio_equipo_por_nmero_de_serie_1:
                #caso mesa
                for serie in ticketTemp.x_studio_equipo_por_nmero_de_serie:
                    seriesDatos = seriesDatos + """
                                            <tr>
                                                <td>""" + str(serie.name) + """</td>
                                                <td>""" + str(serie.product_id.display_name) + """</td>
                                                <td>""" + str(serie.x_studio_ultima_ubicacin) + """</td>
                                                <td>""" + str(serie.x_studio_color_bn) + """</td>
                                            </tr>
                                        """

                wiz.seriesText = """
                                        <table class='table table-bordered table-secondary text-black'>
                                            <thead>
                                                <tr>
                                                    <th scope='col'>Número de serie</th>
                                                    <th scope='col'>Producto</th>
                                                    <th scope='col'>Ultima unicación</th>
                                                    <th scope='col'>Color o B/N</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                """ + seriesDatos +"""
                                            </tbody>
                                        </table>
                                    """
            #idExternoToner = 'studio_customization.tiquete_del_servicio_e501a40f-0bd7-4726-b219-50085c31c177'
            #pdf = self.env.ref(idExternoToner).sudo().render_qweb_pdf([self.id])[0]
            #wiz.pdfToner = base64.encodestring(pdf)
            view = self.env.ref('helpdesk_update.view_helpdesk_detalle_mesa')
            return {
                    'name': _('Más información'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'helpdesk.datos.mesa',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }
        else:
            #caso toner
            wiz = self.env['helpdesk.datos.toner'].search([('ticket_id', '=', self.ticketRelacion.id)], order = 'create_date desc', limit = 1 )
            #idExternoToner = 'studio_customization.tiquete_del_servicio_8a770195-f5a2-4b6c-b905-fc0ff46c1258'
            #pdf = self.env.ref(idExternoToner).sudo().render_qweb_pdf([self.id])[0]
            #wiz.pdfToner = base64.encodestring(pdf)
            view = self.env.ref('helpdesk_update.view_helpdesk_detalle_toner')
            return {
                        'name': _('Datos tóner'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'helpdesk.datos.toner',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': self.env.context,
                    }



class helpdesk_ticket_techra(models.Model):
    _name = "helpdesk.ticket.techra"
    _description = "Historial de tickets de techra"
    esTicketDeTechra = fields.Boolean(
                                        string = 'Es ticket de techra?',
                                        default = False
                                    )
    tipoDeReporteTechra = fields.Text(
                                        string = 'Tipo de reporte techra'
                                    )
    estadoTicketTechra = fields.Text(
                                        string = 'Estado ticket techra'
                                    )
    areaDeAtencionTechra = fields.Text(
                                        string = 'Área de atención techra'
                                    )
    partner_id = fields.Many2one( 
                                    'res.partner',
                                    string = 'Cliente'
                                )
    cliente_text = fields.Text( 
                                string = 'Cliente texto'
                            )
    cliente_clave = fields.Text( 
                                string = 'Clave de cliente'
                            )
    tipo_de_cliente = fields.Text(
                                    string = 'Tipo de cliente'
                                    )
    estatus_de_cobranza = fields.Text(
                                    string = 'Estatus de cobranza'
                                    )
    x_studio_empresas_relacionadas = fields.Many2one( 
                                                        'res.partner',
                                                        string = 'Localidad'
                                                    )
    localidad_text = fields.Text(
                                    string = 'Localidad texto'
                                )
    tipo_de_domicilio = fields.Text(
                                    string = 'Tipo de domicilio'
                                    )
    calle_de_domicilio = fields.Text(
                                    string = 'Calle'
                                    )
    colonia_de_domicilio = fields.Text(
                                    string = 'Colonia'
                                    )
    delegacion_de_domicilio = fields.Text(
                                    string = 'Delegación'
                                    )
    zona_de_domicilio = fields.Text(
                                    string = 'Zona'
                                    )
    no_exterior_de_domicilio = fields.Text(
                                    string = 'No. exterior'
                                    )
    ciudad_de_domicilio = fields.Text(
                                    string = 'Ciudad'
                                    )
    c_p_de_domicilio = fields.Text(
                                    string = 'C.P'
                                    )
    ubicacion_de_domicilio = fields.Text(
                                    string = 'Ubicación'
                                    )
    no_interior_de_domicilio = fields.Text(
                                    string = 'No. exterior'
                                    )
    estado_de_domicilio = fields.Text(
                                    string = 'Estado'
                                    )

    nombreTfsTechra = fields.Text(
                                    string = 'Nombre TFS techra'
                                )
    localidadContacto = fields.Many2one(
                                            'res.partner',
                                            string = 'Localidad contacto'
                                        )
    localidad_contacto_text = fields.Text(
                                            string = 'Localidad contacto texto'
                                        )
    localidad_contacto_telefono = fields.Text(
                                                string = 'Telefono contacto'
                                            )
    localidad_contacto_celular = fields.Text(
                                                string = 'Celular contacto'
                                            )
    localidad_contacto_correo = fields.Text(
                                                string = 'Correo electronico contacto'
                                            )




    contacto_responsable_nombre = fields.Text(
                                                string = 'Nombre contacto responsable'
                                            )
    contacto_responsable_telefono_1 = fields.Text(
                                                string = 'telefono 1 contacto responsable'
                                            )
    contacto_responsable_telefono_2 = fields.Text(
                                                string = 'telefono 2 contacto responsable'
                                            )
    contacto_responsable_extencion_1 = fields.Text(
                                                string = 'extencion 1 contacto responsable'
                                            )
    contacto_responsable_extencion_2 = fields.Text(
                                                string = 'extencion 2 contacto responsable'
                                            )
    contacto_responsable_celular = fields.Text(
                                                string = 'celular contacto responsable'
                                            )
    contacto_responsable_correo = fields.Text(
                                                string = 'Correo electronico contacto responsable'
                                            )


    


    contacto_de_atencion_nombre = fields.Text(
                                                string = 'Nombre contacto de atencion'
                                            )
    contacto_de_atencion_telefono_1 = fields.Text(
                                                string = 'telefono 1 contacto de atencion'
                                            )
    contacto_de_atencion_telefono_2 = fields.Text(
                                                string = 'telefono 2 contacto de atencion'
                                            )
    contacto_de_atencion_extencion_1 = fields.Text(
                                                string = 'extencion 1 contacto de atencion'
                                            )
    contacto_de_atencion_extencion_2 = fields.Text(
                                                string = 'extencion 2 contacto de atencion'
                                            )
    contacto_de_atencion_celular = fields.Text(
                                                string = 'celular contacto de atencion'
                                            )
    contacto_de_atencion_correo = fields.Text(
                                                string = 'Correo electronico contacto de atencion'
                                            )





    x_studio_nmero_de_ticket_cliente = fields.Text(
                                                    string = 'Ticket del cliente',
                                                    )
    x_studio_nmero_ticket_distribuidor_1 = fields.Text(
                                                            string = 'Número de ticket distribuidor',
                                                        )
    x_studio_nmero_de_guia_1 = fields.Text(
                                                string = 'Número de guía'
                                            )
    descripcionDelReporteTechra = fields.Text(
                                                string = 'Descripción del reporte techra'
                                            )
    obsAdicionalesTechra = fields.Text(
                                        string = 'Observaciones adicionales techra'
                                    )
    numTicketDeTechra = fields.Text(
                                        string = 'Número de ticket de techra'
                                    )
    numeroDeSerieTechra = fields.Text(
                                        string = 'Número de serie techra'
                                    )
    robot = fields.Text(
                                        string = 'Robot'
                                    )
    """
    diagnosticos = fields.One2many(
                                        'helpdesk.diagnostico', 
                                        'ticket_techra', 
                                        string = 'Diagnostico', 
                                        track_visibility = 'onchange'
                                    )
    """
    es_repetido = fields.Boolean(
                                    string = 'Es repetido',
                                    default = False
                                )
    active = fields.Boolean(
                                    string = 'Activo',
                                    default = True
                                )
    """
    series = fields.One2many(
                                'dcas.dcas', 
                                'ticket_techra', 
                                string = 'Series en dca', 
                                track_visibility = 'onchange'
                            )
    """
    creado_el = fields.Text(
        string = 'Fecha'
    )
    ultima_nota = fields.Text(
        string = 'Ultima nota'
    )
    fecha_ultima_nota = fields.Text(
        string = 'Fecha nota'
    )

    def identifica_repetidos(self):
        dominio_busqueda_ticket = [('numTicketDeTechra', '=', self.numTicketDeTechra), ('id', '!=', str(self.id)), ('es_repetido', '=', False)]
        serie_id = self.env['helpdesk.ticket.techra'].search(dominio_busqueda_ticket, limit = 1)
        if serie_id:
            if not serie_id.es_repetido:
                vals = {
                    'es_repetido': True
                }
                serie_id.write(vals)
                return serie_id.id
        return -1


    def crea_relacion_dca(self):
        regreso = {}
        dcas_existentes = []

        dominio_busqueda_dca = [('x_studio_tickett', '=', self.numTicketDeTechra), ('ultimaCargaContadoresMesa', '=', True) ]
        dcas_existentes = self.env['dcas.dcas'].search(dominio_busqueda_dca)

        if not dcas_existentes:
            dominio_busqueda_dca = [('x_studio_tickett', '=', self.numTicketDeTechra)]
            dcas_existentes = self.env['dcas.dcas'].search(dominio_busqueda_dca)

        if dcas_existentes:
            for dca in dcas_existentes:
                if not dca.ticket_techra:
                    vals = {
                        'ticket_techra': self.id,
                        'ticket_techra_texto': self.numTicketDeTechra
                    }
                    dca.write(vals)
                    regreso['mensaje'] = 'dca existe'
                    regreso['dca_id'] = dca.id
            return regreso

        series_text = self.numeroDeSerieTechra.replace("[", "").replace("]", "").replace(" ", "")
        lista_series = []
        if "," in series_text:
            lista_series = series_text.split(",")
        else:
            lista_series.append(series_text)

        #_logger.info('Lista de series: ' + str(lista_series))
        for serie in lista_series:
            dominio_busqueda_serie = [('name', '=', serie)]
            serie_id = self.env['stock.production.lot'].search(dominio_busqueda_serie)
            vals = {}
            if serie_id:
                if self.tipoDeReporteTechra == 'Toner':
                    vals['fuente'] = 'helpdesk.ticket'
                else:
                    vals['fuente'] = 'stock.production.lot'
                vals['serie'] = serie_id.id
                vals['ticket_techra'] = self.id
                vals['ticket_techra_texto'] = self.numTicketDeTechra
                vals['creado_por_tickets_techra'] = True

                vals['esContadorDeTechra'] = False
                vals['reinicioDeContador'] = False
                vals['respaldo'] = False
                vals['usb'] = False
                vals['ultimaCargaContadoresMesa'] = False
                vals['x_studio_capturar'] = False
                vals['x_studio_check_temporal'] = False


            else:
                if self.tipoDeReporteTechra == 'Toner':
                    vals['fuente'] = 'helpdesk.ticket'
                else:
                    vals['fuente'] = 'stock.production.lot'
                #vals['serie'] = serie_id
                vals['ticket_techra'] = self.id
                vals['ticket_techra_texto'] = self.numTicketDeTechra
                vals['creado_por_tickets_techra'] = True

                vals['esContadorDeTechra'] = False
                vals['reinicioDeContador'] = False
                vals['respaldo'] = False
                vals['usb'] = False
                vals['ultimaCargaContadoresMesa'] = False
                vals['x_studio_capturar'] = False
                vals['x_studio_check_temporal'] = False
            dca = self.env['dcas.dcas'].create(vals)
            regreso['mensaje'] = 'dca creado'
            regreso['dca_id'] = dca.id
        return regreso




"""
class helpdesk_lines(models.Model):
    _name="helpdesk.lines"
    _description = "Ticket Order"
    producto=fields.Many2one('product.product')
    cantidad=fields.Integer(string='Cantidad')
    serie=fields.Many2one('stock.production.lot')
    ticket=fields.Many2one('helpdesk.ticket',string='Order Reference')
    contadorAnterior=fields.Many2one('dcas.dcas',string='Anterior',compute='ultimoContador')
    contadorColor=fields.Integer(string='Contador Color')
    contadorNegro=fields.Integer(string='Contador Monocromatico')
    usuarioCaptura=fields.Char(string='Capturado por:') 
    current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    
    
    
    aA=fields.Integer(related='contadorAnterior.porcentajeAmarillo',string='Porcentaje A Amarillo')
    a=fields.Integer(string=' Porcentaje Amarillo')
    c=fields.Integer(string='Porcentaje Cian')
    cA=fields.Integer(related='contadorAnterior.porcentajeCian',string='Porcentaje A Cian')
    nA=fields.Integer(related='contadorAnterior.porcentajeNegro',string='Porcentaje A Negro')
    n=fields.Integer(string='Porcentaje Negro')
    m=fields.Integer(string='Porcentaje Magenta')
    mA=fields.Integer(related='contadorAnterior.porcentajeMagenta',string='Porcentaje A Magenta')
    
    
    
    contadorAnteriorMono=fields.Integer(related='contadorAnterior.contadorMono',string='Anterior Monocromatico')
    contadorAnteriorColor=fields.Integer(related='contadorAnterior.contadorColor',string='Anterior Color')
    impresiones=fields.Integer(related='serie.x_studio_impresiones',string='Impresiones B/N')
    impresionesColor=fields.Integer(related='serie.x_studio_impresiones_color',string='Impresiones Color')
    colorToner=fields.Char(related='serie.x_studio_field_A6PR9',string='Color Toner')
    area=fields.Integer()
    

    @api.depends('serie')
    def ultimoContador(self):
        for record in self:
            j=0
            for dc in record.serie.dca:
                if(j==0):
                    record['contadorAnterior']=dc.id
                    j=j+1
                    
    @api.onchange('serie')
    def productos_filtro(self):
        res = {}
        d=[]
        for p in self.serie.product_id.x_studio_toner_compatible:
            d.append(p.id)
        if self.serie !='False':   
            idf = self.area
            if idf == 8 or idf == 13 :          
               res['domain']={'producto':[('categ_id', '=', 5),('id','in',d)]}
            if idf == 9:
               res['domain']={'producto':[('categ_id', '=', 7),('id','in',d)]}
            if idf != 9 and idf != 8:
               res['domain']={'producto':[('id','in',d)]}
        return res
"""



#class helpdesk_historico_componentes(models.Model):
    #_name = 'helpdesk.historico.componentes'
#    _inherit = 'x.studio.historico.de.componentes'


#    ticket_relacion_refacciones = fields.Many2one('helpdesk.confirmar.validar.refacciones', string = 'Ticket realcionado a refaccion')



class helpdesk_confirmar_validar_refacciones(models.Model):
    _name = 'helpdesk.confirmar.validar.refacciones'
    _description = 'helpdesk valida y confirma proceso de refacciones.'
    
    ticket_id = fields.Many2one(
                                    "helpdesk.ticket",
                                    string = 'Ticket'
                                )

    #productos = fields.Many2many(
    #                                'product.product', 
    #                                string = "Productos"
    #                            )
    accesorios = fields.One2many('helpdesk.refacciones', 'wizRelaVal', string = 'Accesorios')

    """
    EN DESARROLLO
    productosDos = fields.One2many(
                                    'helpdesk.refacciones',
                                    'ticketRelacion',
                                    string = "Refacciones y accesorios"
                                )
    """
    activar_compatibilidad = fields.Boolean(
                                                string = 'Activar compatibilidad',
                                                default = False
                                            )
    check = fields.Boolean(
                                string = 'Mostrar en reporte',
                                default = False
                            )
    diagnostico_id = fields.One2many(
                                        'helpdesk.diagnostico',
                                        'ticketRelacion_refacciones',
                                        string = 'Diagnostico',
                                        #compute = '_compute_diagnosticos'
                                    )
    estado = fields.Char(
                            'Estado previo a cerrar el ticket',
                            #compute = "_compute_estadoTicket"
                        )
    comentario = fields.Text(
                                string = 'Comentario'
                            )
    evidencia = fields.Many2many(
                                    'ir.attachment',
                                    string = "Evidencias"
                                )
    """
    historicoTickets = fields.One2many(
                                        'dcas.dcas', 
                                        'serie', 
                                        string = 'Historico de tickets', 
                                        compute='_compute_historico_tickets'
                                        )
    lecturas = fields.One2many(
                                'dcas.dcas', 
                                'serie', 
                                string = 'Lecturas', 
                                compute='_compute_lecturas'
                                )
    toner = fields.One2many(
                                'dcas.dcas', 
                                'serie', 
                                string = 'Tóner', 
                                compute='_compute_toner'
                            )
    """
    #historicoDeComponentes = fields.One2many(
     #                                           'x_studio_historico_de_componentes',
       #                                         'x_relacion_refacciones', 
            #                                    string = 'Historico de Componentes',
                                                #domain = "[ '|', ('x_ultimaCargaRefacciones', '=', True), ('x_studio_modelo', 'like', 'Refacción y/o accesorio:') ]",
                                                #compute='_compute_historico_de_componentes'
          #                                  )
    """
    movimientos = fields.One2many( 
                                    'stock.move.line', 
                                    'lot_id', 
                                    string = 'Movimientos', 
                                    compute='_compute_movimientos'
                                )
    """
    serie = fields.Text(
                            string = "Serie", 
                            #compute = '_compute_serie_nombre'
                        )

    contadoresAnterioresText = fields.Text(
                                                string = 'Contadores anteriores',
                                                store = True
                                            )
    estadoSolicitud = fields.Text(
                                    string = 'Estado de la solicitud',
                                    #compute = '_compute_estado_solicitud'
                                )
    solicitud = fields.Many2one(
                                    'sale.order',
                                    string = 'Solicitud',
                                    #compute = '_compute_solicitud'
                                )
    mensajesAlerta = fields.Text(
                                    string = 'Mensjae de alerta'
                                )
    @api.depends('accesorios.cantidadPedida')
    def cambiarMensajePorProductos(self):
        if self.accesorios:
            refaccionesEnCero = ''
            for refaccion in self.accesorios:
                if not refaccion.cantidadPedida:
                    refaccionesEnCero = refaccionesEnCero + """
                                                                <tr>
                                                                    <td>""" + str(refaccion.productos.categ_id.name) + """</td>
                                                                    <td>""" + str(refaccion.productos.display_name) + """</td>
                                                                    <td>""" + str(refaccion.cantidadPedida) + """</td>
                                                                </tr>
                                                            """
            if refaccionesEnCero != '':
                self.mensajesAlerta = """
                                        <div class='alert alert-info' role='alert'>
                                            <h4 class="alert-heading">Validación de refaciones y/o accesorios en cero !!!</h4>

                                            <p>Se validaran refacciones y/o accesorios con cantidad en cero. Los equipos son los siguientes: </p>
                                            <br/>
                                            <div class='row'>
                                                <table class='table table-bordered table-warning text-black'>
                                                    <thead >
                                                        <tr>
                                                            <th scope='col'>Categoría del producto</th>
                                                            <th scope='col'>Refacción y/o accesorio</th>
                                                            <th scope='col'>Cantidad a pedir</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        """ + refaccionesEnCero + """
                                                    </tbody>
                                                </table>
                                            </div>    
                                        </div>      
                                    """
            else:
                self.mensajesAlerta = ''

    """
    def _compute_solicitud(self):
        if self.ticket_id.x_studio_field_nO7Xg:
            self.solicitud = self.ticket_id.x_studio_field_nO7Xg
        
    def _compute_estado_solicitud(self):
        if self.ticket_id.x_studio_field_nO7Xg:
            if self.ticket_id.x_studio_field_nO7Xg.state == 'sale':
                self.estadoSolicitud = 'Solicitud validada'
            else:
                self.estadoSolicitud = 'Solicitud no validada'
        else:
            self.estadoSolicitud = 'No hay solicitud'
    

    def _compute_estadoTicket(self):
        self.estado = self.ticket_id.stage_id.name
    
    def _compute_diagnosticos(self):
        self.diagnostico_id = self.ticket_id.diagnosticos.ids
    

    
    
    """

    """
    def _compute_historico_tickets(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.historicoTickets = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_field_Yxv2m.ids

    def _compute_lecturas(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.lecturas = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_field_PYss4.ids

    def _compute_toner(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.toner = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_toner_1.ids
    

    def _compute_historico_de_componentes(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            componentes = self.env['x_studio_historico_de_componentes'].search([('x_studio_modelo', '!=', False)])
            #_logger.info('**** componentes: ' + str(componentes))
            #self.historicoDeComponentes = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_histrico_de_componentes.ids
            componentes = componentes.filtered(lambda componente:  componente.x_studio_field_MH4DO.name == str(self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name) and (componente.x_ultimaCargaRefacciones == True or 'Refacción y/o accesorio:' in componente.x_studio_modelo) )
            self.historicoDeComponentes = componentes.ids
    """

    """
    def _compute_movimientos(self):
        if self.ticket_id.x_studio_equipo_por_nmero_de_serie:
            self.movimientos = self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].x_studio_move_line.ids
    """
    @api.onchange('activar_compatibilidad')
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

    def validacionSolicitud(self):
        if self.productos:
            if self.ticket_id.x_studio_field_nO7Xg and self.ticket_id.x_studio_field_nO7Xg.state != 'sale':
                self.ticket_id.x_studio_field_nO7Xg.action_confirm()
            
            if self.ticket_id.x_studio_field_nO7Xg.state == 'sale':
                mensajeTitulo = 'Validación de refacción!!!'
                mensajeCuerpo = 'Se valido la solicitud ' + str(self.ticket_id.x_studio_field_nO7Xg.name) + ' para el ticket ' + str(self.ticket_id.id) + '.'
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
            else:
                mensajeTitulo = 'No se valido!!!'
                mensajeCuerpo = 'No se valido la solicitud ' + str(self.ticket_id.x_studio_field_nO7Xg.name) + ' para el ticket ' + str(self.ticket_id.id) + '.'
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


    def confirmarYValidarRefacciones(self):
        if self.ticket_id.stage_id.id == 3 or self.ticket_id.stage_id.id == 18 or self.ticket_id.stage_id.id == 4:
            mensajeTitulo = 'No se puede validar la solicitud de refacción porque se encuentra en el estado ' + str(self.ticket_id.stage_id.name)
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

        #self.ticket_id.x_studio_productos = [(6, 0, self.accesorios.ids)]
        #if self.accesorios:
        #    self.ticket_id.x_studio_productos = [(6, 0, self.accesorios.ids)]


        _logger.info('*********************accesorios antes de cambiarlos**************')
        for accesorio in self.ticket_id.accesorios:
            _logger.info('id: ' + str(accesorio.id) + 'producto: ' + str(accesorio.productos.display_name) + ' cantidad pedida: ' + str(accesorio.cantidadPedida))

        """
        lista = [(5, 0, 0)]
        for refaccion in self.accesorios:
            vals = {
                'productos': refaccion.productos.id,
                'cantidadPedida': refaccion.cantidadPedida
            }
            lista.append( [0, 0, vals] )
        self.ticket_id.write({'accesorios': lista})
        """


        
        #lista = [[5,0,0]]
        lista = []
        listaDeCantidades = []

        refacciones_en_ticket = self.ticket_id.mapped('accesorios.productos.id')

        for refaccion in self.accesorios:
            if not refaccion.productos.id in refacciones_en_ticket:
                vals = {
                    'productos': refaccion.productos.id,
                    'cantidadPedida': refaccion.cantidadPedida
                }
                lista.append( [0, 0, vals] )
                listaDeCantidades.append(refaccion.cantidadPedida)
        self.ticket_id.write({'accesorios': lista})
        
        lista = []
        productos_en_wizard = self.mapped('accesorios')
        productos_en_wizard_ids = self.mapped('accesorios.productos.id')
        prodcutos_en_ticket_ids = self.ticket_id.mapped('accesorios.id')
        prodcutos_en_ticket = self.ticket_id.accesorios #self.ticket_id.mapped('x_studio_productos')
        indice = 0
        for refaccion in self.accesorios:
            producto_en_wizard = refaccion.productos.id
            for producto_en_ticket in prodcutos_en_ticket:
                if producto_en_wizard == producto_en_ticket.productos.id:
                    id_linea_wizard = producto_en_ticket.id
                    vals = {
                            'cantidadPedida': refaccion.cantidadPedida
                    }
                    lista.append( [1, id_linea_wizard, vals] )
                    break
            indice = indice + 1
        self.ticket_id.write({'accesorios': lista})



        
        _logger.info('*********************accesorios despues de cambiarlos**************')
        for accesorio in self.ticket_id.accesorios:
            _logger.info('id: ' + str(accesorio.id) + 'producto: ' + str(accesorio.productos.display_name) + ' cantidad pedida: ' + str(accesorio.cantidadPedida))
        

        for refaccion in self.ticket_id.accesorios:
            if not refaccion.productos:
                refaccion.unlink()


        _logger.info('*********************accesorios despues de cambiarlos**************')
        for accesorio in self.ticket_id.accesorios:
            _logger.info('id: ' + str(accesorio.id) + 'producto: ' + str(accesorio.productos.display_name) + ' cantidad pedida: ' + str(accesorio.cantidadPedida))



        """
        Funcionalidad que permite no validar las mismas refacciones y/o accesorios. 
        Funcional pero falta probar con más casos.
        """
        """
        procedeAPedirse = False
        listaDeRefaccionesValidadas = []
        if self.ticket_id.validacionesRefaccion:
            for validacion in self.ticket_id.validacionesRefaccion:
                listaDeRefaccionesValidadas = listaDeRefaccionesValidadas + ast.literal_eval(validacion.listaIdsRefaccionesValidadas)
        listaDeRefaccionesValidadas = list(set(listaDeRefaccionesValidadas))
        _logger.info('listaDeRefaccionesValidadas: ' + str(listaDeRefaccionesValidadas))
        _logger.info('self.ticket_id.x_studio_productos.ids' + str(self.ticket_id.x_studio_productos.ids) )
        for refaccion in self.ticket_id.x_studio_productos:
            if not refaccion.product_variant_id.id in listaDeRefaccionesValidadas:
                procedeAPedirse = True
            
        if not listaDeRefaccionesValidadas:
            procedeAPedirse = True

        if procedeAPedirse:
        """ 

        mensajeCuerpo = """ """

        sale_order = self.mapped('ticket_id.x_studio_field_nO7Xg')

        if sale_order:
            _logger.info('3312: inicio actualización refacciones sobre la misma so(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
            mensajeCantidadesEditadas = '\nSe editaron las cantidades de las siguientes refacciones y/o accesorios: '
            mensajeRefaccionesNuevas = '\nSe añadieron las siguientes refacciones y/o accesorios: '

            ticket_id_wizard = self.mapped('ticket_id.id')
            serie_en_ticket = self.mapped('ticket_id.x_studio_equipo_por_nmero_de_serie')
            refacciones_en_wizard = self.mapped('accesorios')
            refacciones_en_solicitud = self.mapped('ticket_id.x_studio_field_nO7Xg.order_line')
            seActualizoUnaCantidad = False
            se_agregaron_refacciones = False

            listaIdValidadas = []
            filasRefacciones = """ """

            refaccionesActualizadasCantidad = []
            refaccionesNuevas = []

            refaccion_no_presente = []
            refaccion_presente = []

            lista_productos_en_solicitud = []
            for refaccion in refacciones_en_solicitud:
                lista_productos_en_solicitud.append(refaccion.product_id.id)

            for refaccion in refacciones_en_wizard:
                if not refaccion.productos.id in lista_productos_en_solicitud:
                    refaccion_no_presente.append(refaccion)
                else:
                    vals = {
                        'refaccion_en_wizard': refaccion,
                        'refaccion_en_solicitud': refacciones_en_solicitud.filtered(lambda x: x.product_id.id == refaccion.productos.id)
                    }
                    refaccion_presente.append(vals)

            _logger.info('refaccion_no_presente: ' + str(refaccion_no_presente) + ' refaccion_presente: ' + str(refaccion_presente))

            #for refaccion in refacciones_en_solicitud:
            #    refaccion_no_presente = refacciones_en_wizard.filtered(lambda x: x.productos.id != refaccion.product_id.id)
            #    refaccion_presente = refacciones_en_wizard.filtered(lambda x: x.productos.id == refaccion.product_id.id)


            if refaccion_no_presente:
                mensajeCuerpo = 'Refaccione(s) y/o accesorio(s) agregados a la Solicitud ' + str(self.ticket_id.x_studio_field_nO7Xg.name) +'.\n\nSe agregaron las refacciones y/o accesorios: '
                for refac in refaccion_no_presente:
                    refaccion_no_presente_cantidad = refac.mapped('cantidadPedida')
                    _logger.info('Refaccion no presente en so')
                    datosr = {
                                'order_id': sale_order[0].id,
                                'product_id': refac.productos.id,
                                'product_uom_qty': refaccion_no_presente_cantidad[0],
                                'x_studio_field_9nQhR': serie_en_ticket[0].id,
                                'price_unit': 0
                            }
                    line = self.env['sale.order.line'].create(datosr)
                    _logger.info('line: ' + str(line))
                    mensajeRefaccionesNuevas = mensajeRefaccionesNuevas + '\nRefacción y/o accesorio: ' + str(refac.productos.display_name) + ', cantidad: ' + str(refaccion_no_presente_cantidad[0])
                    mensajeCuerpo = mensajeCuerpo + str(refac.productos.name) + ', '
                    se_agregaron_refacciones = True

                    fuenteDca = 'stock.production.lot'



                    dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
                    ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
                    dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
                    ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
                    _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

                    dcaObj = False

                    if ultimo_contador_techra and ultimo_contador_odoo:
                        if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                            dcaObj = ultimo_contador_techra
                        else:
                            dcaObj = ultimo_contador_odoo
                    elif ultimo_contador_techra and not ultimo_contador_odoo:
                        dcaObj = ultimo_contador_techra
                    elif ultimo_contador_odoo and not ultimo_contador_techra:
                        dcaObj = ultimo_contador_odoo
                    else:
                        dcaObj = False



                    #if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                    #    dcaObj = ultimo_contador_techra
                    #else:
                    #    dcaObj = ultimo_contador_odoo


                    #forma odoo
                    # = self.env['dcas.dcas'].search([('x_studio_tickett', '=', ticket_id_wizard[0]),('fuente', '=', fuenteDca)], order = 'create_date desc', limit = 1)
                    #forma techra
                    #if not dcaObj:
                    #    dcaObj = self.env['dcas.dcas'].search([('serie', '=', serie_en_ticket[0].name),('fuente', '=', fuenteDca)], order = 'x_studio_fecha desc', limit = 1)
                    _logger.info('aaaaaaaaaaa dcaObj: ' + str(dcaObj))

                    refaccionesTextTemp = 'Refacción y/o accesorio: ' + str(refac.productos.display_name) + '. Descripción: ' + str(refac.productos.description) + '.\n'
                    refaccionesNuevas.append(refac)
                    if dcaObj:
                        _logger.info('inicio: Se esta creando el historico de componente con dcaObj existente')
                        self.env['x_studio_historico_de_componentes'].create({
                                                                                'x_studio_cantidad': refaccion_no_presente_cantidad[0],
                                                                                'x_studio_field_MH4DO': serie_en_ticket[0].id,
                                                                                'x_studio_ticket': str(ticket_id_wizard[0]),
                                                                                'x_studio_contador_color': dcaObj.contadorColor,
                                                                                'x_studio_fecha_de_entrega': datetime.datetime.now(),
                                                                                'x_studio_modelo': refaccionesTextTemp,
                                                                                'x_studio_contador_bn': dcaObj.contadorMono
                                                                            })
                        _logger.info('fin: Se esta creando el historico de componente con dcaObj existente')
                    else:
                        _logger.info('inicio: Se esta creando el historico de componente')
                        self.env['x_studio_historico_de_componentes'].create({
                                                                                'x_studio_cantidad': refaccion_no_presente_cantidad,
                                                                                'x_studio_field_MH4DO': serie_en_ticket[0].id,
                                                                                'x_studio_ticket': str(ticket_id_wizard[0]),
                                                                                'x_studio_fecha_de_entrega': datetime.datetime.now(),
                                                                                'x_studio_modelo': refaccionesTextTemp
                                                                            })
                        _logger.info('fin: Se esta creando el historico de componente')

                    filasRefacciones = filasRefacciones + """
                                                                <tr>
                                                                    <td>""" + str(refac.productos.categ_id.name) + """</td>
                                                                    <td>""" + str(refac.productos.default_code) + """</td>
                                                                    <td>""" + str(refac.productos.name) + """</td>
                                                                    <td>""" + str(refaccion_no_presente_cantidad) + """</td>
                                                                </tr>
                                                            """
                    listaIdValidadas.append(refac.productos.id)


            if refaccion_presente:
                for refac in refaccion_presente:
                    _logger.info('Refaccion presente en so')
                    refaccion_presente_cantidad = refac['refaccion_en_wizard'].mapped('cantidadPedida')
                    if int(refac['refaccion_en_solicitud'].product_uom_qty) != int(refaccion_presente_cantidad[0]) and refaccion_presente_cantidad[0] != 0:
                        refac['refaccion_en_solicitud'].write({
                            'product_uom_qty': refaccion_presente_cantidad[0]
                        })
                        seActualizoUnaCantidad = True
                        mensajeCantidadesEditadas = mensajeCantidadesEditadas + '\nRefacción y/o accesorio: ' + str(refac['refaccion_en_wizard'].productos.display_name) + ', cantidad: ' + str(refaccion_presente_cantidad[0])

                        filasRefacciones = filasRefacciones + """
                                                                <tr>
                                                                    <td>""" + str(refac['refaccion_en_wizard'].productos.categ_id.name) + """</td>
                                                                    <td>""" + str(refac['refaccion_en_wizard'].productos.default_code) + """</td>
                                                                    <td>""" + str(refac['refaccion_en_wizard'].productos.name) + """</td>
                                                                    <td>""" + str(refaccion_presente_cantidad[0]) + """</td>
                                                                </tr>
                                                            """
                        listaIdValidadas.append(refac['refaccion_en_wizard'].productos.id)

                        refaccionesActualizadasCantidad.append(refac['refaccion_en_wizard'])
            
            tablaRefacciones = """
                                    <table class='table table-bordered table-dark text-white'>
                                        <thead >
                                            <tr>
                                                <th scope='col'>Categoría del producto</th>
                                                <th scope='col'>Referencia interna</th>
                                                <th scope='col'>Nombre</th>
                                                <th scope='col'>Cantidad validada</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            """ + filasRefacciones + """
                                        </tbody>
                                    </table>
                                """
            idValidacion = self.env['helpdesk.validacion.so'].create({
                'ticketRelacion': ticket_id_wizard[0],
                'fechaDeValidacionSo': datetime.datetime.now(),
                'refaccionesValidadas': tablaRefacciones,
                'listaRefaccionesValidadas': str(refaccionesActualizadasCantidad + refaccionesNuevas),
                'listaIdsRefaccionesValidadas': str(list(set(listaIdValidadas)))
            })
            self.ticket_id.write({'validacionesRefaccion': [(4, 0, idValidacion)] })
            self.ticket_id.write({'ticketValidadoElDia': datetime.datetime.now() })
            
            comentarioGenerico = 'Solicitud de refacción autorizada por ' + str(self.env.user.name) + '.\nEl día ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S")) + '.\n\n'
            if seActualizoUnaCantidad:
                comentarioGenerico = comentarioGenerico + mensajeCantidadesEditadas
            if se_agregaron_refacciones:
                comentarioGenerico = comentarioGenerico + mensajeRefaccionesNuevas
            if self.comentario:
                comentarioGenerico = comentarioGenerico + str(self.comentario)
            else:
                comentarioGenerico = comentarioGenerico
            self.ticket_id.write({
                                    'stage_id': 102
                                })
            self.env['helpdesk.diagnostico'].create({
                                                        'ticketRelacion': ticket_id_wizard[0],
                                                        'comentario': comentarioGenerico,
                                                        'estadoTicket': self.ticket_id.stage_id.name,
                                                        'evidencia': [(6,0,self.evidencia.ids)],
                                                        'mostrarComentario': self.check,
                                                        'creadoPorSistema': False
                                                    })
            self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
            self.ticket_id.datos_ticket_2()
            _logger.info('3312: fin actualización refacciones sobre la misma so(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
            











        else:
            _logger.info('3312: inicio confirmarYValidarRefacciones(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
            respuesta = 'sin respuesta.'
            respuesta = self.ticket_id.crear_y_validar_solicitud_refaccion()
            _logger.info('3312: fin confirmarYValidarRefacciones(): ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S") ))
            _logger.info('3312: respuesta de crear_y_validar_solicitud_refaccion: ' + str(respuesta))
            if respuesta == 'sin respuesta':
                mensajeTitulo = 'Error'
                mensajeCuerpo = 'Algo salio mal'
            elif respuesta == 'Sin refacciones y/o accesorios':
                mensajeTitulo = 'Error'
                mensajeCuerpo = 'El ticket no tiene refacciones y/o accesorios.'
            elif respuesta == 'Solicitud existente.':
                mensajeTitulo = 'Error'
                mensajeCuerpo = 'El ticket no tiene refacciones y/o accesorios.'
            elif respuesta == 'Solicitud ya generada y validada':
                mensajeTitulo = 'Error'
                mensajeCuerpo = 'Existe una solicitud ya generada y validada.'
            elif respuesta == 'OK':
                refaccionesNuevas = []
                listaIdValidadas = []
                filasRefacciones = """ """
                #creando x_studio_historico_de_componentes
                fuenteDca = 'stock.production.lot'


                dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
                ultimo_contador_odoo = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'create_date desc', limit = 1)
                dominio_ultimo_contador = [('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id), ('x_studio_robot', '!=', False), ('x_studio_fecha', '!=', False), ('fuente', '!=', 'dcas.dcas'), ('creado_por_tickets_techra', '!=', True)]
                ultimo_contador_techra = self.env['dcas.dcas'].search(dominio_ultimo_contador, order = 'x_studio_fecha desc', limit = 1)
                _logger.info('ultimo_contador_techra: ' + str(ultimo_contador_techra.x_studio_fecha) + ' ultimo_contador_odoo: ' + str(ultimo_contador_odoo.create_date))

                dcaObj = False

                if ultimo_contador_techra and ultimo_contador_odoo:
                    if ultimo_contador_techra.x_studio_fecha > ultimo_contador_odoo.create_date:
                        dcaObj = ultimo_contador_techra
                    else:
                        dcaObj = ultimo_contador_odoo
                elif ultimo_contador_techra and not ultimo_contador_odoo:
                    dcaObj = ultimo_contador_techra
                elif ultimo_contador_odoo and not ultimo_contador_techra:
                    dcaObj = ultimo_contador_odoo
                else:
                    dcaObj = False


                #forma odoo
                #dcaObj = self.env['dcas.dcas'].search([('x_studio_tickett', '=', self.ticket_id.id),('fuente', '=', fuenteDca)], order = 'create_date desc', limit = 1)
                #forma techra
                #if not dcaObj:
                #    dcaObj = self.env['dcas.dcas'].search([('serie', '=', self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].name),('fuente', '=', fuenteDca)], order = 'x_studio_fecha desc', limit = 1)
                _logger.info('aaaaaaaaaaa dcaObj: ' + str(dcaObj))
                if dcaObj:
                    refaccionesTextTemp = ''
                    for refaccion in self.accesorios:
                        refaccionesTextTemp = 'Refacción y/o accesorio: ' + str(refaccion.productos.display_name) + '. Descripción: ' + str(refaccion.descripcion) + '.'
                        self.env['x_studio_historico_de_componentes'].create({
                                                                                'x_studio_cantidad': refaccion.cantidadPedida,
                                                                                'x_studio_field_MH4DO': self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id,
                                                                                'x_studio_ticket': str(self.ticket_id.id),
                                                                                'x_studio_contador_color': dcaObj.contadorColor,
                                                                                'x_studio_fecha_de_entrega': datetime.datetime.now(),
                                                                                'x_studio_modelo': refaccionesTextTemp,
                                                                                'x_studio_contador_bn': dcaObj.contadorMono
                                                                            })
                        refaccionesNuevas.append(refaccion)
                        listaIdValidadas.append(refaccion.productos.id)
                        filasRefacciones = filasRefacciones + """
                                                                <tr>
                                                                    <td>""" + str(refaccion.productos.categ_id.name) + """</td>
                                                                    <td>""" + str(refaccion.productos.default_code) + """</td>
                                                                    <td>""" + str(refaccion.productos.name) + """</td>
                                                                    <td>""" + str(refaccion.cantidadPedida) + """</td>
                                                                </tr>
                                                            """
                else:
                    _logger.info('inicio: Se esta creando el historico de componente')
                    refaccionesTextTemp = ''
                    for refaccion in self.accesorios:
                        refaccionesTextTemp = 'Refacción y/o accesorio: ' + str(refaccion.productos.display_name) + '. Descripción: ' + str(refaccion.descripcion) + '.'
                        self.env['x_studio_historico_de_componentes'].create({
                                                                            'x_studio_cantidad': refaccion.cantidadPedida,
                                                                            'x_studio_field_MH4DO': self.ticket_id.x_studio_equipo_por_nmero_de_serie[0].id,
                                                                            'x_studio_ticket': str(self.ticket_id.id),
                                                                            'x_studio_fecha_de_entrega': datetime.datetime.now(),
                                                                            'x_studio_modelo': refaccionesTextTemp
                                                                        })
                        refaccionesNuevas.append(refaccion)
                        listaIdValidadas.append(refaccion.productos.id)
                        filasRefacciones = filasRefacciones + """
                                                                <tr>
                                                                    <td>""" + str(refaccion.productos.categ_id.name) + """</td>
                                                                    <td>""" + str(refaccion.productos.default_code) + """</td>
                                                                    <td>""" + str(refaccion.productos.name) + """</td>
                                                                    <td>""" + str(refaccion.cantidadPedida) + """</td>
                                                                </tr>
                                                            """
                tablaRefacciones = """
                                            <table class='table table-bordered table-dark text-white'>
                                                <thead >
                                                    <tr>
                                                        <th scope='col'>Categoría del producto</th>
                                                        <th scope='col'>Referencia interna</th>
                                                        <th scope='col'>Nombre</th>
                                                        <th scope='col'>Cantidad validada</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    """ + filasRefacciones + """
                                                </tbody>
                                            </table>
                                        """
                mensjaeValidados = 'Se validaron los productos '
                for refaccion in self.accesorios:
                    mensjaeValidados = mensjaeValidados + str(refaccion.productos.display_name) + ', cantidad validada: ' + str(refaccion.cantidadPedida) + '; '
                mensajeTitulo = 'Creación y validación de refacción!!!'
                mensajeCuerpo = 'Se creo y valido la solicitud ' + str(self.ticket_id.x_studio_field_nO7Xg.name) + ' para el ticket ' + str(self.ticket_id.id) + '.'
                comentarioGenerico = 'Solicitud de refacción autorizada por ' + str(self.env.user.name) + '.\nEl día ' + str(datetime.datetime.now(pytz.timezone('America/Mexico_City')).strftime("%d/%m/%Y %H:%M:%S")) + '.\n\n'
                if self.comentario:
                    comentarioGenerico = comentarioGenerico + mensjaeValidados + '\n' + str(self.comentario)
                else:
                    comentarioGenerico = comentarioGenerico + mensjaeValidados
                idValidacion = self.env['helpdesk.validacion.so'].create({
                                                                            'ticketRelacion': self.ticket_id.id,
                                                                            'fechaDeValidacionSo': datetime.datetime.now(),
                                                                            'refaccionesValidadas': tablaRefacciones,
                                                                            'listaRefaccionesValidadas': str(refaccionesNuevas),
                                                                            'listaIdsRefaccionesValidadas': str(listaIdValidadas)
                                                                          })
                self.ticket_id.write({'validacionesRefaccion': [(4, 0, idValidacion)] })
                self.ticket_id.write({'ticketValidadoElDia': datetime.datetime.now() })
                self.env['helpdesk.diagnostico'].create({
                                                            'ticketRelacion': self.ticket_id.id,
                                                            'comentario': comentarioGenerico,
                                                            'estadoTicket': self.ticket_id.stage_id.name,
                                                            'evidencia': [(6,0,self.evidencia.ids)],
                                                            'mostrarComentario': self.check,
                                                            'creadoPorSistema': False
                                                        })
                self.ticket_id.obten_ulimo_diagnostico_fecha_usuario()
                self.ticket_id.datos_ticket_2()
            #mensajeTitulo = 'Creación y validación de refacción!!!'
            #mensajeCuerpo = 'Se creo y valido la solicitud ' + str(self.ticket_id.x_studio_field_nO7Xg.name) + ' para el ticket ' + str(self.ticket_id.id) + '.'    
        #else:
            #mensajeTitulo = 'Error'
            #mensajeCuerpo = 'No es posible validar un ticket con la misma refacción y/o accesorio seleccionado anteriormente'
        wiz = self.env['helpdesk.alerta'].create({'mensaje': mensajeCuerpo})
        view = self.env.ref('helpdesk_update.view_helpdesk_alerta')
        return {
                'name': _('Resultado'),
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

    
    
    def agregarProductos_2(self):
        _logger.info('entro')
        #self.ticket_id.x_studio_productos = [(6, 0, self.productos.ids)]
        lista = [[5,0,0]]
        listaDeCantidades = []
        for refaccion in self.accesorios:
            lista.append( [4, refaccion.productos.id] )
            listaDeCantidades.append(refaccion.cantidadPedida)
        self.ticket_id.write({'x_studio_productos': lista})

        lista = []
        productos_en_wizard = self.mapped('accesorios')
        productos_en_wizard_ids = self.mapped('accesorios.productos.id')
        #_logger.info('productos_en_wizard: ' + str(productos_en_wizard))
        #_logger.info('productos_en_wizard_ids: ' + str(productos_en_wizard_ids))
        prodcutos_en_ticket_ids = self.ticket_id.mapped('x_studio_productos.id')
        #_logger.info('prodcutos_en_ticket_ids: ' + str(prodcutos_en_ticket_ids))
        prodcutos_en_ticket = self.ticket_id.x_studio_productos #self.ticket_id.mapped('x_studio_productos')
        #_logger.info('prodcutos_en_ticket: ' + str(prodcutos_en_ticket))
        indice = 0
        for refaccion in self.accesorios:
            producto_en_wizard = refaccion.productos.id
            #producto_en_ticket = prodcutos_en_ticket[indice]
            for producto_en_ticket in prodcutos_en_ticket:
                if producto_en_wizard == producto_en_ticket.id:
                    vals = {
                            'x_studio_cantidad_pedida': refaccion.cantidadPedida
                    }
                    lista.append( [1, producto_en_wizard, vals] )
                    break
            indice = indice + 1
        #_logger.info('3312: lista actualiza cantidades: ' + str(lista))
        self.ticket_id.write({'x_studio_productos': lista})
        #indice = 0
        #for refaccion in self.ticket_id.x_studio_productos:
        #    refaccion.x_studio_cantidad_pedida = listaDeCantidades[indice]
        #    indice = indice + 1

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
    
