from odoo import models, fields, _
from odoo.exceptions import UserError


class InvoicesChangesWizard(models.TransientModel):
    _name = "invoice.selection.wizard"
    _description = "Invoice selection wizard"

    start_date = fields.Date(string="Start date", required=True)
    end_date = fields.Date(string="End date", required=True)

    def create_report(self):
        """Checking that the dates are correct and creating timesheets report"""
        if self.start_date > self.end_date:
            raise UserError(_("The start date cannot be greater than the end date"))
        invoice_ids = self.env["account.move"].search([
            ("create_date", ">=", self.start_date), ("create_date", ">=", self.start_date), ("state", "=", "posted")])
        dates_to_report = {
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        return self.env.ref("altoros.invoice_timesheets_report_xlsx").report_action(invoice_ids, dates_to_report)
