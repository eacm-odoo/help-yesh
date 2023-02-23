import logging
from datetime import date

from odoo import models

_logger = logging.getLogger(__name__)


class InvoicesChangesReportXlsx(models.AbstractModel):
    _name = "report.altoros.invoice_timesheets_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, invoice_ids):
        """Generating data for the Timesheets report."""
        try:
            report_name = "Timesheets report"
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
            color_grey_format = workbook.add_format(
                {"align": "left", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                 "bold": True, "fg_color": "#DCDCDC", "font_size": 10})
            color_bluish_format = workbook.add_format(
                {"align": "left", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                 "bold": True, "fg_color": "#BFE3F9", "font_size": 10})
            not_set_format = workbook.add_format(
                {"align": "left", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                 "bold": True, "fg_color": "#FFB6C1", "font_size": 10})
            color_dark_blue_format = workbook.add_format(
                {"align": "left", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                 "text_wrap": True, "fg_color": "#87CEEB", "font_size": 10})
            color_light_blue_format = workbook.add_format(
                {"align": "left", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                 "text_wrap": True, "fg_color": "#D6EEFF", "font_size": 10})
            sheet = workbook.add_worksheet(report_name)
            sheet.set_column(1, 11, 15)
            sheet.merge_range(1, 1, 1, 3, "Timesheet Report", header_format)
            sheet.merge_range(3, 1, 3, 2, "Invoice:", table_top_left_format)
            sheet.merge_range(4, 1, 4, 2, "Date:", table_top_left_side_format)
            sheet.merge_range(5, 1, 5, 2, "Reporting period:", table_footer_left_side_format)
            sheet.merge_range(3, 3, 3, 6, ", ".join(invoice_ids.mapped("name")), table_top_right_format)
            sheet.merge_range(4, 3, 4, 6, date.today().strftime('%d-%m-%Y'), table_top_right_side_format)
            start_date = data.get("start_date") if data.get("start_date") else invoice_ids[:1].invoice_date.strftime('%d/%m/%Y')
            end_date = data.get("end_date") if data.get("end_date") else invoice_ids[:1].invoice_date.strftime('%d/%m/%Y')
            sheet.merge_range(5, 3, 5, 6, "from {} to {}".format(start_date, end_date), table_footer_right_side_format)
            sheet.write(8, 1, "Invoice", table_header_format)
            sheet.write(8, 2, "Project", table_header_format)
            sheet.write(8, 3, "Developer", table_header_format)
            sheet.write(8, 4, "Date", table_header_format)
            sheet.write(8, 5, "Task", table_header_format)
            sheet.write(8, 6, "Total hours", table_header_format)
            sheet.write(8, 7, "Rate", table_header_format)
            sheet.write(8, 8, "Total Value", table_header_format)
            sheet.write(8, 9, "Department", table_header_format)
            sheet.write(8, 10, "Sales Type", table_header_format)
            sheet.write(8, 11, "Comment", table_header_format)
            row = 9
            for invoice_id in invoice_ids:
                for timesheet_id in invoice_id.rate_employee_timesheet_ids.sorted("date"):
                    sheet.write(row, 1, invoice_id.name, table_format)
                    sheet.write(row, 2, invoice_id.project_id.name if invoice_id.project_id else "Not Set", table_format)
                    sheet.write(row, 3, timesheet_id.employee_id.name if timesheet_id.employee_id else "Not Set", table_format)
                    sheet.write(row, 4, timesheet_id.date.strftime('%d-%m-%Y') if timesheet_id.date else "", table_format)
                    sheet.write(row, 5, timesheet_id.task_id.name if timesheet_id.task_id else "", table_format)
                    sheet.write(row, 6, timesheet_id.unit_amount, table_right_format)
                    sheet.write(row, 7, timesheet_id.rate if timesheet_id.rate else "", table_right_format)
                    sheet.write(row, 8, timesheet_id.total_value, table_right_format)
                    sheet.write(row, 9, timesheet_id.department_id.name if timesheet_id.department_id else "Not Set", table_right_format)
                    sheet.write(row, 10, timesheet_id.sales_type if timesheet_id.sales_type else "Not Set", table_right_format)
                    sheet.write(row, 11, timesheet_id.comment if timesheet_id.comment else "", table_right_format)
                    row += 1
            unique_project_ids = set(invoice_ids.mapped("project_id"))
            sum_hours_by_project = 0
            sum_value_by_project = 0
            for project_id in unique_project_ids:
                used_invoice_ids = invoice_ids.filtered(lambda sheet_id: sheet_id.project_id == project_id)
                total_hours = sum(used_invoice_ids.rate_employee_timesheet_ids.mapped("unit_amount"))
                total_department_value = sum(used_invoice_ids.rate_employee_timesheet_ids.mapped("total_value"))
                sheet.merge_range(row, 3, row, 4, "Project: {} Total".format(project_id.name), color_dark_blue_format)
                sheet.write(row, 5, "", color_dark_blue_format)
                sheet.write(row, 6, total_hours, color_dark_blue_format)
                sheet.write(row, 7, "", color_dark_blue_format)
                sheet.write(row, 8, total_department_value, color_dark_blue_format)
                sum_hours_by_project += total_hours
                sum_value_by_project += total_department_value
                row += 1
            total_hours_without_discount = sum(invoice_ids.rate_employee_timesheet_ids.mapped("unit_amount"))
            total_value_without_discount = sum(invoice_ids.rate_employee_timesheet_ids.mapped("total_value"))
            if sum_hours_by_project != total_hours_without_discount:
                sheet.merge_range(row, 3, row, 4, "Project: Not Set Total", not_set_format)
                sheet.write(row, 5, "", not_set_format)
                sheet.write(row, 6, total_hours_without_discount - sum_hours_by_project, not_set_format)
                sheet.write(row, 7, "", not_set_format)
                sheet.write(row, 8, total_value_without_discount - sum_value_by_project, not_set_format)
                row += 1
            unique_employee_ids = set(invoice_ids.rate_employee_timesheet_ids.mapped("employee_id"))
            sum_hours_by_employee = 0
            sum_value_by_employee = 0
            for employee_id in unique_employee_ids:
                used_employee_timesheet_ids = invoice_ids.rate_employee_timesheet_ids.filtered(
                    lambda sheet_id: sheet_id.employee_id == employee_id)
                total_hours = sum(used_employee_timesheet_ids.mapped("unit_amount"))
                total_department_value = sum(used_employee_timesheet_ids.mapped("total_value"))
                sheet.merge_range(row, 3, row, 4, "{} Total".format(employee_id.name), color_grey_format)
                sheet.write(row, 5, "", color_grey_format)
                sheet.write(row, 6, total_hours, color_grey_format)
                sheet.write(row, 7, "", color_grey_format)
                sheet.write(row, 8, total_department_value, color_grey_format)
                sum_hours_by_employee += total_hours
                sum_value_by_employee += total_department_value
                row += 1
            if sum_hours_by_employee != total_hours_without_discount:
                sheet.merge_range(row, 3, row, 4, "Developer: Not Set Total", not_set_format)
                sheet.write(row, 5, "", not_set_format)
                sheet.write(row, 6, total_hours_without_discount - sum_hours_by_employee, not_set_format)
                sheet.write(row, 7, "", not_set_format)
                sheet.write(row, 8, total_value_without_discount - sum_value_by_employee, not_set_format)
                row += 1
            unique_department_ids = set(invoice_ids.rate_employee_timesheet_ids.mapped("department_id"))
            sum_hours_by_department = 0
            sum_value_by_department = 0
            for department_id in unique_department_ids:
                used_department_timesheet_ids = invoice_ids.rate_employee_timesheet_ids.filtered(
                    lambda sheet_id: sheet_id.department_id == department_id)
                total_hours = sum(used_department_timesheet_ids.mapped("unit_amount"))
                total_department_value = sum(used_department_timesheet_ids.mapped("total_value"))
                sheet.merge_range(row, 3, row, 4, "Department: {} Total".format(department_id.name), color_bluish_format)
                sheet.write(row, 5, "", color_bluish_format)
                sheet.write(row, 6, total_hours, color_bluish_format)
                sheet.write(row, 7, "", color_bluish_format)
                sheet.write(row, 8, total_department_value, color_bluish_format)
                sum_hours_by_department += total_hours
                sum_value_by_department += total_department_value
                row += 1
            if sum_hours_by_department != total_hours_without_discount:
                sheet.merge_range(row, 3, row, 4, "Department: Not Set Total", not_set_format)
                sheet.write(row, 5, "", not_set_format)
                sheet.write(row, 6, total_hours_without_discount - sum_hours_by_department, not_set_format)
                sheet.write(row, 7, "", not_set_format)
                sheet.write(row, 8, total_value_without_discount - sum_value_by_project, not_set_format)
                row += 1
            unique_sales_types = set(invoice_ids.rate_employee_timesheet_ids.mapped("sales_type"))
            for sales_type in unique_sales_types:
                used_sales_type_timesheet_ids = invoice_ids.rate_employee_timesheet_ids.filtered(
                    lambda sheet_id: sheet_id.sales_type == sales_type)
                total_hours = sum(used_sales_type_timesheet_ids.mapped("unit_amount"))
                total_department_value = sum(used_sales_type_timesheet_ids.mapped("total_value"))
                sheet.merge_range(row, 3, row, 4, "Sales Type: {} Total".format(
                    sales_type) if sales_type else "Sales type: Not Set Total", color_light_blue_format if sales_type else not_set_format)
                sheet.write(row, 5, "", color_light_blue_format if sales_type else not_set_format)
                sheet.write(row, 6, total_hours, color_light_blue_format if sales_type else not_set_format)
                sheet.write(row, 7, "", color_light_blue_format if sales_type else not_set_format)
                sheet.write(row, 8, total_department_value, color_light_blue_format if sales_type else not_set_format)
                row += 1
            sheet.merge_range(row, 3, row, 4, "Total without discount", color_dark_blue_format)
            sheet.write(row, 5, "", color_dark_blue_format)
            sheet.write(row, 6, total_hours_without_discount, color_dark_blue_format)
            sheet.write(row, 7, "", color_dark_blue_format)
            sheet.write(row, 8, total_value_without_discount, color_dark_blue_format)
            row += 1
            discount_department_ids = set(invoice_ids.department_rate_ids.mapped("department_id"))
            for department_id in discount_department_ids:
                used_discount_department_ids = invoice_ids.department_rate_ids.filtered(
                    lambda sheet_id: sheet_id.department_id == department_id)
                discount = sum(used_discount_department_ids.mapped("discounts_by"))
                sheet.merge_range(row, 3, row, 4,
                                  "{} Discount".format(department_id.name) if department_id else "Department: Not Set",
                                  color_bluish_format)
                sheet.write(row, 5, "", color_bluish_format)
                sheet.write(row, 6, "", color_bluish_format)
                sheet.write(row, 7, "", color_bluish_format)
                sheet.write(row, 8, discount, color_bluish_format)
                row += 1
                discount_percent = sum(used_discount_department_ids.mapped("disc_percents"))
                sheet.merge_range(row, 3, row, 4,
                                  "{} Discount, %".format(department_id.name) if department_id else "Department: Not Set",
                                  color_bluish_format)
                sheet.write(row, 5, "", color_bluish_format)
                sheet.write(row, 6, "", color_bluish_format)
                sheet.write(row, 7, "", color_bluish_format)
                sheet.write(row, 8, discount_percent, color_bluish_format)
                row += 1
            unique_sales_type_revenue = set(invoice_ids.sales_type_revenue_ids.mapped("sales_type"))
            for sales_type in unique_sales_type_revenue:
                used_sales_type_revenue_ids = invoice_ids.sales_type_revenue_ids.filtered(
                    lambda revenue_id: revenue_id.sales_type == sales_type)
                total_revenue = sum(used_sales_type_revenue_ids.mapped("sales_type_revenue"))
                sheet.merge_range(row, 3, row, 4, "{}  (with discount)".format(sales_type), color_light_blue_format if sales_type != "not_set" else not_set_format)
                sheet.write(row, 5, "", color_light_blue_format if sales_type != "not_set" else not_set_format)
                sheet.write(row, 6, "", color_light_blue_format if sales_type != "not_set" else not_set_format)
                sheet.write(row, 7, "", color_light_blue_format if sales_type != "not_set" else not_set_format)
                sheet.write(row, 8, total_revenue, color_light_blue_format if sales_type != "not_set" else not_set_format)
                row += 1
            sheet.merge_range(row, 3, row, 4, "Total with discount", color_dark_blue_format)
            sheet.write(row, 5, "", color_dark_blue_format)
            sheet.write(row, 6, "", color_dark_blue_format)
            sheet.write(row, 7, "", color_dark_blue_format)
            sheet.write(row, 8, sum(invoice_ids.mapped("amount_total")), color_dark_blue_format)
            row += 1
        except Exception as exc:
            _logger.error(f"Error when creating xlsx timesheets report. {exc}")
