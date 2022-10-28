from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class RateEmployee(models.Model):
    _name = "rate.employee"
    _description = "Employee rate"
    _inherit = ["mail.thread"]

    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", required=True)
    project_id = fields.Many2one(string="Project", comodel_name="project.project", required=True)
    start_date = fields.Date(string="Start date", required=True)
    end_date = fields.Date(string="End date", required=True)
    rate = fields.Float(string="Rate")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")
    sales_type = fields.Selection(string="Sales type", selection=[("base", "Base"), ("upsale", "Upsale"), ("cross-sale", "Cross-sale")])

    @api.model
    def create(self, vals):
        """Validate date"""
        self.validate_data(vals)
        result = super(RateEmployee, self).create(vals)
        return result

    def write(self, vals):
        """Validate date"""
        self.validate_data(vals)
        res = super(RateEmployee, self).write(vals)
        return res

    def validate_data(self, vals):
        """Date validate"""
        start_date = datetime.strptime(vals.get("start_date"), "%Y-%m-%d").date() or self.start_date
        end_date = datetime.strptime(vals.get("end_date"), "%Y-%m-%d").date() or self.end_date
        if start_date > end_date:
            raise UserError(_("The start date cannot be greater than the end date"))
        actual_currency_id = self.env["rate.employee"].search([("project_id", "=", vals.get("project_id"))],
                                                              limit=1).currency_id.id
        if vals.get("currency_id") != actual_currency_id and actual_currency_id:
            raise UserError(_("The value of the currency field must be the same for one project"))
        rate_employee_ids = self.env["rate.employee"].search(
            [("employee_id", "=", vals.get("employee_id") or self.employee_id.id),
             ("project_id", "=", vals.get("project_id") or self.project_id.id)]) - self
        if rate_employee_ids:
            for rec_employee_id in rate_employee_ids:
                if (start_date >= rec_employee_id.start_date and start_date <= rec_employee_id.end_date) or (
                        end_date >= rec_employee_id.start_date and end_date <= rec_employee_id.end_date) or (
                        start_date < rec_employee_id.start_date and end_date > rec_employee_id.end_date):
                    raise UserError(_("The values of the time ranges should not overlap with each other"))
