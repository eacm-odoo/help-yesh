from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ExpectedBillingDate(models.Model):
    _name = "expected.billing.date"
    _description = "Expected billing date"
    _rec_name = "billing_rate"

    billing_rate = fields.Integer(string="Billing rate", required=True)

    @api.constrains("billing_rate")
    def _check_billing_rate(self):
        """Check range of billing_rate"""
        if self.billing_rate > 30 or self.billing_rate < 1:
            raise ValidationError(_("Check expected billing date."))
