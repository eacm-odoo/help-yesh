def migrate(cr, version):
    #cr.execute("UPDATE ir_model_fields SET state='base' WHERE state='manual' and id in (select res_id from ir_model_data where (module like 'altoros' or module like 'odoo_email_cc_bcc' or  module like 'report_xlsx') and model like 'ir.model.fields')")
    cr.execute("UPDATE ir_model_fields SET state='base' WHERE state='manual'")
    cr.execute("UPDATE ir_model SET state='base' WHERE state='manual' and id in (select res_id from ir_model_data where (module like 'altoros' or module like 'odoo_email_cc_bcc' or  module like 'report_xlsx') and model like 'ir.model')")
    cr.execute("DELETE from ir_model_fields WHERE name like 'has_abnormal_deferred_dates'")
