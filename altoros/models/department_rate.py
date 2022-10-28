from odoo import models, fields, api


class DepartmentRate(models.Model):
    _name = "department.rate"
    _description = "Department rate"
    _inherit = ["mail.thread"]

    department_id = fields.Many2one(string="Department", comodel_name="hr.department", tracking=True)
    total_department_value = fields.Float(string="Total Value", tracking=True, compute="_compute_total_value_hours_dpt")
    account_move_id = fields.Many2one(string="Account move", comodel_name="account.move")
    discounts_by = fields.Float(string="Discounts", tracking=True)
    discount_comment = fields.Char(string="Comments by Discounts", tracking=True)
    total_hours_dpt = fields.Float(string="Total Hours", compute="_compute_total_value_hours_dpt", tracking=True)
    with_discount = fields.Float(string="With Discount", compute="_compute_with_discount_field", tracking=True, store=True)
    disc_percents = fields.Float(string="Disc. %", tracking=True)
    disc_difference = fields.Float(string="Difference", store=True, compute="_compute_disc_difference")
    number_sales_types_in_dept = fields.Float(string="Number of ST", compute="_compute_number_sales_types", store=True)

    @api.depends("total_department_value", "discounts_by", "disc_percents")
    def _compute_with_discount_field(self):
        """Calculates with_discount field"""
        for rec in self:
            rec.with_discount = rec.total_department_value - rec.discounts_by - rec.disc_percents * rec.total_department_value / 100

    @api.depends("total_department_value", "with_discount")
    def _compute_disc_difference(self):
        """Calculates disc_difference field"""
        for rec in self:
            rec.disc_difference = rec.total_department_value - rec.with_discount

    @api.depends("account_move_id.sales_type_departments_ids.sales_type_elements_count")
    def _compute_number_sales_types(self):
        """Calculates number_sales_types_in_dept field"""
        for rec in self:
            rec.number_sales_types_in_dept = sum(rec.account_move_id.sales_type_departments_ids.mapped(
                lambda record: record.sales_type_elements_count if record.dept_id == rec.department_id else 0))

    def _compute_total_value_hours_dpt(self):
        """Calculates total_hours and total_department_value for department from employee timesheets"""
        for rec in self:
            used_employee_timesheet_ids = self.account_move_id.rate_employee_timesheet_ids.filtered(
                lambda sheet_id: sheet_id.department_id == rec.department_id)
            rec.total_hours_dpt = sum(used_employee_timesheet_ids.mapped("unit_amount"))
            rec.total_department_value = sum(used_employee_timesheet_ids.mapped("total_value"))
