import logging
import re
from datetime import datetime
from datetime import timedelta

from odoo import models

_logger = logging.getLogger(__name__)


class TimesheetsToApproveReportXlsx(models.AbstractModel):
    _name = "report.altoros.timesheets_to_approve_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, project_task_ids):
        """Generating data for the InvoicesChanges report."""
        try:
            report_name = "Timesheets to approve"
            start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date() if data.get("start_date") else False
            end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date() if data.get("end_date") else False
            if not start_date and not end_date:
                end_date = datetime.today().date()
                start_date = end_date - timedelta(days=30)

            data_to_report_grouped_by_project = {}
            for project_task_id in project_task_ids:
                for timesheet_id in project_task_id.timesheet_ids:
                    if start_date <= timesheet_id.date <= end_date:
                        data_to_report_grouped_by_project.setdefault(project_task_id.project_id, {})
                        data_to_report_grouped_by_project[project_task_id.project_id].setdefault(timesheet_id.employee_id, {})
                        data_to_report_grouped_by_project[project_task_id.project_id][timesheet_id.employee_id].setdefault(
                            (timesheet_id.date, timesheet_id.task_id), 0.0)

                        data_to_report_grouped_by_project[project_task_id.project_id][timesheet_id.employee_id][(timesheet_id.date, timesheet_id.task_id)] += timesheet_id.unit_amount

            sorted_data_to_report = dict(sorted(data_to_report_grouped_by_project.items(), key=lambda item: int(re.match(r'\d+', item[0].name).group())))
            for project_id, project_data in sorted_data_to_report.items():
                sheet = workbook.add_worksheet(project_id.name)
                header_format = workbook.add_format(
                    {"align": "left", "font_size": 14, "bold": True, "font_name": "Arial", "underline": True,
                     "color": "#c9211e"})
                table_top_left_format = workbook.add_format({"align": "left", "top": 1, "font_size": 11, "bold": True,
                                                             "font_name": "Arial", "left": 1})
                table_top_right_format = workbook.add_format({"align": "left", "top": 1, "font_size": 11, "bold": False,
                                                              "font_name": "Arial", "right": 1})
                table_left_format = workbook.add_format({"align": "left", "font_size": 11, "bold": True,
                                                         "font_name": "Arial", "left": 1})
                table_right_format = workbook.add_format({"align": "left", "font_size": 11, "bold": False,
                                                          "font_name": "Arial", "right": 1})
                table_bottom_left_format = workbook.add_format({"align": "left", "font_size": 11, "bold": True,
                                                                "font_name": "Arial", "left": 1, "bottom": 1})
                table_bottom_right_format = workbook.add_format({"align": "left", "font_size": 11, "bold": False,
                                                                 "font_name": "Arial", "right": 1, "bottom": 1})
                table_header_format = workbook.add_format(
                    {"align": "center", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                     "text_wrap": False, "fg_color": "#87CEEB", "font_size": 10})
                table_format_align_left = workbook.add_format(
                    {"align": "left", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                     "font_size": 10, "num_format": "0.00"})
                table_format_align_right = workbook.add_format(
                    {"align": "right", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                     "font_size": 10, "num_format": "0.00"})
                color_format_align_left = workbook.add_format(
                    {"align": "left", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                     "bold": True, "fg_color": "#C7D0CC", "font_size": 10, "num_format": "0.00"})
                color_format_align_right = workbook.add_format(
                    {"align": "right", "valign": "top", "border": 1, "font_name": "Arial", "text_wrap": False,
                     "bold": True, "fg_color": "#C7D0CC", "font_size": 10, "num_format": "0.00"})
                table_total_format_align_center = workbook.add_format(
                    {"align": "center", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                     "text_wrap": False, "fg_color": "#87CEEB", "font_size": 10, "num_format": "0.00"})
                table_total_format_align_right = workbook.add_format(
                    {"align": "right", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                     "text_wrap": False, "fg_color": "#87CEEB", "font_size": 10, "num_format": "0.00"})
                not_approved_format = workbook.add_format(
                    {"align": "center", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                     "text_wrap": False, "bg_color": "#F5A9A9", "font_size": 10})
                approved_format = workbook.add_format(
                    {"align": "center", "valign": "vcenter", "border": 1, "bold": True, "font_name": "Arial",
                     "text_wrap": False, "bg_color": "#74B998", "font_size": 10})

                sheet.set_column(1, 2, 18)
                sheet.set_column(3, 3, 24)
                sheet.set_column(4, 9, 18)

                sheet.merge_range(1, 1, 1, 2, report_name, header_format)

                sheet.write("G2", "Not approved")
                sheet.conditional_format("G2", {"type": "text",
                                                "criteria": "begins with",
                                                "value": "Approved",
                                                "format": approved_format})
                sheet.conditional_format("G2", {"type": "text",
                                                "criteria": "begins with",
                                                "value": "Not",
                                                "format": not_approved_format})
                sheet.data_validation("G2", {"validate": "list", "source": ["Not Approved", "Approved"]})

                sheet.merge_range(3, 1, 3, 2, "Prepared by:", table_top_left_format)
                sheet.merge_range(3, 3, 3, 4, self.env.user.name, table_top_right_format)
                sheet.merge_range(4, 1, 4, 2, "Date:", table_left_format)
                sheet.merge_range(4, 3, 4, 4, datetime.strftime(datetime.today().date(), "%d-%m-%Y"), table_right_format)
                sheet.merge_range(5, 1, 5, 2, "Department:", table_left_format)
                sheet.merge_range(5, 3, 5, 4, data.get("department"), table_right_format)
                sheet.merge_range(6, 1, 6, 2, "Project:", table_left_format)
                sheet.merge_range(6, 3, 6, 4, project_id.name, table_right_format)
                sheet.merge_range(7, 1, 7, 2, "Reporting period:", table_bottom_left_format)
                sheet.merge_range(7, 3, 7, 4, f"{start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}", table_bottom_right_format)

                sheet.write(9, 1, "Developer", table_header_format)
                sheet.write(9, 2, "Date", table_header_format)
                sheet.write(9, 3, "Task", table_header_format)
                sheet.write(9, 4, "Sum of total hours", table_header_format)
                sheet.write(9, 5, "Non-Billable", table_header_format)
                sheet.write(9, 6, "Total Billable", table_header_format)
                row = 10

                header_employee = False
                total_billable_for_project = 0
                for employee_id, timesheet_data in project_data.items():
                    timesheet_data = dict(sorted(timesheet_data.items(), key=lambda item: item[0][0]))
                    sum_of_total_hours, total_billable = 0, 0
                    for (date, task_id), total_hours in timesheet_data.items():
                        if employee_id != header_employee:
                            sheet.write(row, 1, employee_id.name, table_format_align_left)
                        else:
                            sheet.write(row, 1, "", table_format_align_left)
                        header_employee = employee_id

                        sheet.write(row, 2, datetime.strftime(date, "%d-%m-%Y"), table_format_align_left)
                        sheet.write(row, 3, task_id.name, table_format_align_left)
                        sheet.write(row, 4, total_hours, table_format_align_right)
                        sheet.write(row, 5, "", table_format_align_right)
                        sheet.write(row, 6, total_hours, table_format_align_right)

                        sum_of_total_hours += total_hours
                        total_billable += total_hours
                        row += 1

                    sheet.write(row, 1, f"{employee_id.name} Total", color_format_align_left)
                    sheet.write(row, 2, "", color_format_align_left)
                    sheet.write(row, 3, "", color_format_align_left)
                    sheet.write(row, 4, float(sum_of_total_hours), color_format_align_right)
                    sheet.write(row, 5, "", color_format_align_right)
                    sheet.write(row, 6, total_billable, color_format_align_right)
                    total_billable_for_project += total_billable
                    row += 1

                sheet.write(row, 1, f"Total", table_total_format_align_center)
                sheet.write(row, 2, "", table_total_format_align_center)
                sheet.write(row, 3, "", table_total_format_align_center)
                sheet.write(row, 4, "", table_total_format_align_right)
                sheet.write(row, 5, "", table_total_format_align_right)
                sheet.write(row, 6, total_billable_for_project, table_total_format_align_right)

        except Exception as exc:
            _logger.error(f"Error when creating xlsx report. {exc}")

