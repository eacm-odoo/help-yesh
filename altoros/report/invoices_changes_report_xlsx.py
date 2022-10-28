import logging
from datetime import datetime
from datetime import timedelta

from odoo import models

_logger = logging.getLogger(__name__)


class InvoicesChangesReportXlsx(models.AbstractModel):
    _name = "report.altoros.invoices_changes_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, invoice_ids):
        """Generating data for the InvoicesChanges report."""
        try:
            report_name = "Invoices Changes"
            start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date() if data.get("start_date") else False
            end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date() if data.get("end_date") else False
            if not start_date and not end_date:
                end_date = datetime.today().date()
                start_date = end_date - timedelta(days=30)

            sheet = workbook.add_worksheet(report_name)

            header_format = workbook.add_format(
                {"align": "left", "font_size": 14, "bold": True, "font_name": "Arial", "underline": True,
                 "color": "#c9211e"})
            table_top_left_format = workbook.add_format({"align": "left", "top": 1, "font_size": 11, "bold": True,
                                                         "font_name": "Arial", "left": 1, "bottom": 1})
            table_top_right_format = workbook.add_format({"align": "left", "top": 1, "font_size": 11, "bold": False,
                                                          "font_name": "Arial", "right": 1, "bottom": 1})
            table_header_format = workbook.add_format(
                {"align": "center", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                 "text_wrap": False, "fg_color": "#87CEEB", "font_size": 10})
            table_format = workbook.add_format(
                {"align": "center", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                 "font_size": 10})

            sheet.set_column(1, 9, 18)

            sheet.merge_range(1, 1, 1, 2, report_name, header_format)

            sheet.write(3, 1, "Reporting period:", table_top_left_format)
            sheet.merge_range(3, 2, 3, 3, f"{start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}",
                              table_top_right_format)

            sheet.write(5, 1, "Date", table_header_format)
            sheet.write(5, 2, "Invoice Number", table_header_format)
            sheet.write(5, 3, "Company", table_header_format)
            sheet.write(5, 4, "Customer", table_header_format)
            sheet.write(5, 5, "Project", table_header_format)
            sheet.write(5, 6, "User", table_header_format)
            sheet.write(5, 7, "Field", table_header_format)
            sheet.write(5, 8, "Before", table_header_format)
            sheet.write(5, 9, "After", table_header_format)
            row = 6

            for invoice_id in invoice_ids:
                message_ids = self.env["mail.message"].search([
                    "&",
                    ("res_id", "=", invoice_id.id),
                    ("model", "=", "account.move"),
                    ("create_date", "<=", end_date),
                    ("create_date", ">=", start_date),
                    ("tracking_value_ids", "!=", False)
                ], order='create_date asc')
                for message_id in message_ids:
                    sheet.write(row, 1, message_id.create_date.strftime("%d.%m.%Y"), table_format)
                    sheet.write(row, 2, invoice_id.name, table_format)
                    sheet.write(row, 3, invoice_id.company_id.name if invoice_id.company_id else "",
                                      table_format)
                    sheet.write(row, 4, invoice_id.partner_id.name if invoice_id.partner_id else "",
                                      table_format)
                    sheet.write(row, 5, invoice_id.project_id.sudo().name if invoice_id.project_id else "",
                                      table_format)

                    for tracking_value_id in message_id.tracking_value_ids:
                        field_type = tracking_value_id.field_type if tracking_value_id.field_type not in ["date", "many2one", "selection", "boolean"] else "datetime" if tracking_value_id.field_type == "date" else "integer" if tracking_value_id.field_type == "boolean" else "char"
                        old_value = tracking_value_id[f"old_value_{field_type}"] if field_type != "datetime" else tracking_value_id[f"old_value_{field_type}"].strftime("%d.%m.%Y") if tracking_value_id[f"old_value_{field_type}"] else ""
                        new_value = tracking_value_id[f"new_value_{field_type}"] if field_type != "datetime" else tracking_value_id[f"new_value_{field_type}"].strftime("%d.%m.%Y") if tracking_value_id[f"new_value_{field_type}"] else ""

                        if tracking_value_id.id != message_id.tracking_value_ids[:1].id:
                            sheet.merge_range(row, 1, row, 5, "", table_format)
                        sheet.write(row, 6, tracking_value_id.create_uid.name if tracking_value_id.create_uid else "",
                                    table_format)
                        sheet.write(row, 7, tracking_value_id.field_desc, table_format)
                        sheet.write(row, 8, old_value if old_value else "", table_format)
                        sheet.write(row, 9, new_value if new_value else "", table_format)
                        row += 1
        except Exception as exc:
            _logger.error(f"Error when creating xlsx invoice report. {exc}")
