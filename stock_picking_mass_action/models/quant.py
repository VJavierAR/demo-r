from odoo import _, fields, api
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import logging, ast
_logger = logging.getLogger(__name__)
import threading
import base64
import datetime

class StockQuan(Model):
    _inherit = 'stock.quant'
    quants_registro=fields.One2many('stock.quant.line','quant_id')
    regla=fields.Many2one('stock.warehouse.orderpoint')

    @api.model
    def _unlink_zero_quants(self):
        """ _update_available_quantity may leave quants with no
        quantity and no reserved_quantity. It used to directly unlink
        these zero quants but this proved to hurt the performance as
        this method is often called in batch and each unlink invalidate
        the cache. We defer the calls to unlink in this method.
        """
        precision_digits = max(6, self.env.ref('product.decimal_product_uom').digits * 2)
        # Use a select instead of ORM search for UoM robustness.
        #query = """SELECT id FROM stock_quant WHERE round(quantity::numeric, %s) = 0 AND round(reserved_quantity::numeric, %s) = 0;"""
        #params = (precision_digits, precision_digits)
        #self.env.cr.execute(query, params)
        #quant_ids = self.env['stock.quant'].browse([quant['id'] for quant in self.env.cr.dictfetchall()])
        #quant_ids.sudo().unlink()

    #@api.onchange('quantity')
    def actualizaRegla(self):
        todo=self.search([])
        tt=todo.filtered(lambda x:x.x_studio_almacn.x_studio_mini==True)
        _logger.info(str(len(tt)))
        for t in tt:
            r=self.env['stock.warehouse.orderpoint'].search([['location_id','=',t.location_id.id],['product_id','=',t.product_id.id]])
            if(r.id):
                t.sudo().write({'regla':r.id})
        #if(self.x_studio_almacn.x_studio_mini==True):
        #    q=self.env['stock.warehouse.orderpoint'].search([['location_id','=',self.location_id.id],['product_id','=',self.product_id.id]])
        #    if(q.mapped('id')==[]):
        #        p=self.env['product.product'].search([['name','like',self.product_id.name]])
         #       q=self.env['stock.warehouse.orderpoint'].search([['location_id','=',self.location_id.id],['product_id','in',p.mapped('id')]])
         #       q[0].x_studio_existencia=self.quantity
         #       q[0].x_studio_existencia_2=self.quantity
         #   else:    
          #      q.x_studio_existencia=self.quantity
          #      q.x_studio_existencia_2=self.quantity



    def archivaReporte(self):
        almacenes=self.env['stock.warehouse'].search([['x_studio_cliente','=',False]])
        r=self.search([['location_id','in',almacenes.mapped('lot_stock_id.id')]])
        r[0].write({'x_studio_arreglo':str(r.mapped('id'))})
        pdf=self.env.ref('stock_picking_mass_action.quant_xlsx').sudo().render_xlsx(data=r[0],docids=r[0].id)[0]
        reporte = base64.encodestring(pdf)
        self.env['quant.history'].create({'reporte':reporte,'fecha':datetime.datetime.now().date()})
    
    def edit(self):
        wiz = self.env['quant.action'].create({'quant':self.id,'producto':self.product_id.id,'cantidad':self.quantity,'ubicacion':self.x_studio_field_kUc4x.id,'usuario':self.env.uid})
        view = self.env.ref('stock_picking_mass_action.view_quant_action_form')
        return {
            'name': _('Existencia'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'quant.action',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

class StockQuantLine(Model):
    _name='stock.quant.line'
    _description='registro de cambios'
    descripcion=fields.Char()
    cantidadAnterior=fields.Float()
    cantidadReal=fields.Float()
    quant_id=fields.Many2one('stock.quant')
    usuario=fields.Many2one('res.users')

class HistoricoInventario(Model):
    _name='quant.history'
    _description='Historico Inventario'
    fecha=fields.Date()
    reporte=fields.Binary()