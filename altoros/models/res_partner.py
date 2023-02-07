from odoo import fields, models
from odoo.tools.translate import _

class ResPartner(models.Model):
    _inherit = "res.partner"

    account_payment_term = fields.Integer(string="Actual payment terms, days")

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
