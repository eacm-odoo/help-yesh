{
    "name": "Altoros",
    "summary": "Altoros module",
    "version": "1.0.1",
    "description": """ Altoros module """,
    "depends": [
        "base",
        "hr",
        "project",
        "account",
        "stock_account",
        "account_accountant",
        "timesheet_grid",
        "planning",
        "l10n_generic_coa",
        "sale_management",
        "report_xlsx",
    ],
    "author": "iCode",
    "license": "OPL-1",
    "website": "https://icode.by",
    "data": [
        "security/ir.model.access.csv",
        # views
        "views/rate_employee_views.xml",
        "views/account_move_views.xml",
        "views/project_project_views.xml",
        "views/account_account_views.xml",
        "views/res_partner_views.xml",
        "views/project_task_views.xml",
        "views/sale_order_views.xml",
        "views/cash_flow_analytics_view.xml",
        "views/assets.xml",
        # wizard
        "wizard/edit_opening_balance_wizard_view.xml",
        "wizard/generate_cash_flow_analytics_wizard_view.xml",
        "wizard/timesheet_filling_views.xml",
        "wizard/invoices_changes_wizard_views.xml",
        "wizard/timesheets_to_approve_wizard.xml",
        "wizard/invoice_selection_wizard_view.xml",
        # data
        "data/product_product_data.xml",
        # report
        "report/action_report.xml",

    ],
    'qweb': [
        'static/src/xml/cash_flow_generate.xml',
    ],
}
