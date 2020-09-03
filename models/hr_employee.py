from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    mechanic = fields.Boolean(
        help='Validates if the employee is mechanic.')