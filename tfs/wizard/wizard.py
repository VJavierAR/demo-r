from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo import exceptions

class StockImmediateTransfer(models.TransientModel):
    _name = 'tfs.ticket'
    _description = 'Creacion de ticket'
    tfs_ids = fields.Many2many('tfs.tfs', 'tfs_tsf_ticket_rel')


    def forzar(self):
    	for r in self.tfs_ids:
            r.valida()
            #r.write({'estado':'Valido'})
    		#In=r.inventario.search([['product_id.name','=',r.producto.name],['location_id','=',r.almacen.lot_stock_id.id]]).sorted(key='quantity',reverse=True)
    		#if(len(In)>0):
		   # 	In[0].write({'quantity':In[0].quantity-1})
		   # 	r.write({'estado':'Valido'})
    	#	else:
    	#		raise exceptions.UserError("No existen cantidades en el almacen para el producto " + r.producto.name)

    def crear_ticket(self):
    	for r in self.tfs_ids:
            self.env['helpdesk.ticket'].create({'partner_id':self.cliente.id,'x_studio_empresas_relacionadas':self.localidad.id,'team_id':9,'diagnosticos':[(0,0,{'estadoTicket':'Abierto','comentario':'Falla en rendimiento <60%'})],'stage_id':89,'name':'Falla en rendimiento <60% '+'Serie: '+r.serie.name,'x_studio_equipo_por_nmero_de_serie':[(4,r.serie.id)]})
            r.write({'estado':'Valido'})
    		#else:
    		#	raise exceptions.UserError("No existen cantidades en el almacen para el producto " + r.producto.name)

