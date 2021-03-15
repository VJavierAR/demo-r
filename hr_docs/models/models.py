# -*- coding: utf-8 -*-

from odoo import models, fields, api
from PyPDF2 import PdfFileMerger, PdfFileReader
from io import BytesIO as StringIO
import base64
class hr_docs(models.Model):
    _inherit = 'hr.employee'
    archivos=fields.One2many('hr.document','hr_employee')
    concentrado=fields.Binary('Concentrado',store='True')
    
    
    @api.onchange('archivos')
    def fghhrde(self):
        merger = PdfFileMerger()
        #self.concentrado=''
        for r in self.archivos:
            if r.archivo:
                f2=base64.b64decode(r.archivo)
                H=StringIO(f2)
                merger.append(H)
                
        merger.write('doc.pdf')
        f=open('doc.pdf','rb').read()
        f1=base64.b64encode(f)
        self.concentrado=f1

    
    
    
    
class hr_docs_lines(models.Model):
    _name='hr.document'
    _description = 'Merge documentos hr'
    name=fields.Char('Descripcion')
    archivo=fields.Binary('Archivo')
    hr_employee=fields.Many2one('hr.employee')