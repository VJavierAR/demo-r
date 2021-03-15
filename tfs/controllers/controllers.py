# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)

class SaleOrderCompatibles(http.Controller):
    @http.route('/tfs/autoriza/<int:tfs_id>', auth='public')
    def index(self, tfs_id,**kw):
        mensaje="No cuenta con permisos para relizar esta acción"
        p=request.env['tfs.tfs'].search([['id','=',tfs_id]])
        uido=request.env.context.get('uid')
        u=request.env['res.groups'].search([['name','=','miniAlmacen']]).users.filtered(lambda x:x.id==uido)
        if(u.id!=False):
            if(p.estado=="xValidar"):
                p.valida()
            mensaje="Proceso  "+str(p.name)+" Autorizado"
        return mensaje


class SaleOrderCompatiblesCancel(http.Controller):
    @http.route('/tfs/cancela/<int:tfs_id>', auth='public')
    def index(self, tfs_id,**kw):
        mensaje="No cuenta con permisos para relizar esta acción"
        p=request.env['tfs.tfs'].search([['id','=',tfs_id]])
        uido=request.env.context.get('uid')
        u=request.env['res.groups'].search([['name','=','miniAlmacen']]).users.filtered(lambda x:x.id==uido)
        if(u.id!=False):
            p.canc()
            mensaje="Proceso  "+str(p.name)+" Cancelado"
        return mensaje