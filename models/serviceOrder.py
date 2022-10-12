# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date


class FieldService(models.Model):
    _name = "field.service"
    _description = "Field Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'order_no'
    _order = 'order_no DESC'

    order_no = fields.Char(string='Order No', required=True, copy=False, readonly=True,
                           default=lambda self: _('New'))
    order_date = fields.Date(string="Order Date", default=fields.Datetime.now)
    branch_name = fields.Many2one('res.branch', string='Branch', tracking=True)
    dealer = fields.Many2one(
        'res.partner',
        string='Dealer/Retail',
        domain=['|', ('category_id', '=', 'Dealer'), ('category_id', '=', 'Retailer')]
    )

    c_media = fields.Selection([
        ('over email', 'Over Email'),
        ('phone', 'Phone'),
        ('social media', 'Social Media'),
    ], string='Communication Media', tracking=True)

    service_type = fields.Many2one('service.type', string='Service Type', tracking=True)
    imei_no = fields.Many2one('field.service.data', string='IMEI/Serial No')
    product_id = fields.Many2one(related='imei_no.product_id', string="Product")
    invoice = fields.Char(related='imei_no.invoice', string='Invoice No', tracking=True)
    in_attachment = fields.Binary(string='Invoice Attachment')
    p_date = fields.Date(related='imei_no.p_date', string='POP Date')
    customer_id = fields.Many2one(related='imei_no.customer_id', string='Customer', tracking=True)
    warranty_status = fields.Selection(related='imei_no.warranty_status', string=' Warranty Status', readonly=False,
                                       tracking=True)
    warranty_expiry_date_l = fields.Date(related='imei_no.warranty_expiry_date_l', string='Warranty Expiry Date(L)')
    warranty_expiry_date_p = fields.Date(related='imei_no.warranty_expiry_date_p', string='Warranty Expiry Date(P)')
    warranty_void_reason_1 = fields.Many2one('warranty.void.reason', string="warranty Void Reason", tracking=True)
    guaranty_expiry_date = fields.Date(string='Guaranty Expiry Date')
    department = fields.Selection([
        ('hp notebook', 'HP Notebook'),
        ('phone', 'Phone'),
        ('apple', 'Apple'),
    ], string='Department', tracking=True)
    priority_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority Level', tracking=True)
    p_delivery_date = fields.Date(string='Possible Delivery Date')
    customer_remark = fields.Char(string='Customer Remark')
    remark = fields.Text(string='Remark')
    symptoms = fields.Text(string="Symptoms")
    reason = fields.Text(string="Reason")

    symptoms_lines_ids = fields.One2many('symptoms.lines', 'order_id', string="Symptoms")

    repair_status = fields.Selection([
        ('repaired', 'Repaired'),
        ('not_repaired', 'Not-repaired'),
        ('repairing', 'Repairing'),
    ], string='Repair Status', tracking=True)
    product_receive_date = fields.Date(string='Product Receive Date')
    delivery_date = fields.Date(string='Delivery Date')
    item_receive_branch = fields.Char(string='Item Receive Branch')
    item_receive_status = fields.Char(string='Item Receive Status')
    receive_customer = fields.Boolean(string='Is Receive From Customer')
    so_transfer = fields.Boolean(string='Is So Transfer')
    is_sms = fields.Boolean(string='Is SMS')

    def set_line_number(self):
        sl_no = 0
        for line in self.symptoms_lines_ids:
            sl_no += 1
            line.sl_no = sl_no
        return

    # @api.model
    # def create(self, vals):
    #     if vals.get('order_no', _('New')) == _('New'):
    #         vals['order_no'] = self.env['ir.sequence'].next_by_code('field.service') or _('New')
    #     res = super(FieldService, self).create(vals)
    #     # res.set_line_number()
    #     return res
    #
    # def write(self, vals):
    #     res = super().write(vals)
    #     # self.set_line_number()
    #     return res
    #
    def actions_test(self):
        return

    @api.model
    def create(self, vals):
        # vals['order_no'] = self.env['ir.sequence'].next_by_code('service.order')
        res=super(FieldService, self).create(vals)
        res.set_line_number()
        return res


    def write(self, values):

        res = super(FieldService, self).write(values)
        self.set_line_number()
        return res

    def action_symptoms(self):
        return

    # def write(self, values):
    #     res = super(FieldService, self).write(values)
    #     sl_no = 0
    #     for line in self.symptoms_lines_ids:
    #         sl_no += 1
    #         line.sl_no = sl_no
    #     return res


class SymptomsLines(models.Model):
    _name = "symptoms.lines"
    _description = "Symptoms Lines"

    symptoms1 = fields.Text(string="Symptoms")
    reason1 = fields.Text(string="Reason")
    sl_no = fields.Integer(string='SLN.')

    order_id = fields.Many2one('field.service', string="Order")
