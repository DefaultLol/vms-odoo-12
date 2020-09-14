from odoo import api, fields, models

class VmsProductLine(models.Model):
    _description = 'VMS Product Lines'
    _name = 'vms.product.line'

    @api.depends('product_id')
    def _get_stock_value(self):
        for rec in self:
            rec.product_stock_qty=rec.product_id.qty_available

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
    product_stock_qty=fields.Float(string="Stock quantity",compute='_get_stock_value',store=True)
    # product_stock_qty = fields.Float(string="Stock quantity",default= lambda self:self.product_id.qty_available)
    task_id = fields.Many2one(
        'vms.task',
        string='Task',
    )
    purchase_request = fields.Many2one('vms.order.line',string='PO line id')
    order_line_id = fields.Many2one(
        'vms.order.line',
        string='Activity')

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
        #get vms spare parts out option record to get the id
        type=self.env['stock.picking.type'].search([
            ('name','=','VMS Spare Parts OUT')
        ])
        stock_type_id=type.id
        self.env['stock.picking'].create({
            'location_id':self.find_wh_id(),
            'location_dest_id':self.find_vehicle_location_id(unit_id),
            'picking_type_id':stock_type_id,
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

    @api.onchange('product_id')
    def get_stock(self):
        self.product_stock_qty=self.product_id.qty_available

