from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError



class ServiceOrderTransfer(models.Model):
    _name = 'order.transfer'
    _description = 'Service Order Transfer'
    _rec_name = 'delivery_no'

    #transfer_serial = fields.Char(string="Transfer Serial no")

    delivery_no = fields.Char(string='Delivery No',readonly=True)


    transfer_date = fields.Date(string="Transfer Date", default=fields.Date.context_today,tracking=True,readonly=True)
    Delivery_date = fields.Date(string="Delivery Date")
    item_receive_date = fields.Date(string="item Receive Date")
    repair_status = fields.Char(string="Next Contact Person")
    remarks = fields.Char(string="Remarks")
    transfer_no = fields.Many2one('field.service', string="Service Order no")
    #branch = fields.Many2one('res.branch',string="Branch")
    user_id = fields.Many2one('res.users', string='users', tracking=True, default=lambda self: self.env.user)
    branch = fields.Many2one(related='user_id.branch_id',readonly=True, tracking=True)
    order_transfer_ids = fields.One2many('order.transfer.lines', 'transfer_id',
                                         string="Order Transfer Details")
    is_submitted = fields.Boolean(string='Is Submitted')
    to_branch = fields.Many2one('res.branch', string='To Branch')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submitted For Approval'),
        ('approved', 'Approved'),], default="draft", string="Status", required=True, tracking=True)


    @api.model
    def create(self, vals):
        vals['delivery_no'] = self.env['ir.sequence'].next_by_code('order.transfer')
        return super().create(vals)

    def action_submit_for_approval(self):

        for rec in self:
            if rec.state == 'draft':
                #user_branch = self.env['stock.quant'].search([('product_id', '=', self.transfer_no.product_id)])
                #print(user_branch)
                self.stock_quant_query(self.order_transfer_ids)
                rec.state = "submit_for_approval"

    def stock_quant_query(self, data):
        for x in data:
            user = self.env['res.users'].browse(self._context.get('uid'))
            print(user.warehouse_id.id)
            print(self.branch,user.company_id)
            warehouse_data = self.env['stock.warehouse'].search([
                ('branch_id', '=', x.order_id.branch_name.id),
                ('company_id', '=', user.company_id.id),

            ])
            print(warehouse_data.code,x.order_id.branch_name,warehouse_data,user.branch_id,user.company_id)
            stock_location_data = self.env['stock.location'].search([
                ('location_id', '=', warehouse_data.code),
                ('name', '=', 'Stock'),
                ('branch_id', '=', user.branch_id.id),
                ('company_id', '=', user.company_id.id),
                ('warehouse_id', '=', user.warehouse_id.id),
            ])

            print(stock_location_data)
            print(x.order_id.product_id.id, x.order_id)
            t = x.order_id.product_id
            print(t.id)
            stock_quant_data = self.env['stock.quant'].search([
                ('location_id', '=', stock_location_data.id),
                ('company_id', '=', user.company_id.id),
                ('product_id', '=', t.id),

            ])
            p = self.env['stock.picking.type'].search([
                ('company_id', '=', user.company_id.id),
                ('warehouse_id', '=', warehouse_data.id),
                ('code', '=', 'incoming'),
                ('default_location_src_id', '=', stock_location_data.id)])
            print(p)
            y = self.env['stock.picking'].search(
                [('branch_id', '=', user.branch_id.id), ('company_id', '=', user.company_id.id),
                 ('location_dest_id', '=', stock_location_data.id), ('location_id', '=', stock_location_data.id),
                 ('location_id', '=', stock_location_data.id), ('picking_type_id', '=', p.id)])
            print(y)
            print(stock_quant_data)
            stock_quant_data.quantity = stock_quant_data.quantity - 1
            stock_quant_data.reserved_quantity = stock_quant_data.reserved_quantity + 1
            print(stock_quant_data.quantity, stock_quant_data.reserved_quantity, stock_quant_data.product_id.name)
            print("-------------------------------------------------")




class service_order_transfer_lines(models.Model):
    _name = 'order.transfer.lines'
    _description = 'Service Order Transfer Lines'


    transfer_date = fields.Date(string="Transfer Date")
    model = fields.Char(string="Model")
    quantity = fields.Integer(string="Quantitay",default=1)
    transfer_id = fields.Many2one('order.transfer', string="Service Order Transfer")
    #current_branch=fields.Char(related="transfer_id.branch",string="branch")

    order_id = fields.Many2one('field.service', string="Service Order no", domain=[ ('repair_status', '=', 'pending')])
    item = fields.Many2one(related="order_id.product_id",string='Item')
    #serial_no = fields.Many2one(related="order_id.serial_no", string='Serial No')
    serial_no = fields.Char(string="Serial No")

    @api.onchange('order_id','transfer_id')
    def _onchange_order_transfer(self):
        print("x")
        self.serial_no = self.order_id.imei_no.serial_no



