# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    invoice_department = fields.Char(string="Production Department")

    def _select(self):
        select = super()._select()

        new_select = select.replace("line.balance", "line_revenue.balance")\
            .replace("line.price_total", "line_revenue.price_total")\
            .replace("line.price_subtotal", "line_revenue.price_subtotal")

        return new_select + ", line_revenue.department as invoice_department"

    def _from(self):
        return super()._from() +\
               " RIGHT JOIN account_move_line_revenue line_revenue ON line_revenue.move_line_id = line.id"

    def _group_by(self):
        return super()._group_by() + ", invoice_department, line_revenue.balance, line_revenue.price_total, line_revenue.price_subtotal"
