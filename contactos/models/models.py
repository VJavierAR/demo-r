# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api,tools
from odoo.tools.mimetypes import guess_mimetype
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)
from odoo.tools import pycompat
import datetime
class contactos(models.Model):
    _inherit = 'res.partner'
    nameGerardo = fields.Char()
    grupo = fields.Selection([('101','SOCIEDAD P'),('100','MANUEL SANTIAGO'),('99','KROMA ADUANALES'),('98','GRUPO YMCA'),('97','GRUPO VAEO'),('96','GRUPO TURISTICO'),('95','GRUPO TUM'),('94','GRUPO TRAFIMAR'),('93','GRUPO TECNOVIDRIO'),('92','GRUPO TECNOMAN'),('91','GRUPO SPLITTEL'),('90','GRUPO SILSA'),('89','GRUPO SCM'),('88','Grupo Sciencepool'),('87','GRUPO SAMODACA KAMAJI'),('86','GRUPO SACYR'),('85','GRUPO PUNTA DEL CIELO'),('84','GRUPO PORCELANITE'),('83','GRUPO POP'),('82','GRUPO PLASTIGLAS'),('81','GRUPO PLANETA'),('80','GRUPO PIUCAPITAL'),('79','GRUPO PEGASO'),('78','GRUPO PALOS GARZA'),('77','GRUPO PALMAS'),('76','GRUPO ORENES'),('75','GRUPO OHL'),('74','GRUPO NIHON'),('73','GRUPO NICRO'),('72','GRUPO MVS RADIO'),('71','GRUPO MULTIMEDIOS'),('70','GRUPO MILENIO'),('69','GRUPO METIS'),('68','GRUPO MAZDA'),('67','GRUPO LONDRES'),('66','GRUPO LOGIS'),('65','GRUPO LB'),('64','GRUPO KS'),('63','GRUPO KROMA'),('62','GRUPO JMF SERVICIOS CORPORATIVOS'),('61','GRUPO JEFFERSON'),('60','GRUPO J GARCIA'),('59','GRUPO IPADE'),('58','GRUPO INVEX'),('57','Grupo Intellego'),('56','GRUPO INDORAMA'),('55','GRUPO IENOVA'),('54','GRUPO HUMBRALL'),('53','GRUPO HIR CASA'),('52','GRUPO GRAMOSA'),('51','GRUPO GR'),('50','GRUPO GPL'),('49','GRUPO GNSYS'),('48','GRUPO FYRME'),('47','GRUPO FRIGUS'),('46','GRUPO FLEXIUS'),('45','GRUPO FIBREMEX'),('44','GRUPO FEDERAL MOGUL'),('43','GRUPO EULEN'),('42','GRUPO EMERSON'),('41','GRUPO EDUARDO DIAZ'),('40','GRUPO DRAKO'),('39','GRUPO DRAGON'),('38','GRUPO DIVOL'),('37','GRUPO DISH'),('36','GRUPO DICO'),('35','GRUPO CUSHMAN'),('34','GRUPO CRISVISA'),('33','GRUPO CONSOLTUM'),('32','GRUPO CONSOLID'),('31','GRUPO COMEX'),('30','GRUPO CIBANCO'),('29','GRUPO CHESS'),('28','GRUPO CELUPAL'),('27','GRUPO CBM'),('26','GRUPO CASC'),('25','GRUPO CASA ORTIZ'),('24','GRUPO CARLOS SLIM'),('23','GRUPO BERNAL'),('22','GRUPO BDF'),('21','GRUPO BB SOLUTION'),('20','GRUPO AVANZIA'),('19','GRUPO AVANTE'),('18','GRUPO ATLAS'),('17','GRUPO ARPA'),('16','GRUPO ARO'),('15','GRUPO ANGELES'),('14','GRUPO ANAHUAC'),('13','GRUPO ALTAVISTA'),('12','GRUPO ALDO CONTI'),('11','GRUPO ALDEN'),('10','GRUPO ABENGOA'),('9','GRUPO 3E'),('8','Grupo 3 H Empaque'),('7','GRUPO 2000'),('6','FERROMEX'),('5','ENTREGAS P'),('4','EL CORTE INGLES'),('3','CODERE'),('2','CARGOQUIN'),('1','AVIGRUPO'),('0','Ningún grupo')])
    razonSocial = fields.Selection([('0','DOCUMENTO INTEGRAL CORPORATIVO, SA DE CV'),('1','GN SYS CORPORATIVO S.A. DE C.V.'),('2','GRUPO GNSYS SOLUCIONES SA DE CV'),('3','SERVICIOS CORPORATIVOS GENESIS, S.A DE C.V.')],track_visibility='onchange')
    distribuidor=fields.One2many('zona.distribuidor','rel_contact')
    tipoCliente=fields.Selection([('Arrendamiento','Arrendamiento'),('Digitalización','Digitalización'),('Mixto','Mixto'),('PENDIENTE INACTIVO','PENDIENTE INACTIVO'),('Prospecto','Prospecto'),('Servicio sin tóner','Servicio sin tóner'),('Venta','Venta')],track_visibility='onchange')
    active = fields.Boolean(default = True, track_visibility = 'onchange')
    phone = fields.Char(string = 'Teléfono', track_visibility = 'onchange')
    mobile = fields.Char(string = 'Móvil', track_visibility = 'onchange')
    email = fields.Char(string = 'Correo electrónico', track_visibility = 'onchange')
    comment = fields.Text(string = 'Notas', track_visibility = 'onchange')
    street_name = fields.Char(string = 'Calle', track_visibility = 'onchange', store = True)

class zonaDistribuidor(models.Model):
	_name='zona.distribuidor'
	_description='Zona x distribuidor'
	estado=fields.Many2one('res.country.state','Estado')
	municipio=fields.Char('Municipion')
	rel_contact=fields.Many2one('res.partner')

class ContactosCes(models.Model):
    _inherit='res.partner'
    notaPendiente=fields.Char()
    fechaPendienteInactivo=fields.Date()
    arreglo=fields.Char()
    busqueda=fields.Char()
    street=fields.Char(string='Calle',track_visibility='onchange')
    street_number=fields.Char(string='Exterior',track_visibility='onchange')
    street_number2=fields.Char(string='Interior',track_visibility='onchange')
    contact_address = fields.Char(string='Complete Address')

    def Reporte(self):
        fecha=datetime.datetime.now().date()
        sa=self.search([['tipoCliente','=','PENDIENTE INACTIVO']])
        pos=sa
        pos[0].write({'arreglo':str(pos.mapped('id'))})
        template_id2=self.env['mail.template'].search([('id','=',79)], limit=1)
        mail=template_id2.generate_email(pos[0].id)
        pdf=self.env.ref('stock_picking_mass_action.contacto_pendiente_xlsx').sudo().render_xlsx(data=pos[0],docids=pos[0].id)[0]
        reporte = base64.encodestring(pdf)
        at=self.env['ir.attachment'].create({'name':'Reporte Clientes Pendientes Inactivos','datas':reporte,'datas_fname':'Reporte Clientes Pendientes Inactivos'})
        mail['subject']="Reporte de (Pendientes Inactivos)"
        mail['attachment_ids']=[(6,0,[at.id])]
        self.env['mail.mail'].create(mail).send()

    @api.onchange('tipoCliente')
    def pendienteInactivo(self):
    	for record in self:
    		if(record.tipoCliente=='PENDIENTE INACTIVO'):
    			record['fechaPendienteInactivo']=datetime.datetime.now().date()
    @api.onchange('busqueda')
    def busquedaContac(self):
        return {'domain':{'child_ids': [('name', 'ilike', self.busqueda)]}}

    """            
    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('import_file'):
            self._check_import_consistency(vals_list)
        for vals in vals_list:
            if vals.get('website'):
                vals['website'] = self._clean_website(vals['website'])
            if vals.get('parent_id'):
                vals['company_name'] = False
            if not vals.get('image'):
                vals['image'] = self._get_default_image(vals.get('type'), vals.get('is_company'), vals.get('parent_id'))
                tools.image_resize_images(vals, sizes={'image': (1024, None)})
                partners = super(ContactosCes, self).create(vals_list)
            if self.env.context.get('_partners_skip_fields_sync'):
                return partners
            for partner in partners:
                if(partner.type=='delivery'):
                    cod=self.env['ir.sequence'].next_by_code('almacenes')
                    self.env['stock.warehouse'].sudo().create({'name':partner.display_name,'code':cod,'x_studio_cliente':True,'x_studio_field_E0H1Z':partner.id})
            for partner, vals in pycompat.izip(partners, vals_list):
                partner._fields_sync(vals)
                partner._handle_first_contact_creation()
                return partners
    """            