from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ItemRequisitionInherit(models.Model):
    _inherit = 'stock.picking'
    _order = 'requisition_no DESC'

    picking_user = fields.Boolean(default=False)
    requisition_no = fields.Char(string='Requisition NO.', required=True, copy=False, readonly=True,
                                 default=lambda self: _('New'))
    requisition_date = fields.Date(string='Requisition Date', default=fields.Datetime.now, tracking=True)
    branch_id = fields.Many2one('res.branch', string='Branch', tracking=True)
    item_type = fields.Selection(
        [('warranty', 'Warranty'),
         ('non_warranty', 'Non Warranty')],
        string="Stock type")
    currency = fields.Many2one('res.currency', string='Currency')
    remark = fields.Text(string='Remark')
    reference = fields.Many2many('field.service', string='Service Order', domain="[('id','in',defaul_reference_id)]")
    defaul_reference_id = fields.Many2many('field.service', compute="_get_default_reference")
    warehouse_map = fields.Many2one('warehouse.mapping', string='Warehouse Mapping')

    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self._set_destination_warehouse(),
        check_company=True, readonly=True, required=True,
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

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True,
        default=lambda self: self._set_operation_type_id(),
        states={'draft': [('readonly', False)]})

    partner_id = fields.Many2one('res.partner', default=lambda self: self._get_default_user())

    def _get_default_user(self):
        if 'default_picking_user' in self.env.context.keys() and self.env.context.get('default_picking_user') == True:
            return self.env.user.partner_id
        else:
            None

    @api.depends('state')
    def _get_default_reference(self):
        get_approved_so = self.env['field.service'].sudo().search([('state', '=', 'approval')])
        get_domain_so = self.env['stock.picking'].sudo().search([('state', '!=', 'draft')])
        get_final_so = get_approved_so - get_domain_so.reference
        self.defaul_reference_id = get_final_so.ids

    @api.onchange('picking_type_id')
    def _set_destination_warehouse(self):
        if 'default_picking_user' in self.env.context.keys() and self.env.context.get(
                'default_picking_user') == True:
            logged_user_warehouse = self.env.user.property_warehouse_id.lot_stock_id
            self.location_dest_id = logged_user_warehouse
        else:
            None

    @api.onchange('branch_id', 'item_type')
    def onchange_branch_id(self):
        if 'default_picking_custom' in self.env.context.keys() and self.env.context.get(
                'default_picking_custom') == True:
            for rec in self:
                s_location = self.env['warehouse.mapping'].search(
                    [('branch_id', '=', rec.branch_id.id), ('stock_type', '=', rec.item_type)]).allowed_location.ids

                return {'domain': {
                    'location_id': [('id', 'in', s_location)]}}
        else:
            None

    @api.onchange('picking_type_id')
    def _get_default_location_id(self):
        if 'default_picking_user' in self.env.context.keys() and self.env.context.get(
                'default_picking_user') == True:
            None

        else:
            self.location_id = self.env['stock.picking.type'].search(
                [('id', '=', self.picking_type_id.id)]).default_location_src_id

    def _set_operation_type_id(self):

        if 'default_picking_user' in self.env.context.keys() and self.env.context.get(
                'default_picking_user') == True:
            return self.env['stock.picking.type'].search(
                [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
                 ('code', '=', 'internal')]).id
        else:
            return super(ItemRequisitionInherit, self)._set_operation_type_id()

    @api.model
    def create(self, vals):
        if vals.get('requisition_no', _('New')) == _('New'):
            vals['requisition_no'] = self.env['ir.sequence'].next_by_code('item.requisition') or _('New')
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
