from odoo import fields, models


class EditOpeningBalance(models.TransientModel):
    _name = "edit.opening.balance"
    _description = "Edit opening balance"

    date = fields.Date(string="Date", required=True)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Bank", required=True)
    balance = fields.Float(string="Balance", required=True)

    def recalculate_opening_balance(self):
        """Recalculate opening_balance field for cash.flow.analytics of selected date and journal_id"""
        cash_flow_analytics_ids = self.env["cash.flow.analytics"].search([
            ("date", ">=", self.date),
            ("account_journal_id", "=", self.journal_id.id)
        ])
        if cash_flow_analytics_ids:
            closed_balance = self.balance
            for cash_flow_id in cash_flow_analytics_ids:
                cash_flow_id.opening_balance = closed_balance
                closed_balance = self.env["cash.flow.analytics"].change_closing_balance(cash_flow_id)
