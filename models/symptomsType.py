from odoo import api, fields, models, _


from odoo import api, fields, models, _


class SymptomsType(models.Model):
    _name = "symptoms.type"
    _description = "Symptoms Type"
    _rec_name = "symptom"
    symptom = fields.Char(string='symptom')
    active = fields.Boolean(string='Active', default=True, copy=False)


class ReasonType(models.Model):
    _name = "reasons.type"
    _rec_name = "reason"
    reason = fields.Char(string='Reason')
    active = fields.Boolean(string='Active', default=True, copy=False)