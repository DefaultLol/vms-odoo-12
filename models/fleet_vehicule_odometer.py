from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    type = fields.Selection([
        ('maintenance','Maintenance'),
        ('gasoil','Gasoil'),
        ('autre','Autre')
    ],string="Type",default='autre')
    order_id=fields.Many2one('vms.order',string='Order')
    # cycle_types = fields.Many2many('vms.cycle.type', string='Cycle Types')
