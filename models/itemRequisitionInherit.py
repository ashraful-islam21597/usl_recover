from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItemRequisitionInherit(models.Model):
    # _description = "Item Requisition Warranty Inherit"
    _inherit = 'stock.picking'
    # _rec_name = 'requisition_no'
    # _order = 'requisition_no DESC'

    requisition_no = fields.Char(string='Requisition NO.', required=True, copy=False, readonly=True,
                                 default=lambda self: _('New'))
    requisition_date = fields.Date(string='Requisition Date', default=fields.Datetime.now, tracking=True)
    branch = fields.Many2one('res.branch', string='Branch', tracking=True)
    item = fields.Selection(
        [('warranty', 'Warranty'),
         ('non warranty', 'Non Warranty')],
        string="Item Status", readonly=1)
    # item_status = fields.Char(default='non warranty', string='Item Status', readonly=True)
    employee = fields.Many2one('res.partner', string='Employee', tracking=True)
    currency = fields.Many2one('res.currency', string='Currency')
    remark = fields.Text(string='Remark')
    reference = fields.Many2many('field.service', string='Service Order', domain="[('id','in',defaul_reference_id)]")
    defaul_reference_id = fields.Many2many('field.service', compute="_get_default_reference")
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self._set_destination_warehouse(),
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    @api.depends('state')
    def _get_default_reference(self):
        get_approved_so = self.env['field.service'].sudo().search([('state', '=', 'approval')])
        get_domain_so = self.env['stock.picking'].sudo().search([('state', '!=', 'draft')])
        get_final_so = get_approved_so - get_domain_so.reference
        self.defaul_reference_id = get_final_so.ids

    @api.onchange('picking_type_id')
    def _set_destination_warehouse(self):
        logged_user_warehouse = self.env.user.property_warehouse_id.lot_stock_id
        self.location_dest_id = logged_user_warehouse

    @api.model
    def create(self, vals):
        if vals.get('requisition_no', _('New')) == _('New'):
            vals['requisition_no'] = self.env['ir.sequence'].next_by_code('stock.picking.inherit') or _('New')
        res = super(ItemRequisitionInherit, self).create(vals)
        # res.set_line_number()
        return res

    @api.onchange('reference')
    def onchange_reference(self):
        for rec in self:
            rec.move_ids_without_package = [(6, 0, [])]
            line = [(5, 0, 0)]
            for so in rec.reference:
                dr = self.env['diagnosis.repair'].search([('order_id', '=', so.ids[0])])
                for i in dr.diagnosis_repair_lines_ids:
                    line.append((0, 0, {
                        'product_id': i.part.id,
                        'so_reference': so.ids[0],
                        'description_picking': i.part.product_tmpl_id.name,
                        'name': i.part.product_tmpl_id.name,
                        'product_uom': i.part.product_tmpl_id.uom_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                    }))
                rec.move_ids_without_package = line

    def write(self, vals):
        res = super(ItemRequisitionInherit, self).write(vals)
        # self.set_line_number()
        return res
