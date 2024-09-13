from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProjectEmployeeAssign(models.Model):
    _name = "project.employee.assign"
    _description = "Project Employee Assign"

    project_code = fields.Many2one("project.master", required=True, help='Unique Key', index=True, context={'show_name': True})
    employee_code = fields.Many2one("employee.master", required=True, help='Unique ', index=True, context={'show_name': True})
    year = fields.Many2one("year.master", required=True, help='Unique Key', index=True)
    month = fields.Many2one("month.master", required=True, help='Unique Key', index=True)
    op_hours_planned = fields.Float(required=True)
    op_hours_actual = fields.Float(required=True)

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
        return res

    def write(self, vals):
        res = super(ProjectEmployeeAssign, self).write(vals)
        self._update_project_list_hours()
        return res

    def _update_project_list_hours(self):
        _logger.info(f"Updating project list hours for project: {self.project_code.id}")
        project_list_records = self.env['project.list'].search([('project_code', '=', self.project_code.id)])
        for project in project_list_records:
            _logger.info(f"Recomputing OP hours for project {project.project_code}")
            project._compute_op_hours()


 