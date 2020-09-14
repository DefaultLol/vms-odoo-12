from odoo import fields, models,api

class OperatingUnit(models.Model):
    _inherit = 'product.template'

    spare_part = fields.Boolean('Est pièce détaché',default=True)

    # @api.onchange('spare_part')
    # def is_spare_part(self):