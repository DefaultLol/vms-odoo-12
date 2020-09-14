from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    type = fields.Selection([
        ('maintenance','Maintenance'),
        ('gasoil','Gasoil'),
        ('autre','Autre')
    ],string="Type",default='autre')