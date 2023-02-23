import logging
from datetime import date

from odoo import models

_logger = logging.getLogger(__name__)


class ProjectReportXlsx(models.AbstractModel):
    _name = "report.altoros.project_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, invoice_ids):
        """Generating data for the report xlsx."""
        try:
            for invoice_id in invoice_ids:
                sheet = workbook.add_worksheet(invoice_id.name)
                header_format = workbook.add_format(
                    {"align": "left", "font_size": 14, "bold": True, "font_name": "Arial", "underline": True,
                     "color": "#c9211e"})
                table_top_right_format = workbook.add_format({"align": "left", "top": 1, "font_name": "Arial",
                                                              "right": 1, "font_size": 10})
                table_top_left_format = workbook.add_format({"align": "left", "top": 1, "font_size": 12, "bold": True,
                                                             "font_name": "Arial", "left": 1})
                table_top_left_side_format = workbook.add_format({"align": "left", "font_size": 12, "bold": True,
                                                                  "font_name": "Arial", "left": 1})
                table_top_right_side_format = workbook.add_format({"align": "left", "font_name": "Arial",
                                                                   "right": 1, "font_size": 10})
                table_footer_left_side_format = workbook.add_format(
                    {"align": "left", "font_size": 12, "bold": True, "font_name": "Arial",
                     "bottom": 1, "left": 1})
                table_footer_right_side_format = workbook.add_format({"align": "left", "border": 0,
                                                                      "font_name": "Arial", "bottom": 1, "right": 1,
                                                                      "font_size": 10})
                table_header_format = workbook.add_format(
                    {"align": "center", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                     "text_wrap": True, "fg_color": "#87CEEB", "font_size": 10})
                table_format = workbook.add_format(
                    {"align": "left", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                     "font_size": 10})
                table_right_format = workbook.add_format(
                    {"align": "right", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": True,
                     "font_size": 10, "num_format": "0.00"})
                color_format = workbook.add_format(
                    {"align": "left", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                     "bold": True, "fg_color": "#C7D0CC", "font_size": 10})
                table_color_right_format = workbook.add_format(
                    {"align": "right", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": True,
                     "bold": True, "fg_color": "#C7D0CC", "font_size": 10, "num_format": "0.00"})
                table_footer_format = workbook.add_format(
                    {"align": "center", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                     "text_wrap": True, "fg_color": "#87CEEB", "font_size": 10})
                table_footer_right_format = workbook.add_format(
                    {"align": "right", "valign": "top", "border": 1, "bold": True, "font_name": "Arial",
                     "text_wrap": True, "fg_color": "#87CEEB", "font_size": 10, "num_format": "0.00"})
                sheet.set_column(1, 8, 15)

                sheet.merge_range(1, 1, 1, 3, "Project Report", header_format)
                sheet.merge_range(3, 1, 3, 2, "Prepared by:", table_top_left_format)
                sheet.merge_range(4, 1, 4, 2, "Date:", table_top_left_side_format)
                sheet.merge_range(5, 1, 5, 2, "Project:", table_top_left_side_format)
                sheet.merge_range(6, 1, 6, 2, "Reporting period:", table_footer_left_side_format)
                sheet.merge_range(3, 3, 3, 4, invoice_id.env.user.name, table_top_right_format)
                sheet.merge_range(4, 3, 4, 4, date.today().strftime('%d-%m-%Y'), table_top_right_side_format)
                sheet.merge_range(5, 3, 5, 4, invoice_id.project_id.name, table_top_right_side_format)
                sheet.merge_range(6, 3, 6, 4, "{}-{}".format(invoice_id.start_date.strftime('%d/%m/%Y'),
                                                             invoice_id.end_date.strftime('%d/%m/%Y')),
                                  table_footer_right_side_format)
                sheet.write(8, 1, "Developer", table_header_format)
                sheet.write(8, 2, "Date", table_header_format)
                sheet.write(8, 3, "Task", table_header_format)
                sheet.write(8, 4, "Sum of total hours", table_header_format)
                sheet.write(8, 5, "Non-billable", table_header_format)
                sheet.write(8, 6, "Total billable", table_header_format)
                sheet.write(8, 7, "Rate", table_header_format)
                sheet.write(8, 8, "Total, {}".format(invoice_id.currency_id.name), table_header_format)
                row = 9
                unique_employee_ids = set(invoice_id.rate_employee_timesheet_ids.mapped("employee_id"))
                for employee_id in unique_employee_ids:
                    timesheet_ids = invoice_id.rate_employee_timesheet_ids.search(
                        [("employee_id", "=", employee_id.id), ("account_move_id", "=", invoice_id.id)])
                    for timesheet_id in timesheet_ids.sorted("date"):
                        if timesheet_id.id == timesheet_ids[:1].id:
                            sheet.write(row, 1, timesheet_id.employee_id.name, table_format)
                        else:
                            sheet.write(row, 1, "", table_format)
                        sheet.write(row, 2, timesheet_id.date.strftime('%d-%m-%Y'), table_format)
                        sheet.write(row, 3, timesheet_id.task_id.name if timesheet_id.task_id else "", table_format)
                        sheet.write(row, 4, timesheet_id.unit_amount, table_right_format)
                        sheet.write(row, 5, "", table_format)
                        sheet.write(row, 6, timesheet_id.unit_amount, table_right_format)
                        sheet.write(row, 7, timesheet_id.rate, table_right_format)
                        sheet.write(row, 8, timesheet_id.total_value, table_right_format)
                        row += 1
                    sum_total_billable_value = sum(timesheet_ids.mapped("unit_amount"))
                    sum_total_value = sum(timesheet_ids.mapped("total_value"))
                    sheet.write(row, 1, "{} Total".format(employee_id.name), color_format)
                    sheet.write(row, 2, "", color_format)
                    sheet.write(row, 3, "", color_format)
                    sheet.write(row, 4, sum_total_billable_value, table_color_right_format)
                    sheet.write(row, 5, "", color_format)
                    sheet.write(row, 6, sum_total_billable_value, table_color_right_format)
                    sheet.write(row, 7, sum_total_value / sum_total_billable_value if sum_total_billable_value else 0,
                                table_color_right_format)
                    sheet.write(row, 8, sum_total_value, table_color_right_format)
                    row += 1
            sheet.write(row, 1, "Total", table_footer_format)
            for col in range(2, 6):
                sheet.write(row, col, "", table_footer_format)
            sheet.write(row, 6, sum(invoice_id.rate_employee_timesheet_ids.mapped("unit_amount")),
                        table_footer_right_format)
            sheet.write(row, 7, "", table_footer_format)
            sheet.write(row, 8, sum(invoice_id.rate_employee_timesheet_ids.mapped("total_value")),
                        table_footer_right_format)
            for department_rate in invoice_id.department_rate_ids:
                if department_rate.discounts_by:
                    row += 1
                    sheet.merge_range(row, 1, row, 7, "Discounts {}".format(department_rate.department_id.name), color_format)
                    sheet.write(row, 8, department_rate.discounts_by, table_color_right_format)
                if department_rate.disc_percents:
                    row += 1
                    sheet.merge_range(row, 1, row, 7, "Discounts, % {}".format(department_rate.department_id.name), color_format)
                    sheet.write(row, 8, department_rate.disc_percents, table_color_right_format)
            if any(invoice_id.department_rate_ids.mapped("discounts_by")) or any(invoice_id.department_rate_ids.mapped("disc_percents")):
                row += 1
                sheet.write(row, 1, "Grand Total", table_footer_format)
                sheet.merge_range(row, 2, row, 7, "", table_footer_format)
                sheet.write(row, 8, invoice_id.total_with_discount, table_footer_right_format)
        except Exception as exc:
            _logger.error(f"Error when creating xlsx invoice report. {exc}")
