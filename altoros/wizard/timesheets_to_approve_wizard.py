from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import datetime


class TimesheetsToApproveWizard(models.TransientModel):
    _name = "timesheets.to.approve.wizard"
    _description = "Timesheets to approve"

    start_date = fields.Date(string="Start date", required=True)
    end_date = fields.Date(string="End date", required=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department", required=True)

    def create_report(self):
        """Report with invoices changes creation"""
        if self.start_date > self.end_date:
            raise UserError(_("The start date cannot be greater than the end date"))
        self._cr.execute(""" SELECT id FROM project_task as pt
                             WHERE pt.id IN (
                                             SELECT task_id FROM account_analytic_line AS aal
                                             WHERE (aal.date between %s and %s) AND aal.employee_id IN (
                                                    SELECT id FROM hr_employee AS he 
                                                    WHERE he.department_id = %s
                                                    )
                                             )""", (self.start_date, self.end_date, self.department_id.id))
        project_task_tupples = self._cr.fetchall()
        project_task_list = [project_task_tupple[0] for project_task_tupple in project_task_tupples] if project_task_tupples else []

        data_to_report = {
            "report_name": f"{self.department_id.name} {self.start_date} - {self.end_date}",
            "start_date": self.start_date,
            "end_date": self.end_date,
            "department": self.department_id.name,
        }
        return self.env.ref("altoros.timesheets_to_approve_report_xlsx").report_action(docids=project_task_list, data=data_to_report)
