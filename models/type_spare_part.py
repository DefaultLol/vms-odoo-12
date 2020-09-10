from odoo import fields, models,api

class InheritProduct(models.Model):
    _inherit = "product.template"

    spare_part_id = fields.Many2one('vms.part.type',ondelete='set null',string="Spare part type",index=True,required=True)
    unit_ids = fields.Many2many(
        'fleet.vehicle',
        required=True,
        string='Vehicles',
        store=False)

    @api.onchange('spare_part_id')
    def change_part(self):
        print('changed')


class TypeSparePart(models.Model):
    _name = "vms.part.type"
    _description = "Type of spare parts"

    name = fields.Char(string="Type name")