from odoo import fields, models


class VmsProgram(models.Model):
    _name = 'vms.program'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    cycle_ids = fields.Many2many(
        'vms.cycle',
        required=True,
        string='Cycle(s)',
        store=True)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)