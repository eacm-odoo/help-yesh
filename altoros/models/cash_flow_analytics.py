from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models


class CashFlowAnalytics(models.Model):
    _name = "cash.flow.analytics"
    _description = "Cash flow analytics model"

    date = fields.Date(string="Date")
    account_journal_id = fields.Many2one(comodel_name="account.journal", string="Bank", readonly=True, required=True)
    res_company_id = fields.Many2one(comodel_name="res.company", string="Company", readonly=True, required=True)
    opening_balance = fields.Float(string="Opening Balance", readonly=True)
    customer_id = fields.Many2one(comodel_name="res.partner", string="Customers", readonly=True)
    customer_amount = fields.Float(string="Customers:", readonly=True)
    vendor_id = fields.Many2one(comodel_name="res.partner", string="Vendors", readonly=True)
    vendor_amount = fields.Float(string="Vendors:", readonly=True)
    intercompany_in_id = fields.Many2one(comodel_name="res.partner", string="Intercompany IN", readonly=True)
    intercompany_in_amount = fields.Float(string="Intercompany IN:", readonly=True)
    intercompany_out_id = fields.Many2one(comodel_name="res.partner", string="Intercompany OUT", readonly=True)
    intercompany_out_amount = fields.Float(string="Intercompany OUT:", readonly=True)
    closing_balance = fields.Float(string="Closing Balance", compute="_compute_closing_balance", store=True,
                                   readonly=True)

    def generate_real_cash_flow_analitics(self, start_date, end_date):
        """Generate instances of cash.flow.analytics model for real period and set amount, opening and close balance"""
        self.env["cash.flow.analytics"].search([]).unlink()
        last_date = end_date
        account_payment_ids = self.env["account.payment"].search(
            [("payment_type", "!=", "transfer"), ("state", "not in", ["draft", "cancelled"]),
             ("payment_date", "<", fields.Date.today()), ("payment_date", ">=", start_date)]).sorted("payment_date")
        closing_balance = 0
        for account_payment_id in account_payment_ids:
            cash_flow_analytics_id = self._create_real_cash_flow_analytics(
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
            last_date = account_payment_id.payment_date
        account_move_ids = self.env["account.move"].search(
            [("invoice_payment_state", "=", "not_paid"), ("state", "=", "posted"),
             ("actual_due_date", ">=", fields.Date.today()), ("actual_due_date", "<=", end_date)]).sorted(
            "actual_due_date")
        for account_move_id in account_move_ids:
            cash_flow_analytics_id = self._create_real_cash_flow_analytics(
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
            last_date = account_move_id.actual_due_date
        return last_date, closing_balance

    def _create_real_cash_flow_analytics(self, account_data_id, type, closing_balance, date):
        """Create model cash.flow.analytics real instance"""
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

    def generate_predicted_cash_flow_analitics(self, start_date, end_date, analysis_period, number_payment):
        """Generate instances of cash.flow.analytics model for predicted period and set amount, opening and close balance"""
        last_cash_flow_date, opening_balance = self.generate_real_cash_flow_analitics(start_date, end_date)
        if last_cash_flow_date < end_date:
            cash_flow_object = self.env["cash.flow.analytics"]
            partner_list = [("customer_id", "customer_amount"), ("vendor_id", "vendor_amount"),
                            ("intercompany_in_id", "intercompany_in_amount"),
                            ("intercompany_out_id", "intercompany_out_amount")]
            for partner, amount in partner_list:
                cash_flow_analytics_ids = self.env["cash.flow.analytics"].search([(partner, "!=", False)])
                if len(cash_flow_analytics_ids) > 1:
                    cash_flow_combination = [(getattr(cash_flow_id, partner, False), cash_flow_id.account_journal_id)
                                             for cash_flow_id in cash_flow_analytics_ids]
                    compiled_combination = defaultdict(int)
                    for comb in cash_flow_combination:
                        compiled_combination[comb] += 1
                    for key, value in compiled_combination.items():
                        partner_id = key[0].id
                        journal_id = key[1].id
                        if value > 1:
                            partner_cash_flow_object = self.env["cash.flow.analytics"]
                            last_cash_flow_ids = self.env["cash.flow.analytics"].search(
                                [(partner, "=", partner_id), ("account_journal_id", "=", journal_id)])[-2::]
                            date_range = self.get_date_range(partner, key[0].account_payment_term, last_cash_flow_ids)
                            company_id = last_cash_flow_ids[-1].res_company_id.id
                            first_predicted_date = last_cash_flow_date + date_range
                            while first_predicted_date < end_date:
                                cash_flow_id = self._create_predicted_cash_flow_analytics(first_predicted_date,
                                                                                          journal_id, company_id,
                                                                                          partner, partner_id)
                                partner_cash_flow_object += cash_flow_id
                                first_predicted_date += date_range
                            cash_flow_object += partner_cash_flow_object
                            self._set_cash_flow_amount(partner_cash_flow_object, amount, partner_id, journal_id,
                                                       analysis_period, number_payment)
            self._set_cash_flow_opening_close_balance(cash_flow_object, opening_balance)

    def _set_cash_flow_opening_close_balance(self, cash_flow_ids, opening_balance):
        """Set cash flow opening_balance according recent cash_flow_analytics"""
        for cash_flow_id in cash_flow_ids:
            cash_flow_id.opening_balance = opening_balance
            opening_balance = self.change_closing_balance(cash_flow_id)

    def _create_predicted_cash_flow_analytics(self, first_predicted_date, journal_id, company_id, partner, partner_id):
        """Create model cash.flow.analytics predicted instance"""
        cash_flow_id = self.env["cash.flow.analytics"].create({
            "date": first_predicted_date,
            "account_journal_id": journal_id,
            "res_company_id": company_id,
        })
        setattr(cash_flow_id, partner, partner_id)
        return cash_flow_id

    def _set_cash_flow_amount(self, cash_flow_ids, amount_type, partner_id, journal_id, period, payment_number):
        """Set cash flow amount according recent account_payment"""
        recent_date = fields.Date.today() - timedelta(days=period)
        account_payment_ids = self.env["account.payment"].search(
            [("payment_type", "!=", "transfer"), ("state", "in", ["posted", "reconciled"]),
             ("journal_id", "=", journal_id), ("partner_id", "=", partner_id),
             ("payment_date", ">=", recent_date)])
        if account_payment_ids:
            amount_list = account_payment_ids[-payment_number::].mapped("amount")
            for cash_flow_id in cash_flow_ids:
                amount = sum(amount_list) / len(amount_list)
                setattr(cash_flow_id, amount_type, amount)
                amount_list.append(amount)
                amount_list.pop(0)

    @staticmethod
    def get_date_range(partner, payment_term, cash_flow_ids):
        """Calculate date_range for cash_flow_analytics model"""
        if partner in ["customer_id", "vendor_id"] and payment_term:
            date_range = timedelta(days=payment_term)
        else:
            date_time = cash_flow_ids[1].date - cash_flow_ids[0].date
            date_range = date_time if date_time < timedelta(days=1) else timedelta(days=1)
        return date_range
