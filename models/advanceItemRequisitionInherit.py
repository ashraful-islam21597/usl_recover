from odoo import api, fields, models, _
import datetime
from odoo.exceptions import ValidationError


class AdvanceItemRequisitionInherit(models.Model):
    _inherit = "stock.picking"
    _order = 'requisition_no_1 desc'

    picking_custom = fields.Boolean(default=False)
    partner_id = fields.Many2one('res.partner', default=lambda self: self._get_default_partner())
    requisition_no_1 = fields.Char(readonly=True,
                                   default=lambda self: _('New'), string="Requisition No")
    requisition_date = fields.Date(default=fields.Datetime.now, string="Requisition Date", tracking=True)
    item_type = fields.Selection(
        [('warranty', 'Warranty'),
         ('non_warranty', 'Non Warranty')],
        string="Stock type")
    branch_id = fields.Many2one('res.branch', string='Branch', tracking=True)
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
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self._get_default_location_id(),
        check_company=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]}
    )

    show_submit_for_approval = fields.Boolean(
        compute='_compute_show_submit_for_approval',
        help='Technical field used to compute whether the button "Request For Approve" should be displayed.')

    state = fields.Selection(selection_add=[
        ('submitted_for_approval', 'Submitted For Approval'),
        ('approved', 'Approved'),
        ('waiting',)
    ])

    @api.model
    def create(self, vals):
        if vals.get('requisition_no_1', _('New')) == _('New'):
            vals['requisition_no_1'] = self.env['ir.sequence'].next_by_code('advance.item.requisition') \
                                       or _('New')
        res = super(AdvanceItemRequisitionInherit, self).create(vals)
        return res

    def _get_default_partner(self):
        if 'default_picking_custom' in self.env.context.keys() and self.env.context.get(
                'default_picking_custom') == True:
            return self.env.user.partner_id
        else:
            None

    @api.onchange('picking_type_id')
    def _get_default_location_id(self):
        if 'default_picking_custom' in self.env.context.keys() and self.env.context.get(
                'default_picking_custom') == True:
            None

        else:
            self.location_id = self.env['stock.picking.type'].search(
                [('id', '=', self.picking_type_id.id)]).default_location_src_id

    @api.onchange('picking_type_id')
    def _set_destination_warehouse(self):
        if 'default_picking_custom' in self.env.context.keys() and self.env.context.get(
                'default_picking_custom') == True:
            logged_user_warehouse = self.env.user.property_warehouse_id.lot_stock_id
            self.location_dest_id = logged_user_warehouse
        else:
            None

    def _set_operation_type_id(self):

        if 'default_picking_custom' in self.env.context.keys() and self.env.context.get(
                'default_picking_custom') == True:

            return self.env['stock.picking.type'].search(
                [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
                 ('code', '=', 'internal')]).id

        else:
            return super(AdvanceItemRequisitionInherit, self)._set_operation_type_id()

    @api.depends('state', 'move_lines')
    def _compute_show_submit_for_approval(self):
        for picking in self:
            if not picking.move_lines and not picking.package_level_ids:
                picking.show_submit_for_approval = False
            elif not picking.immediate_transfer and picking.state == 'draft':
                picking.show_submit_for_approval = True
            elif picking.state != 'draft' or not picking.id:
                picking.show_submit_for_approval = False
            else:
                picking.show_submit_for_approval = True

    def action_submit_for_approval(self):
        for rec in self:
            rec.state = 'submitted_for_approval'

    def action_approved(self):
        for rec in self:
            rec.state = 'approved'

    @api.depends('partner_id')
    def _get_partner(self):
        partner = self.env['res.users'].browse(self.env.uid).partner_id
        for rec in self:
            rec.partner_id = partner.id

    @api.onchange('picking_type_id', 'partner_id')
    def _onchange_picking_type(self):
        super(AdvanceItemRequisitionInherit, self)._onchange_picking_type()
        if self.picking_custom == True:
            self.location_id = None
