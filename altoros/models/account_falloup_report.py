import re
from datetime import date

from odoo import api, models
from odoo.tools.translate import _


class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"

    def _cron_send_email_followup(self):
        """Send by mail the followup to all customers who has followup_level"""
        partner_ids = self.env["res.partner"].search([("followup_level", "!=", False), ("is_follow_up", "=", True)])
        for record in partner_ids:
            options = {
                "partner_id": record.id,
            }
            try:
                self.send_email(options)
            except ValueError:
                return False

    @api.model
    def send_email(self, options):
        """Send by mail the followup to the customer"""
        partner_id = self.env["res.partner"].search([("id", "=", options.get("partner_id"))])
        non_blocked_aml_ids = partner_id.unreconciled_aml_ids.filtered(lambda aml: not aml.blocked)
        if not non_blocked_aml_ids:
            return True
        invoice_partner = self.env["res.partner"].browse(partner_id.address_get(["invoice"])["invoice"])
        email = invoice_partner.email
        if email and email.strip():
            self = self.with_context(lang=partner_id.lang or self.env.user.lang)
            for followup_id in self.env["account_followup.followup.line"].search([("auto_execute", "=", True)]):
                if any([(date.today() - line_id.move_id.invoice_date_due).days == followup_id.delay if line_id.move_id.invoice_date_due else False
                        for line_id in non_blocked_aml_ids]):
                    account_move_object = self.env["account.move"]
                    options["followup_level"] = (followup_id.id, followup_id.delay)
                    options["keep_summary"] = False
                    body_html = self.with_context(print_mode=True, mail=True).get_html(options)
                    body_html = body_html.replace(b"o_account_reports_edit_summary_pencil",
                                                  b"o_account_reports_edit_summary_pencil d-none")
                    start_index = body_html.find(b"<span>", body_html.find(b"<div class='o_account_reports_summary'>"))
                    end_index = start_index > -1 and body_html.find(b"</span>", start_index) or -1
                    if end_index > -1:
                        replaced_msg = body_html[start_index:end_index].replace(b"\n", b"")
                        body_html = body_html[:start_index] + replaced_msg + body_html[end_index:]
                    for move_line_id in non_blocked_aml_ids:
                        if not move_line_id.move_id.invoice_date_due or (
                                date.today() - move_line_id.move_id.invoice_date_due).days != followup_id.delay:
                            pattern = re.compile(fr"<tr((?!tr)[\s\S])*?{move_line_id.id}[\s\S]*?tr>".encode("utf-8"))
                            body_html = pattern.sub(b"", body_html)
                        else:
                            account_move_object += move_line_id.move_id
                            project_name = move_line_id.move_id.project_id.name
                            amount_residual = str(move_line_id.move_id.amount_residual)
                            invoice_date_due = move_line_id.move_id.invoice_date_due.strftime("%B %d")
                            body_html = body_html.replace(b"{project_project_name}", project_name.encode("ascii"))
                            body_html = body_html.replace(b"{account_move_amount_residual}", amount_residual.encode("ascii"))
                            body_html = body_html.replace(b"{invoice_date_due}", invoice_date_due.encode("ascii"))
                    for res_partner_id in partner_id + partner_id.child_ids.filtered(lambda p: p.is_follow_up):
                        res_partner_id.with_context(mail_post_autofollow=True,
                                                lang=res_partner_id.lang or self.env.user.lang).message_post(
                            partner_ids=[invoice_partner.id],
                            body=body_html,
                            subject=_("%s Payment Reminder") % (self.env.company.name) + " - " + res_partner_id.name,
                            subtype_id=self.env.ref("mail.mt_note").id,
                            model_description=_("payment reminder"),
                            email_layout_xmlid="mail.mail_notification_light",
                            attachment_ids=followup_id.join_invoices and account_move_object.message_main_attachment_id.ids or [],
                        )

    def _get_lines(self, options, line_id=None):
        """Delete total lines from Follow-up Reports"""
        lines = super()._get_lines(options)
        return [line for line in lines if line.get("class") != "total"]
