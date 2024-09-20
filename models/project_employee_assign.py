from odoo import models, fields, api

class ProjectEmployeeAssign(models.Model):
    _name = "project.employee.assign"
    _description = "Project Employee Assign"

    project_code = fields.Many2one("project.master", required=True, help='Unique Key', index=True, context={'show_name': True})
    employee_code = fields.Many2one("employee.master", required=True, help='Unique ', index=True, context={'show_name': True})
    year = fields.Many2one("year.master", required=True, help='Unique Key', index=True)
    month = fields.Many2one("month.master", required=True, help='Unique Key', index=True)
    op_hours_planned = fields.Float(required=True)
    op_hours_actual = fields.Float(required=True)
    planned_cost = fields.Float(string='Planned Cost', compute='_compute_costs', store=True)
    actual_cost = fields.Float(string='Actual Cost', compute='_compute_costs', store=True)

    _sql_constraints = [
        ('unique_project_employee_year_month', 'UNIQUE(project_code, employee_code, year, month)', 'The combination of project code, employee code, year, and month must be unique.')
    ]

    @api.model
    def create(self, vals):
        record = super(ProjectEmployeeAssign, self).create(vals)

        existing_assignment = self.env['project.employee.assign.per.month'].search([
            ('project_code', '=', record.project_code.id),
            ('employee_code', '=', record.employee_code.id)
        ], limit=1)

        if not existing_assignment:
            month_field = f'month_{str(record.month.month).zfill(2)}'

            self.env['project.employee.assign.per.month'].create({
                'project_code': record.project_code.id,
                'employee_code': record.employee_code.id,
                month_field: record.op_hours_actual,
            })
        return record
    
    @api.model
    def create(self, vals):
        res = super(ProjectEmployeeAssign, self).create(vals)
        res._update_project_list_hours()
        res._update_project_list_costs()  
        return res

    def write(self, vals):
        res = super(ProjectEmployeeAssign, self).write(vals)
        self._update_project_list_hours()
        self._update_project_list_costs() 
        return res

    def _update_project_list_hours(self):
        project_list_records = self.env['project.list'].search([('project_code', '=', self.project_code.id)])
        for project in project_list_records:
            project._compute_op_hours()

    def _update_project_list_costs(self):
        project_list_records = self.env['project.list'].search([('project_code', '=', self.project_code.id)])
        for project in project_list_records:
            project._compute_costs()  

    # compute actual cost
    @api.depends('employee_code', 'op_hours_planned', 'op_hours_actual')
    def _compute_costs(self):
        for record in self:
            if record.employee_code and record.employee_code.class_code:
                unit_price = record.employee_code.class_code.unit_price
                
                record.planned_cost = unit_price * record.op_hours_planned if unit_price else 0.0
                
                record.actual_cost = unit_price * record.op_hours_actual if unit_price else 0.0
            else:
                record.planned_cost = 0.0
                record.actual_cost = 0.0
 