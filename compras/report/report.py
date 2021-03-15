# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging, ast
_logger = logging.getLogger(__name__)
import datetime

class report(models.AbstractModel):
    _name = 'report.report_custom_purchase_template'