from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class GenerateCashFlowAnalytics(models.TransientModel):
    _name = "generate.cash.flow.analytics"
    _description = "Period selection to generate cash flow analytics"

    start_date = fields.Date(string="Start date", required=True)
    end_date = fields.Date(string="End date", required=True)
    forecast_type = fields.Selection(selection=[("real", "Real data"), ("predicted", "Predicted data")],
                                     string="Type of forecast", required=True, default="real")
    analysis_period = fields.Integer(string="Data analysis period, days", default="30")
    number_recent_payment = fields.Integer(string="Number of recent payments", default="3")

    def generate_cash_flow_analytics(self):
        """Selection period to generate cash flow analytics"""
        if self.start_date > self.end_date:
            raise UserError(_("The start date cannot be greater than the end date"))
        if not self.analysis_period or not self.number_recent_payment:
            raise UserError(_("Check analysis period and number of recent payments"))
        if self.forecast_type == "real":
            self.env["cash.flow.analytics"].generate_real_cash_flow_analitics(self.start_date, self.end_date)
        else:
            self.env["cash.flow.analytics"].generate_predicted_cash_flow_analitics(self.start_date, self.end_date,
                                                                                   self.analysis_period,
                                                                                   self.number_recent_payment)
