from datetime import datetime
from datetime import timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsOrderLine(models.Model):
    _name = 'vms.order.line'
    _description = 'VMS Order Line'

    # @api.model
    # def _test_end_date(self):
    #     print('lol')
    #     print(self.duration)
    #     return timedelta(hours=self.duration)
    #     # return timedelta(hours=self.duration)
    #     # end_date=null
    #     # for rec in self:
    #     #     strp_date = datetime.strptime(str(rec.start_date), "%Y-%m-%d %H:%M:%S")
    #     #     end_date = strp_date + timedelta(hours=rec.duration)
    #     #
    #     # return end_date

    @api.depends('start_date')
    def _end_date_default(self):
        for rec in self:
            if rec.start_date:
                strp_date = datetime.strptime(
                    str(rec.start_date), "%Y-%m-%d %H:%M:%S")
                rec.end_date = strp_date + timedelta(hours=rec.duration)

    task_id = fields.Many2one(
        'vms.task', string='Task',
        required=True)
    start_date = fields.Datetime(
        default=fields.Datetime.now(),
        string='Schedule start',
        required=True)
    end_date = fields.Datetime(
        string='Schedule end',
        compute='_end_date_default',
        store=True)
    start_date_real = fields.Datetime(
        string='Real start date', readonly=True)
    end_date_real = fields.Datetime(
        string='Real Finishing', readonly=True)
    duration = fields.Float(store=True)
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier', '=', True)])
    external = fields.Boolean()
    product_id = fields.Many2one(
        'product.template',
        string="Product",
        domain=[('type', '=', 'service'), ('purchase_ok', '=', True)])
    qty_product = fields.Float(string="Quantity", default="1.0")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel')])
    real_duration = fields.Float(readonly=True)
    spare_part_ids = fields.One2many(
        'vms.product.line',
        'order_line_id',
        string='Spare Parts',
        help='You must save the order to select the mechanic(s).')
    spare_part_ids1 = fields.One2many(
        'vms.product.line',
        'purchase_request',
        string='Appel d\'offres associés',
        help='You must save the order to select the mechanic(s).')
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True)
    purchase_state = fields.Boolean(
        string="Purchase Order State Done",
        compute='_compute_purchase_state')
    order_id = fields.Many2one('vms.order', string='Order', readonly=True)
    real_time_total = fields.Integer()

    # @api.model
    # def default_get(self, fields):
    #     res=super(VmsOrderLine,self).default_get(fields)
    #     order_id = self._context.get('default_task_id')
    #     print(order_id)
    #     spare_part_ids=[(5,0,0)]
    #     data=self.env['vms.product.line'].search([])
    #     print('test')
    #     print(self.get_current_task())
    #     for rec in data:
    #         line=(0,0,{
    #             'product_id':1,
    #             'product_qty':15,
    #             'product_uom_id':1
    #         })
    #         spare_part_ids.append(line)
    #     res.update({
    #         'spare_part_ids':spare_part_ids
    #     })
    #     return res

    # def get_current_task(self):
    #     print(self.task_id)
    #     return self.task_id

    @api.multi
    def unlink(self):
        self.spare_part_ids.unlink()
        return super(VmsOrderLine, self).unlink()

    @api.onchange('task_id')
    def _onchange_task(self):
        print(self.task_id)
        self.clear_field1()
        for rec in self:
            rec.duration = rec.task_id.duration
            if rec.start_date:
                strp_date = datetime.strptime(
                    str(rec.start_date), "%Y-%m-%d %H:%M:%S")
                rec.end_date = strp_date + timedelta(hours=rec.duration)
            for spare_part in rec.task_id.spare_part_ids:
                spare = rec.spare_part_ids.new({
                    'product_id': spare_part.product_id.id,
                    'product_qty': spare_part.product_qty,
                    'product_uom_id': spare_part.product_uom_id.id,
                    'state': 'draft'})

                rec.spare_part_ids += spare

    @api.onchange('duration')
    def _onchange_duration(self):
        for rec in self:
            if rec.start_date:
                strp_date = datetime.strptime(
                    str(rec.start_date), "%Y-%m-%d %H:%M:%S")
                rec.end_date = strp_date + timedelta(hours=rec.duration)

    @api.depends('start_date_real', 'end_date_real')
    def _compute_real_time_total(self):
        for rec in self:
            start_date = datetime.strptime(rec.start_date_real, '%Y-%m-%d')
            end_date = datetime.strptime(rec.end_date_real, '%Y-%m-%d')
            total_days = start_date - end_date
            rec.real_time_total = total_days.days

    @api.depends('task_id')
    def lol(self):
        print('lol')

    @api.depends('purchase_order_id')
    def _compute_purchase_state(self):
        for rec in self:
            rec.purchase_state = (rec.purchase_order_id.id and
                                  rec.purchase_order_id.state == 'done')

    @api.multi
    def action_process(self,unit_id):
        for rec in self:
            if rec.order_id.state != 'open':
                raise ValidationError(_('The order must be open.'))
            rec.write({
                'state': 'process',
                'start_date_real': fields.Datetime.now(),
            })
            if not rec.external:
                if not rec.spare_part_ids:
                    return True
                rec.spare_part_ids.stock_move(unit_id)

    @api.multi
    def get_real_duration(self):
        for rec in self:
            rec.end_date_real=datetime.now()
            test=rec.end_date_real-rec.start_date_real
            seconds = test.total_seconds()
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            t, hours = divmod(float(hours), 24)
            t, minutes = divmod(float(minutes), 60)
            # rec.real_duration = sum([task.duration for task in rec.task_id])
            rec.real_duration=hours

    @api.multi
    def action_done(self):
        for rec in self:
            if rec.external:
                if not rec.purchase_state:
                    raise ValidationError(_(
                        'Verify that purchase order are in done state '
                        'to continue'))
            rec.get_real_duration()
            rec.end_date_real = fields.Datetime.now()
            rec.state = 'done'

    @api.multi
    def action_cancel(self):
        for rec in self:
            if not rec.external:
                if self.mapped('spare_part_ids').filtered(lambda x: x.state == 'done'):
                    raise ValidationError(
                        _('Error, you cannot cancel a maintenance order'
                            ' with done stock moves.'))
                self.mapped('spare_part_ids').mapped(
                    'procurement_ids').cancel()
            rec.write({
                'state': 'cancel',
                'start_date_real': False,
            })

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            rec.state = 'draft'

    def purchase_generator(self):
        partlist = []
        if(len(self.spare_part_ids1) != 0):
            for x in self:
                for line in x.spare_part_ids1:
                    partlist.append((0,0, {
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom_id': 1,
                        'schedule_date': fields.Date.context_today(self),
                    }))
                if not partlist:
                    raise Warning(_('Purchase requisition is already created!'))
                if partlist:
                    x.env['purchase.requisition'].create({
                        'line_ids': partlist,
                        'exclusive': 'multiple',
                        'origin': x.order_id.name,
                        'description': 'Demande de pièce pour la maintenece de la vehicule avec la matricul suivante '
                    })
        else:
            raise ValidationError('Purchase request is empty!')

    def assign_products_purchase(self):
        po = []
        for need_parts in self.spare_part_ids:
            if need_parts.product_stock_qty > 0:
                if need_parts.product_qty > need_parts.product_stock_qty:
                    po.append((0, 0, {'product_uom_id': 1,'product_id': need_parts.product_id.id,
                                          'product_qty': need_parts.product_qty - need_parts.product_stock_qty,'product_stock_qty': need_parts.product_id.qty_available}))
            if need_parts.product_stock_qty <= 0:
                po.append((0, 0, {'product_uom_id': 1,'product_id': need_parts.product_id.id, 'product_qty': need_parts.product_qty,
                                      'product_stock_qty': need_parts.product_id.qty_available}))
        return po

    @api.multi
    def compute_stock(self):
        self.clear_field()
        if(len(self.spare_part_ids) != 0):
            for rec in self:
                rec.spare_part_ids1=self.assign_products_purchase()
            return True
        else:
            raise ValidationError('Spare parts are empty!')

    #to clear field
    def clear_field(self):
        for rec in self:
            rec.write({'spare_part_ids1': [(5, 0, 0)]})

    def clear_field1(self):
        for rec in self:
            rec.write({'spare_part_ids': [(5, 0, 0)]})





