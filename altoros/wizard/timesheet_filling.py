from odoo import models, fields, _, api
from odoo.exceptions import UserError


class TimesheetFilling(models.TransientModel):
    _name = "timesheet.filling"
    _description = "Timesheet filling"

    project_id = fields.Many2one(string="Project", comodel_name="project.project")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    select_billing_month = fields.Selection([
        ("1", "January"),
        ("2", "February"),
        ("3", "March"),
        ("4", "April"),
        ("5", "May"),
        ("6", "June"),
        ("7", "July"),
        ("8", "August"),
        ("9", "September"),
        ("10", "October"),
        ("11", "November"),
        ("12", "December"),
    ], string="Billing Month", required=True, readonly=False)

    @api.onchange("start_date", "end_date")
    def _onchange_date(self):
        """Gets billing_month """
        if self.start_date and self.end_date and self.start_date.month == self.end_date.month:
            self.select_billing_month = str(self.start_date.month)
        else:
            self.select_billing_month = ""

    def create_invoice(self):
        """Invoice creation and autofill timesheets"""
        if self.start_date > self.end_date:
            raise UserError(_("The start date cannot be greater than the end date"))
        project_task_ids = self.env["project.task"].search([("project_id", "=", self.project_id.id)])
        result = [(5, 0, 0)]
        for project_task_id in project_task_ids:
            timesheet_ids = project_task_id.timesheet_ids.filtered(
                lambda timesheet_id: timesheet_id.date >= self.start_date and timesheet_id.date <= self.end_date)
            if timesheet_ids:
                for timesheet_id in timesheet_ids:
                    rate_employee_id = self.env["rate.employee"].search(
                        [("project_id", "=", self.project_id.id), ("employee_id", "=", timesheet_id.employee_id.id),
                         ("start_date", "<=", timesheet_id.date), ("end_date", ">=", timesheet_id.date)])
                    result.append((0, 0, {"date": timesheet_id.date,
                                          "task_id": project_task_id.id,
                                          "employee_id": timesheet_id.employee_id.id,
                                          "description": timesheet_id.name,
                                          "unit_amount": timesheet_id.unit_amount,
                                          "department_id": timesheet_id.employee_id.department_id.id,
                                          "rate": rate_employee_id.rate,
                                          "sales_type": rate_employee_id.sales_type,
                                          }))
        invoice_id = self.env["account.move"].with_context(default_type="out_invoice").create(
            {"project_id": self.project_id.id,
             "start_date": self.start_date,
             "end_date": self.end_date,
             "billing_month": self.select_billing_month,
             "billing_year": self.start_date.year,
             "invoice_payment_term_id": self.project_id.partner_id.property_payment_term_id,
             "rate_employee_timesheet_ids": result})
        invoice_id.rate_employee_timesheet_ids._onchange_unit_amount_rate()
        invoice_id.onchange_rate_employee_timesheet_ids()
        return {
            "view_mode": "form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": invoice_id.id,

        }
