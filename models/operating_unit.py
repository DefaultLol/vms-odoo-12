from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    order_sequence_id = fields.Many2one(
        'ir.sequence', string='Order Sequence')
    report_sequence_id = fields.Many2one(
        'ir.sequence', string='Report Sequence')