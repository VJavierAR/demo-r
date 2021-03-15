# -*- coding: utf-8 -*-
{
    'name': "res_user",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Cesar Lopez R",
    'website': "http://",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
  'version': '12.0.1.0.0',
    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded

    # only loaded in demonstration mode
    #'demo': [
     #   'demo/demo.xml',
    #],
    'installable': True,
    'application': True,
    'auto_install': False,
}
