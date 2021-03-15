# -*- coding: utf-8 -*-
from odoo import models, fields, api,_,exceptions
import base64
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
#from io import BytesIO
from pdf2image import convert_from_path, convert_from_bytes
import os
import re
from PyPDF2 import PdfFileMerger, PdfFileReader,PdfFileWriter
from io import BytesIO as StringIO
import base64
import datetime,time
from odoo.tools.mimetypes import guess_mimetype
import logging, ast
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
_logger = logging.getLogger(__name__)
import xml.etree.ElementTree as ET
from xml.dom import minidom

class compras(models.Model):
    _inherit = 'product.product'


    def agregarCompatible(self):
        wiz = self.env['add.compatible'].create({'productoInicial':self.id})
        view = self.env.ref('stock_picking_mass_action.view_addcompatile_action_form')
        return {
            'name': _('Agregar Compatibles'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.compatible',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }