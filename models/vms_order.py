from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsOrder(models.Model):
    _description = 'VMS Orders'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'vms.order'

    name = fields.Char(string='Order Number', readonly=True)
    operating_unit_id = fields.Many2one(
        'operating.unit', string='Base', required=True)
    supervisor_id = fields.Many2one(
        'hr.employee',
        string='Supervisor',
        domain=[('mechanic', '=', True)],)
    date = fields.Datetime(
        required=True,
        default=fields.Datetime.now)
    current_odometer = fields.Float()
    type = fields.Selection(
        [('preventive', 'Preventive'),
         ('corrective', 'Corrective')],
        required=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        readonly=True,
        default=lambda self: self._default_warehouse_id(),)
    start_date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        string='Schedule start')
    end_date = fields.Datetime(
        #required=True,
        # compute='_compute_end_date',
        string='Schedule end'
    )
    start_date_real = fields.Datetime(
        readonly=True,
        string='Real start date')
    end_date_real = fields.Datetime(
        # compute="_compute_end_date_real",
        readonly=True,
        string='Real end date'
    )
    order_line_ids = fields.One2many(
        'vms.order.line',
        'order_id',
        string='Order Lines',
    )
    program_id = fields.Many2one(
        'vms.program',
        string='Program')
    report_ids = fields.Many2many(
        'vms.report',
        string='Report(s)')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('released', 'Released'),
         ('cancel', 'Cancel')],
        readonly=True,
        default='draft')
    unit_id = fields.Many2one(
        'fleet.vehicle',
        string='Unit', required=True, store=True)
    cycle_types=fields.Many2many('vms.cycle',string='Cycle Types')

    @api.onchange('program_id')
    def change_program(self):
        self.order_line_ids=False
        for cycle in self.program_id.cycle_ids:
            for task in cycle.task_ids:
                data=[]
                for parts in task.spare_part_ids:
                    print(parts.id)
                    data.append(parts.id)
                print(task.id)
                spare = self.order_line_ids.new({
                    'task_id': task.id,
                    'duration': task.duration,
                    'state':'draft',
                    'start_date':fields.Datetime.now(),
                    'spare_part_ids':[(6,None,[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19])]
                })
                self.order_line_ids += spare

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search(
            [('company_id', '=', company)], limit=1)
        return warehouse_ids

    @api.model
    def create(self, values):
        res = super(VmsOrder, self).create(values)
        if res.operating_unit_id.order_sequence_id:
            sequence = res.operating_unit_id.order_sequence_id
            res.name = sequence.next_by_id()
        else:
            raise ValidationError(_(
                'Verify that the sequences in the base are assigned'))
        return res

    @api.depends('order_line_ids')
    def _compute_end_date_real(self):
        for rec in self:
            if rec.start_date_real:
                sum_time = 0.0
                for line in rec.order_line_ids:
                    if line.state == 'done':
                        sum_time += line.real_duration
                strp_date = datetime.strptime(
                    str(rec.start_date_real), "%Y-%m-%d %H:%M:%S")
                rec.end_date_real = strp_date + timedelta(hours=sum_time)

    @api.multi
    def action_released(self):
        for order in self:
            for line in order.order_line_ids:
                line.action_done()
            # if order.type == 'preventive':
                # Preguntar que tenemos que hacer ahora.
            if order.type == 'corrective':
                for report in order.report_ids:
                    report.state = 'closed'
            order.state = 'released'

    @api.multi
    @api.onchange('type', 'unit_id')
    def _onchange_type(self):
        for rec in self:
            if rec.type == 'preventive':
                rec.program_id = rec.unit_id.program_id
                rec.current_odometer = rec.unit_id.odometer
                rec.order_line_ids = False
            else:
                rec.program_id = False
                rec.current_odometer = False
                rec.sequence = False
                rec.order_line_ids = False

    # @api.depends('order_line_ids')
    # def _compute_end_date(self):
    #     for rec in self:
    #         sum_time = 0.0
    #         if rec.start_date:
    #             for line in rec.order_line_ids:
    #                 sum_time += line.duration
    #             strp_date = datetime.strptime(
    #                 rec.start_date, "%Y-%m-%d %H:%M:%S")
    #             rec.end_date = strp_date + timedelta(hours=sum_time)
    #
    @api.multi
    def action_open(self):
        for rec in self:
            #check if there is an order sticked to the vehicle already and the order is open
            orders = self.search_count([
                ('unit_id', '=', rec.unit_id.id), ('state', '=', 'open'),
                ('id', '!=', rec.id)])
            if orders > 0:
                raise ValidationError(_(
                    'Unit not available for maintenance because it has more '
                    'open order(s).'))
            if not rec.order_line_ids:
                raise ValidationError(_(
                    'The order must have at least one task'))
            rec.state = 'open'
            if rec.type == 'corrective':
                rec.report_ids.write({'state': 'pending'})
            rec.order_line_ids.action_process(self.unit_id)
            rec.start_date_real = fields.Datetime.now()
    #
    # @api.multi
    # def action_cancel(self):
    #     for rec in self:
    #         rec.order_line_ids.action_cancel()
    #         if rec.type == 'corrective':
    #             for report in rec.report_ids:
    #                 report.state = 'cancel'
    #         rec.state = 'cancel'
    #
    # @api.multi
    # def action_cancel_draft(self):
    #     for rec in self:
    #         rec.state = 'draft'
    #         if rec.type == 'corrective':
    #             for report in rec.report_ids:
    #                 report.state = 'draft'
    #         for line in rec.order_line_ids:
    #             line.state = 'draft'
    #             for spare in line.spare_part_ids:
    #                 spare.state = 'draft'
    #
    @api.multi
    def print_mo(self):
        return self.env['report'].get_action(self, 'vms.report_order')

    # This method will be executed by the planned action to create new order
    @api.model
    def create_order(self):
        vehicles=self.env['fleet.vehicle'].search([])
        cycles=self.env['vms.cycle'].search([],order="frequency asc")
        print('first')
        print(cycles)
        possible_cycles=[]
        choosen_cycles=[]
        k=0
        for vehicle in vehicles:
            #take orders corresponding to the vehicle which are not released
            order = self.env['vms.order'].search([
                ('unit_id', '=',vehicle.id),
                ('state','!=','released')
            ])
            #if order exist stop
            if(order):
                #go to next
                print('order already exist')
                continue
            else:
                print('Vehicle: {}'.format(vehicle.name))
                #current odometer of vehicle
                veh_odometer=vehicle.odometer
                for cycle in cycles:
                    if(veh_odometer >= cycle.frequency):
                        possible_cycles.append(cycle)
                        print(cycle.name)
                choosen_cycles = self.get_final_choosen_cyle(possible_cycles,vehicle)
                print('choooooooosen')
                print(choosen_cycles)
                if(len(choosen_cycles) != 0):
                    self.order_creation(vehicle,choosen_cycles)
                else:
                    print('do nothing')

    def order_creation(self,vehicle,cycles):
        if len(cycles)!=0:
            tasks=self.create_task_list(cycles)
            cycle=self.create_cycle_list(cycles)
            self.env['vms.order'].create({
                'operating_unit_id':self.env['operating.unit'].search([])[0].id,
                'unit_id':vehicle.id,
                'type':'preventive',
                'supervisor_id':self.env['hr.employee'].search([])[0].id,
                'current_odometer':vehicle.odometer,
                'order_line_ids':tasks,
                'cycle_types':cycle
            })
            template_id = self.env.ref('vms.email_template_order_creation').id
            email_values = {'key': u'value'}
            self.env['mail.template'].browse(template_id).with_context(email_values).send_mail(self.id, force_send=True)
        else:
            print('can\'t create')

    def create_task_list(self,cycles):
        data=[]
        for cycle in cycles:
            for task in cycle.task_ids:
                data.append((0,0,{
                    'task_id':task.id,
                    'duration':task.duration
                }))
        return data

    def create_cycle_list(self,cycles):
        data=[]
        for cycle in cycles:
            data.append((4,cycle.id))
        return data

    # This method check if in out choosen array is their cycle with the same type and just leave only one type of cycle
    def check_cycle_type(self,cycle,current_cycle):
        #chec if current cycle should stay in array of cycle or not
        stay=True
        for rec in cycle:
            if(rec != current_cycle):
                if rec.type == current_cycle.type:
                    if current_cycle.frequency < rec.frequency:
                        stay=False
        return stay

    # Get array of choosen cycles
    def get_final_choosen_cyle(self,possible_cycles,vehicle):
        print('final')
        choosen_cycles=[]
        for rec in possible_cycles:
            stay=self.check_cycle_type(possible_cycles,rec)
            if stay:
                print(rec.name)
                choosen_cycles.append(rec)
        choosen_cycles=self.check_odometer_history(vehicle,choosen_cycles)
        print(choosen_cycles)
        if choosen_cycles==None:
            return []
        return choosen_cycles

    def check_odometer_history(self,vehicle,cycles):
        choosen_cycles=[]
        exist=False
        # get odometer history log of the vehicle which type is maintenance with descending order
        odometer_log = self.env['fleet.vehicle.odometer'].search([
            ('vehicle_id', '=', vehicle.id),
            ('type', '=', 'maintenance')
        ])
        if len(odometer_log) != 0:
            for cycle in cycles:
                for rec in odometer_log:
                    if cycle in rec.order_id.cycle_types:
                        exist=True
                if not exist:
                    choosen_cycles.append(cycle)
            return choosen_cycles
        else:
            return cycles

    def send_mail(self):
        template_id=self.env.ref('vms.email_template_order_creation').id
        self.env['mail.template'].browse(template_id).send_mail(self.id,force_send=True)







