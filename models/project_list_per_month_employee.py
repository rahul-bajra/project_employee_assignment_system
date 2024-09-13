from odoo import models, fields, api

class ProjectListPerMonthEmployee(models.Model):
    _name = 'project.list.per.month.employee'
    _description = 'Project List Per Month Employee'

    project_code = fields.Many2one('project.master', string='Project Code', required=True, help='Reference to the Project Master')
    month = fields.Many2one("month.master", required=True, help='Unique Key', index=True)
    employee_code = fields.Many2one("employee.master", help='Unique Key', index=True, context={'show_name': True})
    employee_assignment_id = fields.Many2one('project.employee.assign', string='Employee Assignment')
    op_hours_planned = fields.Float(related='employee_assignment_id.op_hours_planned', string='OP Planned Hours')
    op_hours_actual = fields.Float(related='employee_assignment_id.op_hours_actual', string='OP Actual Hours')
    planned_cost = fields.Float(related='employee_assignment_id.planned_cost', compute='_compute_costs', store=True)
    actual_cost = fields.Float(related='employee_assignment_id.actual_cost', compute='_compute_costs', store=True)

