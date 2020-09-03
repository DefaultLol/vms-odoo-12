from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = 'product.template'

    spare_part = fields.Boolean('Est pièce détaché',default=True)