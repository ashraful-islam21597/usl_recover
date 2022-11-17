from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import UserError


class StockPickingOperation(models.Model):
    _inherit = "stock.picking"
    _rec_name = 'name'
    _order = 'name desc'
    serial = fields.Char(string='Order No', required=True, copy=False, readonly=True,
                         default=lambda self: _('New'))
    service_order_id = fields.Many2one('field.service', string="Service Order")
    transfer_to_branch = fields.Many2one('res.branch', string="To Branch")
    contact_person = fields.Many2one('res.partner')
    custom_operation_receive = fields.Boolean(default=False)
    custom_operation_transfer = fields.Boolean(default=False)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True, readonly=True,
        default=lambda self: self._set_operation_type(),
        states={'draft': [('readonly', False)]})
    received = fields.Boolean(related='service_order_id.receive_customer', string="received status")
    branch_id = fields.Many2one('res.branch', default=lambda self: self.env.user.branch_id)

    def _set_operation_type(self):
        if 'default_custom_operation_transfer' in self.env.context.keys() and self.env.context.get(
                'default_custom_operation_transfer') == True:
            return self.env['stock.picking.type'].search(
                [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
                 ('code', '=', 'internal')], limit=1).id
        elif 'default_custom_operation_receive' in self.env.context.keys() and self.env.context.get(
                'default_custom_operation_receive') == True:

            return self.env['stock.picking.type'].search(
                [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
                 ('code', '=', 'incoming')], limit=1).id
        else:
            None

    @api.onchange('service_order_id')
    def onchange_service_order(self):
        user = self.env['res.users'].browse(self._context.get('uid'))
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
                'order_id': self.service_order_id.id,
                'serial_no': self.service_order_id.imei_no

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
        contact_person=self.env['res.users'].search([('branch_id','=',self.transfer_to_branch.id)])
        contact_person = self.env['res.users'].search([('branch_id', '=', self.transfer_to_branch.id)])
        print(contact_person.name)
        #contact_person = self.env['res.partner'].search([('user_id', '=', contact_person.id)])
        print(contact_person.name)
        s = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', warehouse_data.id),
             ('code', '=', 'incoming')], limit=1).default_location_dest_id
        if s:
            self.location_dest_id = s
            self.partner_id=contact_person.partner_id

    @api.model
    def create(self, vals):
        res = super(StockPickingOperation, self).create(vals)
        if vals.get('serial', _('New')) == _('New'):
            if res.picking_type_id.code == 'incoming':
                val = self.env['ir.sequence'].next_by_code('so.receive') or _('New')
                res.name = val

        if res.picking_type_id.code == 'internal':
            val = self.env['ir.sequence'].next_by_code('so.transfer') or _('New')
            res.name = val
        so_id = vals.get('service_order_id')
        so = self.env['field.service'].sudo().search([('id', '=', so_id)])
        if res.picking_type_id.code == 'incoming':
            so.receive_customer = True
            so.product_receive_date = res.scheduled_date

            so.item_receive_status = "Received"
            so.product_receive_date = res.scheduled_date
            print(so.product_receive_date, self.scheduled_date)
        elif res.picking_type_id.code == 'internal':

            so.so_transfer = True
            print(res.transfer_to_branch)
            so.current_branch = res.transfer_to_branch.id
            print(so.current_branch)
            so.item_receive_status = "Transfered"
        return res

    @api.model
    def write(self,vals):
        print(self.service_order_id)
        print(self.state)
        res = super(StockPickingOperation,self).write(vals)
        so = self.env['field.service'].sudo().search([('id', '=', self.service_order_id.id)])
        if self.picking_type_id.code == 'internal':
            print("write",self.state)
            so.so_transfer = True
            so.current_branch = self.transfer_to_branch.id
            so.item_receive_status = "Transfered"

        return res

    def action_cancel(self):
        super(StockPickingOperation, self).action_cancel()
        so = self.env['field.service'].sudo().search([('id', '=', self.service_order_id.id)])
        so.so_transfer = False
        print(so)



    def action_operation(self):
        print("working")
        form_id = self.env.ref('usl_service_erp.view_picking_form_field_service_transfer').id,
        tree_id = self.env.ref('usl_service_erp.view_picking_tree_field_service_transfer').id,
        p = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
             ('code', '=', 'internal')], limit=1)
        user = self.env['res.users'].browse(self._context.get('uid'))
        print("x", p)

        return {

            'name': ('Item Transfer'),
            'view_mode': 'tree,form',
            # 'view_type': 'tree,form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            # 'context': {'default_picking_type_id': p.id},
            'res_model': 'stock.picking',
            'context': {'default_picking_type_id': p.id, 'default_branch_id': user.branch_id.id,
                        'default_service_order_id': self.service_order_id.id},
            'type': 'ir.actions.act_window',
            'domain': [('picking_type_id', '=', p.id)],
            'target': 'current',
            'res_id': self.id,

        }

    def action_transfer_order_receive_operation(self):
        form_id = self.env.ref('usl_service_erp.view_picking_form_field_service_transfer_order_receive').id,
        tree_id = self.env.ref('usl_service_erp.view_picking_tree_field_service_transfer_order_receive').id,
        p = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', self.env.user.context_default_warehouse_id.id),
             ('code', '=', 'internal')], limit=1)
        user = self.env['res.users'].browse(self._context.get('uid'))

        return {

            'type': 'ir.actions.act_window',
            'name': _('Transfered Orders Receive'),
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],

            'res_model': 'stock.picking',
            'domain': [('transfer_to_branch', '=', user.branch_id.id),('state', '=','assigned')],


        }

    def action_operation_receive(self):
        print("hello")
        return




class stockmove(models.Model):
    _inherit = 'stock.move'
    order_ref = fields.Many2one('res.partner', string="Receive from")
    order_id = fields.Many2one('field.service', string="Order Id")
    serial_no = fields.Char(string="Serial No")


