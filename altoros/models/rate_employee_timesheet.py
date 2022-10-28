from odoo import models, fields, api


class RateEmployeeTimesheet(models.Model):
    _name = "rate.employee.timesheet"
    _description = "Employee timesheets"
    _inherit = ["mail.thread"]

    date = fields.Date(string="Date", readonly=True)
    task_id = fields.Many2one(string="Task", comodel_name="project.task", readonly=True)
    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", readonly=True)
    description = fields.Char(string="Description task", readonly=True)
    unit_amount = fields.Float(string="Total hours", tracking=True)
    rate = fields.Float(string="Rate", tracking=True)
    total_value = fields.Float(string="Total value", tracking=True)
    department_id = fields.Many2one(string="Department", comodel_name="hr.department", tracking=True)
    account_move_id = fields.Many2one(string="Account move", comodel_name="account.move")
    comment = fields.Char(string="Comment", tracking=True)
    sales_type = fields.Selection(string="Sales type",
                                  selection=[("base", "Base"), ("upsale", "Upsale"), ("cross-sale", "Cross-sale")])

    @api.onchange("unit_amount", "rate")
    def _onchange_unit_amount_rate(self):
        """Autofill total_value field"""
        for rec in self:
            rec.total_value = rec.unit_amount * rec.rate

    def unlink(self):
        """Sends message to chatter if record unlinked"""
        for rec in self:
            rec._send_message_to_chatter()
        res = super().unlink()
        return res
