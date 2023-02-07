from odoo import fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError


class GenerateCashFlowAnalytics(models.TransientModel):
    _name = "generate.cash.flow.analytics"
    _description = "Period selection to generate cash flow analytics"

    start_date = fields.Date(string="Start date", required=True)
    end_date = fields.Date(string="End date", required=True)

    def generate_cash_flow_analytics(self):
        """Selection period to generate cash flow analytics"""
        if self.start_date > self.end_date:
            raise UserError(_("The start date cannot be greater than the end date"))
        self.env["cash.flow.analytics"].generate_cash_flow_analitics(self.start_date, self.end_date)
