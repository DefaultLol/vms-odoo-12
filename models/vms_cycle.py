from odoo import fields, models


class VmsCycle(models.Model):
    _name = 'vms.cycle'
    _order = 'name asc'

    name = fields.Char(required=True)
    task_ids = fields.Many2many('vms.task', string="Tasks", required=True)
    frequency = fields.Integer(required=True)
    uom_id = fields.Many2one('uom.uom',ondelete='set null',string="Unité de mesure",index=True,required=True)
    type=fields.Many2one('vms.cycle.type',string='Type',required=True)
    active = fields.Boolean(default=True)



class CycleType(models.Model):
    _name='vms.cycle.type'

    name=fields.Char(string='Name')
