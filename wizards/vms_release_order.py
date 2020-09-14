from datetime import datetime
from odoo import fields,api,models
from odoo.exceptions import ValidationError

class VmsReleaseOrder(models.TransientModel):
    _name='vms.wizard.release.order'

    my_button = fields.Boolean('Label')
    invisible_field=fields.Char()
    finished=fields.Boolean(default=False)
    transfert=fields.Many2many('stock.picking',readonly=True)

    @api.model
    def default_get(self, default_fields):
        res = super(VmsReleaseOrder, self).default_get(
            default_fields)
        order_id = self._context.get('active_ids')
        name = self.env['vms.order'].browse(order_id).name
        pickings=self.env['stock.picking'].search([
            ('origin','=',name)
        ])
        data = []
        for rec in pickings:
            data.append((0, 0, {
                'name': rec.name,
                'state': rec.state
            }))
        res['transfert'] = data

        return res

    @api.multi
    @api.onchange('my_button')
    def onchange_my_button(self):
        if(self.invisible_field):
            for record in self:
                for rec in record.transfert:
                    if rec.state != 'done':
                        raise ValidationError('Picking are not done')
            self.finished=True
            self.release()
            self.create_odometer()
            return {
                'warning': {
                    'title': 'Released order!',
                    'message': 'Successfully released order'}
            }
        else:
            self.invisible_field='test'

    @api.multi
    def release(self):
        order_id = self._context.get('active_ids')
        print(order_id)
        order = self.env['vms.order'].browse(order_id)
        for line in order.order_line_ids:
            line.action_done()
        if order.type == 'corrective':
            for report in order.report_ids:
                report.state = 'closed'
        order.write({
            'state': 'released'
        })

    def create_odometer(self):
        order_id = self._context.get('active_ids')
        order = self.env['vms.order'].browse(order_id)
        if(order.type == "preventive"):
            odometer = order.current_odometer
        else:
            odometer = order.report_ids.kilometre_new

        self.env['fleet.vehicle.odometer'].create({
            'date': datetime.now(),
            'vehicle_id': order.unit_id.id,
            'driver_id': order.unit_id.driver_id,
            'value': odometer,
            'type': 'maintenance'
        })


