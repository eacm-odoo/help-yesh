from collections import defaultdict

from odoo import fields, models, api


class SaleTypeRevenue(models.Model):
    _name = "sales.type.revenue"
    _description = "Sales type revenue"

    sales_type = fields.Selection(string="Sales type",
                                  selection=[("base", "Base"), ("upsale", "Upsale"), ("cross-sale", "Cross-sale"),
                                             ("not_set", "Not set")], readonly=True)
    sales_type_revenue = fields.Float(string="Revenue", readonly=True)
    account_move_id = fields.Many2one(string="Account move", comodel_name="account.move")
