from odoo import api, models, fields
from odoo.tools.safe_eval import safe_eval

class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _get_tracked_fields(self):
        """ Return a structure of tracked fields for the current model.
            :return dict: a dict mapping field name to description, containing on_change fields
            If model has track_all_fields=True - add to track all the fields that are located in the view
            If model has fields_to_track - add to track fields in the fields_to_track list
        """
        tracked_fields = []
        if getattr(self, "track_all_fields", None):
            fields_on_view = self.fields_view_get()["fields"]
            for name, field in self._fields.items():
                if name in fields_on_view:
                    tracked_fields.append(name)
        elif getattr(self, "fields_to_track", None):
            tracked_fields = safe_eval(self.fields_to_track)
        else:
            for name, field in self._fields.items():
                tracking = getattr(field, "tracking", None) or getattr(field, "track_visibility", None)
                if tracking:
                    tracked_fields.append(name)

        if tracked_fields:
            return self.fields_get(tracked_fields)
        return {}

    @api.model
    def _send_message_to_chatter(self):
        """Sends message to model chatter if record is unlinked|created"""
        self.ensure_one()
        tracked_fields = self._get_tracked_fields()
        old_values = {}
        for field in tracked_fields:
            old_values[field] = 0
        changes, tracking_value_ids = self._message_track(tracked_fields, old_values)
        if changes:
            self.message_post(body=f"Deleted/created line in '{self._description}' with tracked fields:",
                              tracking_value_ids=tracking_value_ids)


class Message(models.Model):
    _inherit = "mail.message"

    routed_from_model = fields.Char(string="Routed from model")
    routed_model_id = fields.Integer(string="Routed model id")

    def create(self, vals_list):
        """Sends copy of tracking message to model from route"""
        records = super().create(vals_list)
        message_routes = {
            "rate.employee.timesheet": "account.move",
            "department.rate": "account.move",
            "account.move.line": "account.move",
        }
        for record in records:
            if record.model in message_routes and record.tracking_value_ids:
                model_id = self.env[record.model].search([("id", "=", record.res_id)], limit=1)
                model_fields = model_id.fields_get()
                related_fields = []
                for field, values in model_fields.items():
                    if values.get("relation") == message_routes[record.model]:
                        related_fields.append(field)
                if model_id and related_fields:
                    for related_field in related_fields:
                        records.copy({"model": message_routes[record.model],
                                      "body": record.body if record.body else f"Changed line in '{model_id._description}' with tracked fields:",
                                      "routed_from_model": record.model,
                                      "routed_model_id": record.res_id,
                                      "res_id": model_id[related_field].id,
                                      "tracking_value_ids": record.tracking_value_ids})
        return records