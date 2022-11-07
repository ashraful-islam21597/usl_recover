from odoo import api, fields, models, _
from datetime import date


class StockPickingOperation(models.Model):
    _inherit = "stock.picking"
    _order = 'name desc'
    service_order_id = fields.Many2one('field.service', string="Service Order")
    transfer_to_branch = fields.Many2one('res.branch', string="To Branch")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approval', 'Approval'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'), ])



    # def action_confirm(self):
    #     for rec in self:
    #         if rec.state == "draft":
    #             rec.state = 'approval'

    @api.onchange('service_order_id')
    def onchange_order(self):
        user = self.env['res.users'].browse(self._context.get('uid'))
        # self.move_ids_without_package = [(5, 0, 0)]
        val_list = []
        warehouse_data = self.env['stock.warehouse'].search([
            ('branch_id', '=', self.transfer_to_branch.id),
            ('company_id', '=', user.company_id.id),

        ])
        for rec in self.env['field.service'].sudo().search([('order_no', '=', self.service_order_id.display_name)]):
            vals = (0, 0, {
                'product_id': rec.product_id.id,
                'description_picking': rec.product_id.product_tmpl_id.name,
                'name': rec.product_id.product_tmpl_id.name,
                'product_uom': rec.product_id.product_tmpl_id.uom_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'branch_id': user.branch_id.id,
                'order_ref': self.service_order_id.customer_id.id,

            })
            print(self.service_order_id.customer_id.id)
            val_list.append(vals)

        self.move_ids_without_package = val_list

    @api.onchange("transfer_to_branch")
    def onchange_transfering_branch(self):

        user = self.env['res.users'].browse(self._context.get('uid'))
        # print(user.warehouse_id.id)
        print(self.transfer_to_branch.id, user.company_id)
        warehouse_data = self.env['stock.warehouse'].search([
            ('branch_id', '=', self.transfer_to_branch.id),
            ('company_id', '=', user.company_id.id),

        ])
        # stock_location_data = self.env['stock.location'].search([
        #     ('location_id', '=', warehouse_data.code),
        #     ('name', '=', 'Stock'),
        #     ('branch_id', '=', self.transfer_to_branch.id),
        #     ('company_id', '=', user.company_id.id),
        #     ('warehouse_id', '=', warehouse_data.id),
        # ])
        s = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', warehouse_data.id),
             ('code', '=', 'incoming')], limit=1).default_location_dest_id.id
        print(s)
        self.location_dest_id = s
        # self.partner_id = warehouse_data.create_uid.id

    @api.model
    def create(self, vals):
        res = super(StockPickingOperation, self).create(vals)

        y = vals.get('service_order_id')
        so = self.env['field.service'].sudo().search([('id', '=', y)])
        print(res.picking_type_id.code)
        if res.picking_type_id.code == 'incoming':
            so.receive_customer = True
            so.item_receive_status = "Received"
            so.product_receive_date = self.scheduled_date
        elif res.picking_type_id.code == 'internal':
            so.so_transfer = True
            so.item_receive_status = "Transfered"
        return res

    def action_operation(self):
        form_id = self.env.ref('usl_service_erp.view_picking_form_field_service_transfer').id,
        tree_id = self.env.ref('usl_service_erp.view_picking_tree_field_service_transfer').id,
        p = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
             ('code', '=', 'internal')], limit=1)
        user = self.env['res.users'].browse(self._context.get('uid'))
        print("x", p)

        return {

            'type': 'ir.actions.act_window',
            'name': _('Item Transfer'),
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            # 'context': {'default_picking_type_id': p.id},
            'res_model': 'stock.picking',
            'context': {'default_picking_type_id': p.id,
                        'default_service_order_id': self.service_order_id.id},
            'domain': [('picking_type_id', '=', p.id)],

            'res_id': self.id,

        }


    def action_transfer_order_receive_operation(self):
        form_id = self.env.ref('usl_service_erp.view_picking_form_field_service_transfer_order_receive').id,
        tree_id = self.env.ref('usl_service_erp.view_picking_tree_field_service_transfer_order_receive').id,

        p = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
             ('code', '=', 'internal')], limit=1)
        user = self.env['res.users'].browse(self._context.get('uid'))
        print(self.id, user.id)

        return {

            'type': 'ir.actions.act_window',
            'name': _('Item Transfer receive'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],

            'res_model': 'stock.picking',
            #'context': {'default_picking_type_id': p.id,'default_branch': user.branch_id.id,
                        #'default_service_order_id': self.service_order_id.id},
            'domain': [('transfer_to_branch', '=',user.branch_id.id)],

            # 'res_id': self.id,

        }



    def action_operation_receive(self):
        form_id = self.env.ref('usl_service_erp.view_picking_form_field_service_receive').id,
        tree_id = self.env.ref('usl_service_erp.view_picking_tree_field_service_receive').id,
        p = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
             ('code', '=', 'incoming')], limit=1)
        user = self.env['res.users'].browse(self._context.get('uid'))
        return {

            'type': 'ir.actions.act_window',
            'name': _('Item Receive'),
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'res_model': 'stock.picking',
            'context': {'default_picking_type_id': p.id,
                        'default_service_order_id': self.service_order_id.id},
            'domain': [('picking_type_id', '=', p.id)],

            'res_id': self.id,
        }


class stockmove(models.Model):
    _inherit = 'stock.move'
    order_ref = fields.Many2one('res.partner', string="Receive from")

    # @api.onchange("order_ref")
    # def onchange_transfering_branch(self):
    #     user = self.env['res.users'].browse(self._context.get('uid'))
    #     # print(user.warehouse_id.id)
    #     print(self.transfer_to_branch.id, user.company_id)
    #     warehouse_data = self.env['stock.warehouse'].search([
    #         ('branch_id', '=', self.transfer_to_branch.id),
    #         ('company_id', '=', user.company_id.id),
    #
    #     ])
    #     s = self.env['stock.picking.type'].search(
    #         [('warehouse_id', '=', warehouse_data.id),
    #          ('code', '=', 'incoming')], limit=1).default_location_dest_id.id
    #     print(s)
    #     self.location_dest_id = s
    #     self.partner_id = warehouse_data.create_uid.id

# 'res_id': record_id,
# but if you are using more then one view
# you must use views to pass mutliple ids
# 'views': [(form_id, 'form'), (tree_id, 'tree')],
# and to specify the search view use
# 'search_view_id': search_view_id,

# 'name': _('Item Receive'),
# 'type': 'ir.actions.act_window',
# 'res_model': 'stock.picking',
# 'view_type': 'form',
# 'view_mode': 'form',
# 'view_id': form_id,
# 'context': {'default_picking_type_id': p.id },
# 'target': 'current',
