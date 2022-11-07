from odoo import api, fields, models, _
import datetime
from odoo.exceptions import ValidationError


class AdvanceItemRequisitionWarrantyInherit(models.Model):
    _inherit = "stock.picking"
    # _rec_name = 'requisition_no_1'
    # _order = 'requisition_no_1 desc'

    requisition_no_1 = fields.Char(readonly=True,
                                   default=lambda self: _('New'), string="Requisition No")
    requisition_date = fields.Date(default=fields.Datetime.now, string="Requisition Date", tracking=True)
    item = fields.Selection(
        [('warranty', 'Warranty'),
         ('non warranty', 'Non Warranty')],
        string="Item Status", readonly=1)

    branch = fields.Many2one('res.branch', string="Branch")
    employee = fields.Many2one('res.users', string="Employee", tracking=True)
    currency = fields.Many2one('res.currency', string="Currency")
    remark = fields.Text(string="Remark")

    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self._set_destination_warehouse(),
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True,
        default=lambda self: self._set_operation_type_id(),
        states={'draft': [('readonly', False)]})

    @api.model
    def create(self, vals):
        if vals.get('requisition_no_1', _('New')) == _('New'):
            vals['requisition_no_1'] = self.env['ir.sequence'].next_by_code('stock.picking.inherit') \
                                     or _('New')
        res = super(AdvanceItemRequisitionWarrantyInherit, self).create(vals)
        return res

    @api.onchange('picking_type_id')
    def _set_destination_warehouse(self):
        logged_user_warehouse = self.env.user.property_warehouse_id.lot_stock_id
        self.location_dest_id = logged_user_warehouse

    def _set_operation_type_id(self):
        return self.env['stock.picking.type'].search([('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
                                                      ('code', '=', 'internal')]).id

