from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    x_studio_assigned_employee = fields.Many2one(string="Assigned employee (Old)", comodel_name="hr.employee")
