from odoo import fields, models
from odoo.tools.translate import _

class ResPartner(models.Model):
    _inherit = "res.partner"

    account_payment_term = fields.Integer(string="Actual payment terms, days")
    expected_billing_date_ids = fields.Many2many(comodel_name="expected.billing.date",
                                                 relation="partner_expected_billing_date_rel",
                                                 column1="res_partner_id", column2="expected_billing_date_id",
                                                 string="Expected billing date")
    is_follow_up = fields.Boolean(string="Follow-ups", default=True)

    def return_related_project(self):
        """Return all related projects for res_partner"""
        project_ids = self.env["project.project"].search([("partner_id", "=", self.id)])
        return {
            "name": _("Projects"),
            "domain": [("id", "in", project_ids.ids)],
            "res_model": "project.project",
            "view_mode": "tree,form",
            "type": "ir.actions.act_window",
        }

    def write(self, values):
        """Update deviation field for posted customer invoices"""
        result = super(ResPartner, self).write(values)
        for rec in self:
            if "expected_billing_date_ids" in values:
                self.env["account.move"].search(
                    [("type", "=", "out_invoice"), ("state", "=", "posted"),
                     ("partner_id", "=", rec.id)]).calculate_deviation()
        return result
