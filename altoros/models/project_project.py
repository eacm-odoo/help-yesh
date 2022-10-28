from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = "project.project"

    project_owner = fields.Selection(selection=[
        ("dedicated_teams", "Dedicated Teams"),
        ("cloud_foundry", "Cloud Foundry"),
        ("protofire", "Protofire"),
    ], string="Project Owner BL")

    project_customer = fields.Many2one(string="Customer Project", comodel_name="res.partner")
