from odoo import models, api, fields


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "mail.thread"]

    fields_to_track = fields.Char(string="Track all fields", default=["quantity", "price_unit", "discount", "price_subtotal", "debit", "credit"])

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """ Changing the creation of name in lines """
        for line in self:
            if not line.product_id or line.display_type in ("line_section", "line_note"):
                continue

            line.name = self.move_id.create_line_name()
            line.account_id = line._get_computed_account()
            taxes = line._get_computed_taxes()
            if taxes and line.move_id.fiscal_position_id:
                taxes = line.move_id.fiscal_position_id.map_tax(taxes, partner=line.partner_id)
            line.tax_ids = taxes
            line.product_uom_id = line._compute_product_uom_id()
            line.price_unit = line._compute_price_unit()

        if len(self) == 1:
            return {"domain": {"product_uom_id": [("category_id", "=", self.product_uom_id.category_id.id)]}}

    def unlink(self):
        """Sends message to chatter if record unlinked"""
        for rec in self:
            rec._send_message_to_chatter()
        res = super().unlink()
        return res
