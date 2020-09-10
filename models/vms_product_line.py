from odoo import api, fields, models

class VmsProductLine(models.Model):
    _description = 'VMS Product Lines'
    _name = 'vms.product.line'

    product_id = fields.Many2one(
        'product.template',
        domain=[('spare_part','=',True)],
        required=True,
        string='Spare Part')
    product_qty = fields.Float(
        required=True,
        default=0.0,
        string='Quantity',
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    task_id = fields.Many2one(
        'vms.task',
        string='Task',
    )
    order_line_id = fields.Many2one(
        'vms.order.line',
        string='Activity')
    # procurement_ids = fields.One2many(
    #     'procurement.order',
    #     'vms_product_line_id',
    #     string='Procurement Orders',)

    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     self.product_uom_id = self.product_id.uom_id
    #
    # @api.multi
    # def _prepare_order_line_procurement(self, group_id=False):
    #     self.ensure_one()
    #     order = self.order_line_id.order_id
    #     prod_loc_id = (
    #         order.warehouse_id.wh_vms_out_picking_type_id.
    #         default_location_dest_id
    #     )
    #     return {
    #         'name': self.product_id.name,
    #         'origin': order.name,
    #         'product_id': self.product_id.id,
    #         'product_qty': self.product_qty,
    #         'product_uom': self.product_uom_id.id,
    #         'company_id': self.env.user.company_id.id,
    #         'group_id': group_id,
    #         'vms_product_line_id': self.id,
    #         'date_planned': fields.Datetime.now(),
    #         'location_id': prod_loc_id.id,
    #         'route_ids': self.product_id.route_ids and [
    #             (4, self.product_id.route_ids.ids)] or [],
    #         'warehouse_id': order.warehouse_id.id,
    #     }
    #
    # @api.multi
    # def procurement_create(self):
    #     new_procs = self.env['procurement.order']
    #     proc_group_obj = self.env["procurement.group"]
    #     for line in self:
    #         if (line.order_line_id.state != 'process' or not
    #                 line.product_id._need_procurement()):
    #             continue
    #         qty = 0.0
    #         for procurement in line.procurement_ids:
    #             qty += procurement.product_qty
    #
    #         if not line.order_line_id.order_id.procurement_group_id:
    #             vals = line.order_line_id.order_id._prepare_procurement_group()
    #             line.order_line_id.order_id.procurement_group_id = (
    #                 proc_group_obj.create(vals)
    #             )
    #
    #         vals = line._prepare_order_line_procurement(
    #             line.order_line_id.order_id.procurement_group_id.id)
    #         vals['product_qty'] = line.product_qty - qty
    #         new_proc = self.env["procurement.order"].with_context(
    #             procurement_autorun_defer=True).create(vals)
    #         new_procs += new_proc
    #     new_procs.run()
    #     return new_procs

    def find_wh_id(self):
        res = self.env['stock.location'].search([
            ('name','=','Stock')
        ])
        return res[0].id

    def find_vehicle_location_id(self,unit_id):
        res = self.env['stock.location'].search([
            ('name', '=', unit_id.virtual_stock)
        ])
        return res[0].id

    def insert_spare_parts(self):
        #create array to populate one2many field
        products = []
        for x in self:
            products.append((0, 0, {
                "name": "lol",
                "product_uom": 1,
                'product_id': x.product_id.id,
                'product_uom_qty': x.product_qty,
                'reserved_availability': x.product_qty,
                'quantity_done': x.product_qty,
            }))
        return products

    def move_prod(self,unit_id,products):
        self.env['stock.picking'].create({
            'location_id':self.find_wh_id(),
            'location_dest_id':self.find_vehicle_location_id(unit_id),
            'picking_type_id':7,
            'origin':self.order_line_id.order_id.name,
            'odometer':unit_id.odometer,
            'move_ids_without_package':products
        })
        # move = self.env['stock.move'].create({
        #     'name': 'Use on MyLocation',
        #     'location_id': self.find_wh_id(),
        #     'location_dest_id': self.find_vehicle_location_id(unit_id),
        #     'product_id': prod.id,
        #     'product_uom': 1,
        #     'product_uom_qty': 15,
        # })
        # move._action_confirm()
        # move._action_assign()
        # move.move_line_ids.write(
        #     {'qty_done': 15})  # This creates a stock.move.line record. You could also do it manually
        # move._action_done()

    def stock_move(self,unit_id):
        products=self.insert_spare_parts()
        for y in self:
            y.move_prod(unit_id,products)
            break
