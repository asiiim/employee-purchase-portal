# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    
    # Add a field called "Allowed Product Categories"
    """
        - Type of the field is Many2many
    """
    allowed_product_categories = fields.Many2many('product.category', 
        string='Allowed Product Categories')