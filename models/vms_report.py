from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VmsReport(models.Model):
    _description = 'VMS Reports'
    _name = 'vms.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Number', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date = fields.Datetime(required=True, default=fields.Datetime.now)
    operating_unit_id = fields.Many2one(
        'operating.unit', string='Base', required=True)
    unit_id = fields.Many2one(
        'fleet.vehicle',
        required=True,
        string='Unit')
    order_id = fields.Many2one(
        'vms.order',
        readonly=True,
        string='Order')
    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        string='Driver')
    kilometre_actuel=fields.Float(string='Kilometrage actuel')
    kilometre_new=fields.Float(string='Nouveau kilometrage')
    kilometre_diff=fields.Float(string='Kilometrage parcouru',default=lambda self: self.kilometre_new-self.kilometre_actuel)
    end_date = fields.Datetime()
    state = fields.Selection(
        [('pending', 'Pending'),
         ('closed', 'Closed'),
         ('cancel', 'Cancel')],
        default='pending')
    notes = fields.Html()

    # @api.depends('kilometre_new')
    # def set_kilometre_diff(self):
    #     for rec in self:
    #         rec.kilometre_diff=rec.kilometre_new-rec.kilometre_actuel


    @api.onchange('unit_id')
    def check_age(self):
        if self.unit_id:
            self.kilometre_actuel=self.unit_id.odometer
            self.kilometre_new = self.unit_id.odometer

    @api.onchange('kilometre_new')
    def check_kilometre(self):
        if(self.kilometre_new):
            if((self.kilometre_new - self.kilometre_actuel) < 0):
                self.kilometre_diff=0
                self.kilometre_new = self.unit_id.odometer
                return {
                    'warning': {
                        'title': "Error",
                        'message': "Kilometre new should not be inferior",
                    }
                }
            else:
                self.kilometre_diff=self.kilometre_new-self.kilometre_actuel

    # @api.constrains('kilometre_new')
    # def kilometre_negative(self):
    #     if(self.kilometre_new < 0):
    #         raise ValidationError(_(
    #             'Negative new kilometre !'))


    @api.model
    def create(self, values):
        self._cr.execute(
            "UPDATE fleet_vehicle_odometer SET value={} WHERE vehicle_id={} ".format(values['kilometre_new'],values['unit_id']))
        res = super(VmsReport, self).create(values)
        if res.operating_unit_id.report_sequence_id:
            sequence = res.operating_unit_id.report_sequence_id
            res.name = sequence.next_by_id()
        else:
            raise ValidationError(_(
                'Verify that the sequences in the base are assigned'))
        return res

    # @api.model
    # def create(self, values):
    #     if(values.get('name',_('New')) == _('New')):
    #         values['name']=self.env['ir.sequence'].next_by_code('vms.sequence') or _('New')
    #     res = super(VmsReport, self).create(values)
    #     return res

    # vehicles = self.env['fleet.vehicle'].search([('name', '=', self.unit_id.name)])
    # vehicles.write({
    #     'odometer':self.unit_id.odometer
    # })

    def action_confirmed(self):
        for rec in self:
            rec.state = 'closed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_pending(self):
        for rec in self:
            rec.state = 'pending'