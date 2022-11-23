from odoo import api, fields, models, _


class ItemConsumption(models.Model):
    _name = 'item.consumption'
    _description = 'Item Consumption'

    order_id = fields.Many2one('field.service', string="Service Order", default=lambda self: self.id)
    item_consumption_line_ids = fields.One2many('item.consumption.lines', 'item_consumption_id')
    diagnosis_repair_ids = fields.Many2one('diagnosis.repair')

    @api.onchange('order_id')
    def onchange_order_id(self):
        for rec in self:
            rec.item_consumption_line_ids = [(6, 0, [])]
            line = [(5, 0, 0)]
            for so in rec.order_id:
                dr = self.env['diagnosis.repair'].search([('order_id', '=', so.ids[0])])
                for i in dr.diagnosis_repair_lines_ids:
                    line.append((0, 0, {
                        'part': i.part.id,
                    }))
                rec.item_consumption_line_ids = line


class ItemConsumptionLines(models.Model):
    _name = "item.consumption.lines"
    _description = "Item Consumption Lines"

    item_consumption_id = fields.Many2one('item.consumption')
    part = fields.Many2one('product.product', string="Part")
    qty = fields.Integer(string="Quantity")
    consumption_status = fields.Selection(
        [('used', 'Used'),
         ('unused', 'Unused')],
        string="Consumption Status"
    )
    bad_ct_serial_no = fields.Char(string="Bad CT/Serial No")
    good_ct_serial_no = fields.Char(string="Good CT/Serial No")
    material_request_no = fields.Char(string="Material Request No")
    purchase_order_no = fields.Char(string="Purchase Order No")
    shipping_date = fields.Datetime(string="Shipping Date")
    remark = fields.Char(string="Remark")
