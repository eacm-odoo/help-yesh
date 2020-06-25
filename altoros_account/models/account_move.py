# -*- coding: utf-8 -*-

from odoo import fields, models, api

DEPARTMENT_FIELDS = [
    'x_studio_department_1_1',
    'x_studio_department_2',
    'x_studio_department_3',
    'x_studio_department_4',
    'x_studio_department_5',
]


class AccountMove(models.Model):
    _inherit = 'account.move'

    revenue_ids = fields.One2many('account.move.line.revenue', 'move_id', string="Invoice Line Revenue")
    split_revenue = fields.Boolean("Split revenue by Department?", default=True)

    def update_aml_revenue(self):
        for record in self:
            # All departments of this invoice
            move_departments = [record[dep] for dep in DEPARTMENT_FIELDS if record[dep]]

            for line in record.invoice_line_ids:
                # Delete revenue lines with outdated departments
                outdated_lines = line.revenue_ids.filtered(lambda x: x.department not in move_departments)
                outdated_lines.unlink()

                line_departments = [rev.department for rev in line.revenue_ids]
                new_departments = list(set(move_departments) - set(line_departments))
                if new_departments:
                    line.write({
                        'revenue_ids': [(0, 0, {'move_line_id': line.id, 'department': x})
                                        for x in new_departments]
                    })
                elif not move_departments and not line.revenue_ids:
                    line.write({
                        'revenue_ids': [(0, 0, {'move_line_id': line.id})]
                    })

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AccountMove, self).create(vals_list)
        records.update_aml_revenue()
        return records

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        self.update_aml_revenue()
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    revenue_ids = fields.One2many('account.move.line.revenue', 'move_line_id', string="Invoice Line Revenue")
