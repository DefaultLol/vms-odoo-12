from odoo import fields, models


class VmsTask(models.Model):
    _name = 'vms.task'
    _description = 'VMS Task'
    _order = 'name asc'

    name = fields.Char(required=True)
    duration = fields.Float(required=True, store=True)

    active = fields.Boolean(default=True)