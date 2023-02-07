from odoo import api, fields, models


class CashFlowAnalytics(models.Model):
    _name = "cash.flow.analytics"
    _description = "Cash flow analytics model"

    date = fields.Date(string="Date")
    account_journal_id = fields.Many2one(comodel_name="account.journal", string="Bank", readonly=True, required=True)
    res_company_id = fields.Many2one(comodel_name="res.company", string="Company", readonly=True, required=True)
    opening_balance = fields.Float(string="Opening Balance", readonly=True, required=True)
    customer_id = fields.Many2one(comodel_name="res.partner", string="Customers", readonly=True)
    customer_amount = fields.Float(string="Customers:", readonly=True)
    vendor_id = fields.Many2one(comodel_name="res.partner", string="Vendors", readonly=True)
    vendor_amount = fields.Float(string="Vendors:", readonly=True)
    intercompany_in_id = fields.Many2one(comodel_name="res.partner", string="Intercompany IN", readonly=True)
    intercompany_in_amount = fields.Float(string="Intercompany IN:", readonly=True)
    intercompany_out_id = fields.Many2one(comodel_name="res.partner", string="Intercompany OUT", readonly=True)
    intercompany_out_amount = fields.Float(string="Intercompany OUT:", readonly=True)
    closing_balance = fields.Float(string="Closing Balance", compute="_compute_closing_balance", store=True, readonly=True)

    def generate_cash_flow_analitics(self, start_date, end_date):
        """Generate instances of cash.flow.analytics model and set amount, opening and close balance"""
        self.env["cash.flow.analytics"].search([]).unlink()
        account_payment_ids = self.env["account.payment"].search(
            [("payment_type", "!=", "transfer"), ("state", "not in", ["draft", "cancelled"]),
             ("payment_date", "<", fields.Date.today()), ("payment_date", ">=", start_date)])
        closing_balance = 0
        for account_payment_id in account_payment_ids.sorted("payment_date"):
            cash_flow_analytics_id = self._create_cash_flow_analytics(
                account_payment_id,
                account_payment_id.partner_type,
                closing_balance,
                account_payment_id.payment_date,
            )
            is_outbound_type = account_payment_id.payment_type == "outbound"
            outbound_amount = -account_payment_id.amount if is_outbound_type else account_payment_id.amount
            cash_flow_analytics_id.write({
                "customer_amount": outbound_amount if cash_flow_analytics_id.customer_id else 0,
                "vendor_amount": outbound_amount if cash_flow_analytics_id.vendor_id else 0,
                "intercompany_in_amount": account_payment_id.amount if cash_flow_analytics_id.intercompany_in_id else 0,
                "intercompany_out_amount": outbound_amount if cash_flow_analytics_id.intercompany_out_id else 0,
            })
            closing_balance = self.change_closing_balance(cash_flow_analytics_id)
        account_move_ids = self.env["account.move"].search(
            [("invoice_payment_state", "=", "not_paid"), ("state", "=", "posted"),
             ("actual_due_date", ">=", fields.Date.today()), ("actual_due_date", "<=", end_date)])
        for account_move_id in account_move_ids.sorted("actual_due_date"):
            cash_flow_analytics_id = self._create_cash_flow_analytics(
                account_move_id,
                account_move_id.type,
                closing_balance,
                account_move_id.actual_due_date,
            )
            amount = account_move_id.amount_total
            cash_flow_analytics_id.write({
                "customer_amount": amount if cash_flow_analytics_id.customer_id else 0,
                "vendor_amount": -amount if cash_flow_analytics_id.vendor_id else 0,
                "intercompany_in_amount": amount if cash_flow_analytics_id.intercompany_in_id else 0,
                "intercompany_out_amount": -amount if cash_flow_analytics_id.intercompany_out_id else 0,
            })
            closing_balance = self.change_closing_balance(cash_flow_analytics_id)

    def _create_cash_flow_analytics(self, account_data_id, type, closing_balance, date):
        """Create model cash.flow.analytics instance"""
        is_company = account_data_id.partner_id.id in self.env["res.company"].search([]).mapped("partner_id").ids
        partner_id = account_data_id.partner_id.id
        costomer_id = partner_id if not is_company and type in ["customer", "out_invoice"] else False
        vendor_id = partner_id if not is_company and type in ["supplier", "in_invoice"] else False
        intercompany_in_id = partner_id if is_company and type in ["customer", "out_invoice"] else False
        intercompany_out_id = partner_id if is_company and type in ["supplier", "in_invoice"] else False
        cash_flow_analytics_id = self.env["cash.flow.analytics"].create({
            "date": date,
            "account_journal_id": account_data_id.journal_id.id,
            "res_company_id": account_data_id.company_id.id,
            "opening_balance": closing_balance,
            "customer_id": costomer_id,
            "vendor_id": vendor_id,
            "intercompany_in_id": intercompany_in_id,
            "intercompany_out_id": intercompany_out_id,
        })
        return cash_flow_analytics_id

    def change_closing_balance(self, cash_flow_analytics_id):
        """Change closing_balance field according all current amount"""
        closing_balance = sum([
            cash_flow_analytics_id.customer_amount,
            cash_flow_analytics_id.vendor_amount,
            cash_flow_analytics_id.intercompany_in_amount,
            cash_flow_analytics_id.intercompany_out_amount,
            cash_flow_analytics_id.opening_balance,
        ])
        cash_flow_analytics_id.closing_balance = closing_balance
        return closing_balance

    @api.depends("opening_balance")
    def _compute_closing_balance(self):
        """Calculate closing_balance after changing opening_balance"""
        for cash_flow_analytics_id in self:
            self.change_closing_balance(cash_flow_analytics_id)
