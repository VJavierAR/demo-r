# -*- coding: utf-8 -*-

from odoo import _, models, fields, api, tools
from email.utils import formataddr
from odoo.exceptions import UserError,RedirectWarning
from odoo import exceptions, _
import logging, ast
import datetime, time
_logger = logging.getLogger(__name__)

class DcasUpdate(models.Model):
	_inherit = 'product.product'
	x_studio_color_bn=fields.Selection([('B/N','B/N'),('Color','Color')])	

     
