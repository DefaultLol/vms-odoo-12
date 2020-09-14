# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Vehicle Maintenance System',
    'version' : '1.0',
    'summary': 'Module to track maintenance of vehicles',
    'sequence': 15,
    'description': "description",
    'category': 'Maintenance',
    'depends' : [
        'mail',
        'account',
        'fleet',
        'hr',
        'purchase',
        'stock',
        'sale',
        'stock_operating_unit',
        'bsr_fleet_stock_analytic',
        'purchase_requisition'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/vms_release_order_view.xml',
        'views/vms_view.xml',
        'views/vms_report_view.xml',
        'views/vms_order_view.xml',
        'views/fleet_vehicule_view.xml',
        'views/hr_employee_view.xml',
        'views/vms_cycle_view.xml',
        'views/vms_program.xml',
        'views/vms_task.xml',
        'views/operating_unit_view.xml',
        'views/product_template_view.xml',
        'views/vms_order_line_view.xml',
        'views/stock_picking_view.xml',
        'views/fleet_vehicle_odometer_view.xml',
        'wizards/vms_wizard_maintenance_order_view.xml',
        'reports/report.xml',
        'reports/report_card.xml',
        'data/report_sequence.xml',
        'data/ir_sequence_data.xml',
        'data/stock_picking_type_data.xml',
        'data/cron_order.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}

