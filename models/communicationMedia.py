
from odoo import api, fields, models, _
from datetime import date


class CommunicationMedia(models.Model):
    _name = 'communication.media'
    _description = 'Communication Media'
    _rec_name = "c_media"

    c_media = fields.Char(string='Communication media')