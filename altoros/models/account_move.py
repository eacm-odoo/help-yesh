import logging
from datetime import date
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    project_id = fields.Many2one(string="Project", comodel_name="project.project")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    rate_employee_timesheet_ids = fields.One2many(string="Employee timesheets", comodel_name="rate.employee.timesheet",
                                                  inverse_name="account_move_id")
    department_rate_ids = fields.One2many(string="Department rate", comodel_name="department.rate",
                                          inverse_name="account_move_id", )
    total_price = fields.Float(string="Total price", compute="_compute_total_price", store=True)

    split_revenue = fields.Boolean(string="Split revenue by Department?")
    sales_type = fields.Selection(selection=[("Current", "Current"), ("New", "New")], string="Current/New")
    sales_type_revenue = fields.Char(string="Revenue Current/New")
    billing_month = fields.Selection([
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
    ], string="Billing Month")
    billing_year = fields.Char(string="Billing year")
    project_owner = fields.Selection(string="Project Owner BL", related="project_id.project_owner", store=True)
    invoice_date = fields.Date(string="Invoice/Bill Date", default=fields.Date.today)
    track_all_fields = fields.Boolean(string="Track all fields", default=True)
    total_with_discount = fields.Float(string="Total with discount", compute="_compute_with_discount", store=True)
    sales_type_revenue_ids = fields.One2many(string="Sales type revenue", comodel_name="sales.type.revenue",
                                             inverse_name="account_move_id", compute="_compute_sales_type_revenue_ids",
                                             store=True)
    sales_type_departments_ids = fields.One2many(string="Sales type by departments",
                                                 comodel_name="sales.type.departments",
                                                 inverse_name="account_move_id",
                                                 compute="_compute_sales_type_departments_ids",
                                                 store=True)
    # fields to match with the studio module
    x_studio_billing_month = fields.Selection(selection=[
        ("January", "January"),
        ("February", "February"),
        ("March", "March"),
        ("April", "April"),
        ("May", "May"),
        ("June", "June"),
        ("July", "July"),
        ("August", "August"),
        ("September", "September"),
        ("October", "October"),
        ("November", "November"),
        ("December", "December"),
    ], string="Billing month OLD")
    x_studio_billing_year = fields.Selection(selection=[
        ("2019", "2019"),
        ("2020", "2020"),
        ("2021", "2021"),
        ("2022", "2022"),
        ("2023", "2023"),
        ("2024", "2024"),
        ("2025", "2025"),
    ], string="Billing year OLD")
    x_studio_customer_project = fields.Char(string="Customer project OLD")
    x_studio_project = fields.Char(string="Additional project OLD")
    x_studio_project_owner_bl = fields.Selection([
        ("Dedicated Teams", "Dedicated Teams"),
        ("Cloud Foundry", "Cloud Foundry"),
        ("Protofire", "Protofire"),
    ], string="Project owner BL OLD")
    x_studio_licence_ = fields.Char(string="Licence # OLD")
    x_studio_department_1_1 = fields.Selection(selection=[
        (".NET Development", ".NET Development"),
        ("Quality Assurance", "Quality Assurance"),
        ("Front-end Development", "Front-end Development"),
        ("Java Development", "Java Development"),
        ("Mobile Development", "Mobile Development"),
        ("Ruby Development", "Ruby Development"),
        ("Argentina Labs", "Argentina Labs"),
        ("CF Minsk", "CF Minsk"),
        ("CF US", "CF US"),
        ("Blockchain Start-ups", "Blockchain Start-ups"),
        ("Insurance on Tokens", "Insurance on Tokens"),
        ("EBC", "EBC"),
        ("ML/Al", "ML/Al"),
        ("IT Infrastructure", "IT Infrastructure"),
        ("MLBL_Robot", "MLBL_Robot"),
        ("MLBL_Camera", "MLBL_Camera"),
        ("MLBL_Camera_Hardware", "MLBL_Camera_Hardware"),
    ], string="Department 1 OLD")
    x_studio_department_2 = fields.Selection(selection=[
        (".NET Development", ".NET Development"),
        ("Quality Assurance", "Quality Assurance"),
        ("Front-end Development", "Front-end Development"),
        ("Java Development", "Java Development"),
        ("Mobile Development", "Mobile Development"),
        ("Ruby Development", "Ruby Development"),
        ("Argentina Labs", "Argentina Labs"),
        ("CF Minsk", "CF Minsk"),
        ("CF US", "CF US"),
        ("Blockchain Start-ups", "Blockchain Start-ups"),
        ("Insurance on Tokens", "Insurance on Tokens"),
        ("EBC", "EBC"),
        ("ML/Al", "ML/Al"),
        ("IT Infrastructure", "IT Infrastructure"),
        ("MLBL_Robot", "MLBL_Robot"),
        ("MLBL_Camera", "MLBL_Camera"),
        ("MLBL_Camera_Hardware", "MLBL_Camera_Hardware"),
    ], string="Department 2 OLD")
    x_studio_department_3 = fields.Selection(selection=[
        (".NET Development", ".NET Development"),
        ("Quality Assurance", "Quality Assurance"),
        ("Front-end Development", "Front-end Development"),
        ("Java Development", "Java Development"),
        ("Mobile Development", "Mobile Development"),
        ("Ruby Development", "Ruby Development"),
        ("Argentina Labs", "Argentina Labs"),
        ("CF Minsk", "CF Minsk"),
        ("CF US", "CF US"),
        ("Blockchain Start-ups", "Blockchain Start-ups"),
        ("Insurance on Tokens", "Insurance on Tokens"),
        ("EBC", "EBC"),
        ("ML/Al", "ML/Al"),
        ("IT Infrastructure", "IT Infrastructure"),
        ("MLBL_Robot", "MLBL_Robot"),
        ("MLBL_Camera", "MLBL_Camera"),
        ("MLBL_Camera_Hardware", "MLBL_Camera_Hardware"),
    ], string="Department 3 OLD")
    x_studio_department_4 = fields.Selection(selection=[
        (".NET Development", ".NET Development"),
        ("Quality Assurance", "Quality Assurance"),
        ("Front-end Development", "Front-end Development"),
        ("Java Development", "Java Development"),
        ("Mobile Development", "Mobile Development"),
        ("Ruby Development", "Ruby Development"),
        ("Argentina Labs", "Argentina Labs"),
        ("CF Minsk", "CF Minsk"),
        ("CF US", "CF US"),
        ("Blockchain Start-ups", "Blockchain Start-ups"),
        ("Insurance on Tokens", "Insurance on Tokens"),
        ("EBC", "EBC"),
        ("ML/Al", "ML/Al"),
        ("IT Infrastructure", "IT Infrastructure"),
        ("MLBL_Robot", "MLBL_Robot"),
        ("MLBL_Camera", "MLBL_Camera"),
        ("MLBL_Camera_Hardware", "MLBL_Camera_Hardware"),
    ], string="Department 4 OLD")
    x_studio_department_5 = fields.Selection(selection=[
        (".NET Development", ".NET Development"),
        ("Quality Assurance", "Quality Assurance"),
        ("Front-end Development", "Front-end Development"),
        ("Java Development", "Java Development"),
        ("Mobile Development", "Mobile Development"),
        ("Ruby Development", "Ruby Development"),
        ("Argentina Labs", "Argentina Labs"),
        ("CF Minsk", "CF Minsk"),
        ("CF US", "CF US"),
        ("Blockchain Start-ups", "Blockchain Start-ups"),
        ("Insurance on Tokens", "Insurance on Tokens"),
        ("EBC", "EBC"),
        ("ML/Al", "ML/Al"),
        ("IT Infrastructure", "IT Infrastructure"),
        ("MLBL_Robot", "MLBL_Robot"),
        ("MLBL_Camera", "MLBL_Camera"),
        ("MLBL_Camera_Hardware", "MLBL_Camera_Hardware"),
    ], string="Department 5 OLD")
    x_studio_revenue_1 = fields.Char(string="Revenue 1 OLD")
    x_studio_revenue_2 = fields.Char(string="Revenue 2 OLD")
    x_studio_revenue_3 = fields.Char(string="Revenue 3 OLD")
    x_studio_revenue_4 = fields.Char(string="Revenue 4 OLD")
    x_studio_revenue_5 = fields.Char(string="Revenue 5 OLD")
    x_studio_discount_1_1 = fields.Char(string="Discount 1 OLD")
    x_studio_discount_2 = fields.Char(string="Discount 2 OLD")
    x_studio_discount_3 = fields.Char(string="Discount 3 OLD")
    x_studio_discount_4 = fields.Char(string="Discount 4 OLD")
    x_studio_discount_5 = fields.Char(string="Discount 5 OLD")
    x_studio_comment_1 = fields.Char(string="Comment 1 OLD")
    x_studio_comment_2 = fields.Char(string="Comment 2 OLD")
    x_studio_comment_3 = fields.Char(string="Comment 3 OLD")
    x_studio_comment_4 = fields.Char(string="Comment 4 OLD")
    x_studio_comment_5 = fields.Char(string="Comment 5 OLD")
    x_studio_currentnew = fields.Selection(selection=[("Current", "Current"), ("New", "New")],
                                           string="Current/New OLD", default="Current")
    x_studio_sales_type = fields.Selection(selection=[
        ("Base", "Base"), ("Upsales", "Upsales"), ("Cross-sell", "Cross-sell")], string="Sales Type 1 OLD")
    x_studio_sales_type_2 = fields.Selection(selection=[
        ("Base", "Base"), ("Upsales", "Upsales"), ("Cross-sell", "Cross-sell")], string="Sales Type 2 OLD")
    x_studio_sales_type_3_1 = fields.Selection(selection=[
        ("Base", "Base"), ("Upsales", "Upsales"), ("Cross-sell", "Cross-sell")], string="Sales Type 3 OLD")
    x_studio_revenue_currentnew = fields.Char(string="Revenue Current/New OLD")
    x_studio_revenue_sales_type_1 = fields.Char(string="Revenue Sales Type 1 OLD")
    x_studio_revenue_sales_type_2 = fields.Char(string="Revenue Sales Type 2 OLD")
    x_studio_revenue_sales_type_3 = fields.Char(string="Revenue Sales Type 3 OLD")
    x_studio_currency = fields.Char(string="Currency OLD")
    x_studio_company_currency = fields.Char(string="Company currency OLD")
    actual_due_date = fields.Date(compute="_compute_actual_due_date", string="Actual Due Date", store=True)
    deviation = fields.Float(string="Deviation, days", group_operator="avg")

    def get_report_base_filename(self):
        """Get report filename"""
        return f"timesheets_report_{', '.join(self.mapped('name'))}"

    @api.onchange("project_id")
    def onchange_project_id(self):
        """Change partner_id according project_id"""
        self.partner_id = self.project_id.partner_id.id

    @api.depends("invoice_date", "partner_id", "partner_id.account_payment_term")
    def _compute_actual_due_date(self):
        """Compute actual_due_date field according invoice_date and account_payment_term"""
        for rec in self:
            payment_term = rec.partner_id.account_payment_term if rec.partner_id else False
            rec.actual_due_date = rec.invoice_date + timedelta(
                days=payment_term) if payment_term and rec.invoice_date else rec.invoice_date_due

    @api.depends("rate_employee_timesheet_ids")
    def _compute_sales_type_departments_ids(self):
        """
        Creates sales_type_departments lines from rate_employee_timesheet_ids data.
        Calculates rate value for departments sales_types.
        """
        for rec in self:
            timesheet_value_data = {}
            for rate_id in rec.rate_employee_timesheet_ids:
                timesheet_value_data.setdefault(rate_id.department_id, {rate_id.sales_type: {"total": 0, "count": 0}})
                timesheet_value_data[rate_id.department_id].setdefault(rate_id.sales_type, {"total": 0, "count": 0})

                timesheet_value_data[rate_id.department_id][rate_id.sales_type]["total"] += rate_id.total_value
                timesheet_value_data[rate_id.department_id][rate_id.sales_type]["count"] += 1

            self.sales_type_departments_ids = [(5, 0, 0)]
            for department_id, sales_type_values in timesheet_value_data.items():
                for sales_type, value in sales_type_values.items():
                    rec.sales_type_departments_ids = [(0, 0, {
                        "dept_id": department_id.id,
                        "sales_type_by_dept": sales_type or "not_set",
                        "account_move_id": rec.id,
                        "sales_revenue_by_dept": value["total"],
                        "sales_type_elements_count": value["count"],
                    })]

    @api.depends("sales_type_departments_ids.revenue_with_disc")
    def _compute_sales_type_revenue_ids(self):
        """Creates sales_type_revenue lines. Calculates sales_type_revenue with discounts"""
        for rec in self:
            sales_type_value_data = {}
            for sales_type_departments_id in rec.sales_type_departments_ids:
                sales_type_value_data.setdefault(sales_type_departments_id.sales_type_by_dept, 0)
                sales_type_value_data[sales_type_departments_id.sales_type_by_dept] += sales_type_departments_id.revenue_with_disc

            self.sales_type_revenue_ids = [(5, 0, 0)]
            for sales_type, total_value in sales_type_value_data.items():
                rec.sales_type_revenue_ids = [(0, 0, {"sales_type": sales_type,
                                                      "account_move_id": rec.id,
                                                      "sales_type_revenue": total_value})]

    @api.depends("department_rate_ids.with_discount")
    def _compute_with_discount(self):
        """Compute total_with_discount field"""
        for rec in self:
            rec.total_with_discount = sum(rec.department_rate_ids.mapped("with_discount"))

    def create_line_name(self):
        """ Create line name for account.move.line """
        start_date = self.start_date.strftime("%d %B") if self.start_date else False
        end_date = self.end_date.strftime("%d %B, %Y") if self.end_date else False
        name = f"Payment for the period {start_date} - {end_date}"
        return name

    @api.onchange("rate_employee_timesheet_ids")
    def onchange_rate_employee_timesheet_ids(self):
        """Compute rate_employee_timesheet_ids fieldhe chjer bfcherbfh"""
        for rec in self:
            rec.department_rate_ids = [(5, 0, 0)]
            unique_department_ids = set(self.rate_employee_timesheet_ids.mapped("department_id"))
            for department_id in unique_department_ids:
                self.department_rate_ids = [(0, 0, {"department_id": department_id.id,
                                                    "account_move_id": rec.id,
                                                    })]

    @api.depends("rate_employee_timesheet_ids.total_value")
    def _compute_total_price(self):
        """Compute total_price field"""
        for rec in self:
            rec.total_price = sum(rec.rate_employee_timesheet_ids.mapped("total_value"))

    def set_invoice_line_ids(self):
        """Set invoice_line_ids,find account_id for current company or create account_id"""
        product_id = self.env.ref("altoros.product_service").id
        account_id = self.env["account.account"].search(
                [("user_type_id", "=", self.env.ref("account.data_account_type_revenue").id),
                 ("company_id", "=", self.company_id.id),
                 ("is_use_for_service", "=", True)], limit=1).id
        if not account_id:
            account_id = self.env["account.account"].create(
                {"name": "Product Sales",
                 "code": "400000",
                 "user_type_id": self.env.ref("account.data_account_type_revenue").id,
                 "company_id": self.company_id.id,
                 "is_use_for_service": True}).id
        price_unit = self.total_price
        if not self.env.context.get("is_tomesheets_context"):
            price_unit = self.total_with_discount
        vals_dct = {"product_id": product_id,
                    "move_id": self.id,
                    "account_id": account_id,
                    "quantity": 1,
                    "name": self.create_line_name(),
                    "price_unit": price_unit,
                    }
        if self.invoice_line_ids:
            min_sequence = min(self.invoice_line_ids.mapped("sequence"))
            vals_dct["sequence"] = min_sequence
            min_sequence_line_ids = self.invoice_line_ids.filtered(lambda rec: rec.sequence == min_sequence)
            self.invoice_line_ids = [(2, min_sequence_line_ids[0].id)]
            if len(min_sequence_line_ids) > 1:
                for invoice_line_id in self.invoice_line_ids:
                    invoice_line_id.sequence = invoice_line_id.sequence + 1
        self.invoice_line_ids = [(0, 0, vals_dct)]
        self.department_rate_ids._set_total_value_hours_dpt()

    def check_for_or_create_record(self, model_name, search_domain, **kwargs):
        """Checking for or creating a model record."""
        try:
            record_id = self.env[model_name].search(search_domain, limit=1)
            if not record_id:
                record_id = self.env[model_name].create(kwargs)
            return record_id
        except (AttributeError, Exception):
            return self.env[model_name].create(kwargs)

    @api.model
    def create(self, vals):
        """Call method _check_fiscalyear_lock_date if move with invoice date and not move_lines"""
        res = super(AccountMove, self).create(vals)
        if not res.invoice_line_ids:
            res._check_fiscalyear_lock_date()
        return res

    def write(self, vals):
        """Call method _check_fiscalyear_lock_date
        if move with invoice_date and method was not called before"""
        res = super(AccountMove, self).write(vals)
        for move in self:
            is_checked_lock_dates = ("date" in vals and move.date != vals["date"]) \
                                    or ("state" in vals and move.state == "posted" and vals["state"] != "posted")
            if not is_checked_lock_dates and move.invoice_date:
                move._check_fiscalyear_lock_date()
        return res

    def _check_fiscalyear_lock_date(self):
        """Overwrite method for checking not only state and moves with invoice_date"""
        for move in self.filtered(lambda move: move.state == "posted" or move.invoice_date):
            if self.user_has_groups("account.group_account_manager"):
                if move.date <= (move.company_id.fiscalyear_lock_date or date.min):
                    raise UserError(_(
                        "You cannot add/modify entries prior to and inclusive of the lock date %s.") % format_date \
                                        (self.env, move.company_id.fiscalyear_lock_date))
            else:
                lock_date = max(move.company_id.period_lock_date or date.min,
                                move.company_id.fiscalyear_lock_date or date.min)
                if move.date <= (lock_date or date.min):
                    raise UserError(_("You cannot add/modify entries prior to and inclusive of the lock date %s. "
                                      "Check the company settings or ask someone with the 'Adviser' role") % format_date \
                                        (self.env, lock_date))
        return True

    def action_post(self):
        """Check sales_type and sales_type_revenue fields"""
        res = super(AccountMove, self).action_post()
        for move in self:
            if not move.project_owner:
                raise UserError(_("Project Owner BL must be selected. Go to the Project and select it."))
            if not move.sales_type or not move.sales_type_revenue:
                raise UserError(_("Please fill in the fields Current/New and Revenue Current/New"))
        self.calculate_deviation()
        return res

    def calculate_deviation(self):
        """Calculate devision field according invoice_date"""
        for move_id in self:
            if not move_id.partner_id.expected_billing_date_ids:
                continue
            else:
                expected_billing_rate = sorted(move_id.partner_id.expected_billing_date_ids.mapped("billing_rate"), reverse=True)
                if move_id.invoice_date.month == 2:
                    expected_billing_rate = [28 if rate in (29, 30) else rate for rate in expected_billing_rate]
                invoice_day_qty = move_id.invoice_date.day if move_id.invoice_date else False
                if invoice_day_qty:
                    if any([invoice_day_qty == rate for rate in expected_billing_rate]):
                        move_id.deviation = 0
                        continue
                    min_qty_days_data = {abs(rate - invoice_day_qty): rate for rate in
                                         expected_billing_rate}
                    min_qty_days = min(min_qty_days_data.keys())
                    min_rate = min_qty_days_data[min_qty_days]
                    if min_rate > invoice_day_qty:
                        min_qty_days = -min_qty_days
                    try:
                        if min_qty_days >= 16:
                            move_id.deviation = 30 - min_qty_days
                        else:
                            move_id.deviation = min_qty_days
                    except Exception:
                        _logger.exception("Failed to write deviation")
