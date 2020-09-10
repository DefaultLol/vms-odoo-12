from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_type_id = fields.Many2one('stock.picking.type',string='Type d\'opération')
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_type_id.code',
        readonly=True)
    odometer=fields.Float(readonly=True)

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    wh_vms_out_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='VMS OUT Picking Operation',)

    @api.multi
    def write(self, vals):
        for rec in self:
            if 'delivery_steps' in vals.keys():
                vms_out_operation_id = self.env.ref(
                    'vms.stock_picking_type_vms_out')
                if rec.wh_vms_out_picking_type_id != vms_out_operation_id:
                    vals.update({
                        'wh_vms_out_picking_type_id': vms_out_operation_id.id,
                    })
            return super(StockWarehouse, self).write(vals)

    def get_routes_dict(self):
        res = super(StockWarehouse, self).get_routes_dict()
        stock_loc_obj = self.env['stock.location']
        prod_loc = stock_loc_obj.search(
            [('usage', '=', 'production')], limit=1)
        for warehouse in self.browse(res.keys()):
            res[warehouse.id]['ship_only'].append(
                self.Routing(
                    warehouse.lot_stock_id,
                    prod_loc,
                    warehouse.wh_vms_out_picking_type_id))
        return res