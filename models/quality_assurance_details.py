from odoo import api, fields, models, _
from datetime import date

class QualityAssurance(models.Model):
    _name = "quality.assurance"
    _description = "quality assurance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    order_id = fields.Many2one('field.service',string="Order No")
    order_date = fields.Date(related="order_id.order_date",string="Order Date")
    retail = fields.Many2one(related="order_id.retail", string="Retailer/Customer")

    communication_media = fields.Many2one(related='order_id.communication_media', string='Communication Media', tracking=True)

    #service_type = fields.Char(related='order_id.service_type', string='Service Type', tracking=True)
    imei_no = fields.Char(related='order_id.imei_no', readonly=False)
    # imei_number = fields.Char(string='IMEI/Serial No')

    product_id = fields.Many2one(related='order_id.product_id', readonly=False)
    invoice = fields.Char(related='order_id.invoice', readonly=False)
    in_attachment = fields.Binary(related='order_id.in_attachment', readonly=False)
    p_date = fields.Date(related='order_id.p_date', readonly=False)
    customer_id = fields.Many2one(related='order_id.customer_id', readonly=False)
    warranty_status = fields.Many2one(related='order_id.warranty_status', readonly=False)
    warranty_expiry_date_l = fields.Date(related='order_id.warranty_expiry_date_l', readonly=False)
    warranty_expiry_date_p = fields.Date(related='order_id.warranty_expiry_date_p', readonly=False)
    warranty_void_reason_1 = fields.Many2one(related='order_id.warranty_void_reason_1', readonly=False)
    guaranty_expiry_date = fields.Date(related='order_id.guaranty_expiry_date', readonly=False)
    departments = fields.Many2one(related='order_id.departments', readonly=False)
    priority_lavel_duration = fields.Char(related='order_id.priority_lavel_duration', readonly=False)
    phone = fields.Char(related='order_id.phone', readonly=False)
    user_id = fields.Many2one(related='order_id.user_id', readonly=False)
    priority = fields.Selection(related='order_id.priority', readonly=False)

    state = fields.Selection(related='order_id.state', readonly=False)

    priority_levels = fields.Many2one(related='order_id.priority_levels', readonly=False)
    p_delivery_date = fields.Date(related='order_id.p_delivery_date', readonly=False)
    customer_remark = fields.Char(related='order_id.customer_remark', readonly=False)
    remark = fields.Char(related='order_id.remark', readonly=False)

    symptoms_lines_ids = fields.One2many(related='order_id.symptoms_lines_ids', readonly=False)
    symptoms_lines_id = fields.Many2one(related='order_id.symptoms_lines_id', readonly=False)
    special_notes_ids = fields.One2many(related='order_id.special_notes_ids', readonly=False)

    repair_status = fields.Selection(related='order_id.repair_status', readonly=False)

    product_receive_date = fields.Date(related='order_id.product_receive_date', readonly=False)
    delivery_date = fields.Date(related='order_id.delivery_date', readonly=False)
    item_receive_branch = fields.Many2one(related='order_id.item_receive_branch', readonly=False)
    item_receive_status = fields.Char(related='order_id.item_receive_status', readonly=False)
    receive_customer = fields.Boolean(related='order_id.receive_customer', readonly=False)

    so_transfer = fields.Boolean(related='order_id.so_transfer', readonly=False)
    is_sms = fields.Boolean(related='order_id.is_sms', readonly=False)
    special_note = fields.Char(related='order_id.special_note', readonly=False)
    branch_name = fields.Many2one(related='order_id.branch_name', readonly=False)
    qc_line_ids= fields.One2many('quality.assurance.lines','qa_id',string='QC Check List')

class QualityCheckListLines(models.Model):
    _name="quality.assurance.lines"
    name=fields.Many2one('quality.list', string="QC Category")
    description=fields.Many2one("quality.list.lines",name="Description")
    qa_id=fields.Many2one('quality.assurance',string='QA Line')

