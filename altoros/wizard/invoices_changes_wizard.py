from odoo import models, fields, _
from odoo.exceptions import UserError


class InvoicesChangesWizard(models.TransientModel):
    _name = "invoices.changes.wizard"
    _description = "Invoices changes"

    start_date = fields.Date(string="Start date", required=True)
    end_date = fields.Date(string="End date", required=True)
    invoice_start_date = fields.Date(string="Invoice start date", required=True)
    invoice_end_date = fields.Date(string="Invoice end date", required=True)

    def create_report(self):
        """Report with invoices changes creation"""
        if self.start_date > self.end_date or self.invoice_start_date > self.invoice_end_date:
            raise UserError(_("The start date cannot be greater than the end date"))
        if (self.invoice_end_date - self.invoice_start_date).days > 31:
            raise UserError(_("The invoice creation period should be no more than one month"))
        invoice_ids = self.env["account.move"].search(
            [("write_date", ">=", self.start_date), ("invoice_date", ">=", self.invoice_start_date),
             ("invoice_date", "<=", self.invoice_end_date)])
        dates_to_report = {
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        return self.env.ref("altoros.invoices_changes_report_xlsx").report_action(invoice_ids, dates_to_report)
