from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_use_for_service = fields.Boolean(string="Use for Service")
