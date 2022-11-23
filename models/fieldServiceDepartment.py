# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class FieldServiceDepartment(models.Model):
    _name = "field.service.department"
    _description = "Field Service Department"
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)




