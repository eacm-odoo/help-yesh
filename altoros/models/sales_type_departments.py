from odoo import fields, models, api


class SaleTypeDepartments(models.Model):
    _name = "sales.type.departments"
    _description = "Sales type by departments"

    dept_id = fields.Many2one(comodel_name="hr.department", string="Department", readonly=True)
    sales_type_by_dept = fields.Selection(string="Sales type",
                                          selection=[("base", "Base"), ("upsale", "Upsale"), ("cross-sale", "Cross-sale"),
                                                     ("not_set", "Not set")], readonly=True)
    sales_type_elements_count = fields.Integer(string="Sales type elements count")
    sales_revenue_by_dept = fields.Float(string="Revenue", readonly=True)
    account_move_id = fields.Many2one(string="Account move", comodel_name="account.move")
    revenue_with_disc = fields.Float(string="Revenue with Discounts", compute="_compute_revenue_with_disc", store=True)

    @api.depends("account_move_id.department_rate_ids.disc_difference", "sales_revenue_by_dept")
    def _compute_revenue_with_disc(self):
        """Calculates revenue_with_disc if changed disc_difference in department_rate_ids"""
        for rec in self:
            department_rate_ids = rec.account_move_id.department_rate_ids.filtered(lambda record: record.department_id == rec.dept_id)
            rec.revenue_with_disc = rec.sales_revenue_by_dept - sum(department_rate_ids.mapped("disc_difference")) / (sum(department_rate_ids.mapped("number_sales_types_in_dept")) or 1) * rec.sales_type_elements_count