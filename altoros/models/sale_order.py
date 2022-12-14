from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_studio_sales_manager = fields.Selection(string="Sales Manager (Old)", selection=[
        ("Ilya Obritski", "Ilya Obritski"),
        ("Pavel Karatkevich", "Pavel Karatkevich"),
        ("Tatsiana Sushko", "Tatsiana Sushko"),
        ("Yuliya Kunts", "Yuliya Kunts"),
        ("Yury Yurchanka", "Yury Yurchanka"),
        ("Mikhail Shykavets", "Mikhail Shykavets"),
        ("Ekaterina Grishina", "Ekaterina Grishina"),
        ("Igor Aksinin", "Igor Aksinin"),
        ("Jan-Terje Nordlien", "Jan-Terje Nordlien"),
        ("Margaret Apanasevich", "Margaret Apanasevich")
    ])
