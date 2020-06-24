# -*- coding: utf-8 -*-

from odoo import fields, models, api


REV_MAP_FIELDS = {
    'x_studio_department_1_1': 'x_studio_revenue_1',
    'x_studio_department_2': 'x_studio_revenue_2',
    'x_studio_department_3': 'x_studio_revenue_3',
    'x_studio_department_4': 'x_studio_revenue_4',
    'x_studio_department_5': 'x_studio_revenue_5',
}


class AccountMoveLineRevenue(models.Model):
    _name = 'account.move.line.revenue'
    _description = "Account Move Line Revenue"
    _rec_name = 'move_line_id'

    move_line_id = fields.Many2one('account.move.line', 'Journal Item')
    move_id = fields.Many2one('account.move', related='move_line_id.move_id', store=True)
    currency_id = fields.Many2one('res.currency', related='move_line_id.company_currency_id',
                                  string='Currency', readonly=True)

    department = fields.Char('Department')
    balance = fields.Monetary('Balance', compute='_compute_amount', store=True)
    price_total = fields.Monetary('Total', compute='_compute_amount', store=True)
    price_subtotal = fields.Monetary('Subtotal', compute='_compute_amount', store=True)

    @api.depends('move_line_id', 'department',
                 'move_line_id.balance', 'move_line_id.price_total', 'move_line_id.price_subtotal',
                 'move_id.x_studio_department_1_1', 'move_id.x_studio_department_2',
                 'move_id.x_studio_department_3', 'move_id.x_studio_department_4',
                 'move_id.x_studio_department_5',

                 'move_id.x_studio_revenue_1', 'move_id.x_studio_revenue_2',
                 'move_id.x_studio_revenue_3', 'move_id.x_studio_revenue_4',
                 'move_id.x_studio_revenue_5', 'move_id.amount_untaxed')
    def _compute_amount(self):
        def _str_to_float(string):
            string = string.replace(',', '')
            return float(string)

        for record in self:
            amount_field = None
            move_id = record.move_id
            move_line_id = record.move_line_id

            if record.move_line_id and record.department:
                for department in REV_MAP_FIELDS:
                    if move_id[department] == record.department:
                        amount_field = REV_MAP_FIELDS[department]
                        break

            if amount_field and move_id.amount_untaxed:
                amount_department = _str_to_float(move_id[amount_field])
                ratio = amount_department / move_id.amount_untaxed
                record.balance = move_line_id.balance * ratio
                record.price_total = move_line_id.price_total * ratio
                record.price_subtotal = move_line_id.price_subtotal * ratio
            else:
                record.balance = move_line_id.balance
                record.price_total = move_line_id.price_total
                record.price_subtotal = move_line_id.price_subtotal
