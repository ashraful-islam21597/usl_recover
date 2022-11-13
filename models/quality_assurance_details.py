# from odoo import api, fields, models, _
# from datetime import date
#
# class QualityAssurance(models.Model):
#     _name = "quality.assurance"
#     _description = "quality assurance"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#
#     order_id = fields.Many2one('field.service',string="Order No")
#     order_date = fields.Date(related="order_id.order_date",string="Order Date")
#     retail = fields.Many2one(related="order_id.retail", string="Retailer/Customer")
#
#     communication_media = fields.Many2one(related='order_id.communication_media', string='Communication Media', tracking=True)
#
#     #service_type = fields.Char(related='order_id.service_type', string='Service Type', tracking=True)
#     imei_no = fields.Char(related='order_id.imei_no', readonly=False)
#     # imei_number = fields.Char(string='IMEI/Serial No')
#
#     product_id = fields.Many2one(related='order_id.product_id', readonly=False)
#     invoice = fields.Char(related='order_id.invoice', readonly=False)
#     in_attachment = fields.Binary(related='order_id.in_attachment', readonly=False)
#     p_date = fields.Date(related='order_id.p_date', readonly=False)
#     customer_id = fields.Many2one(related='order_id.customer_id', readonly=False)
#     warranty_status = fields.Many2one(related='order_id.warranty_status', readonly=False)
#     warranty_expiry_date_l = fields.Date(related='order_id.warranty_expiry_date_l', readonly=False)
#     warranty_expiry_date_p = fields.Date(related='order_id.warranty_expiry_date_p', readonly=False)
#     warranty_void_reason_1 = fields.Many2one(related='order_id.warranty_void_reason_1', readonly=False)
#     guaranty_expiry_date = fields.Date(related='order_id.guaranty_expiry_date', readonly=False)
#     departments = fields.Many2one(related='order_id.departments', readonly=False)
#     priority_lavel_duration = fields.Char(related='order_id.priority_lavel_duration', readonly=False)
#     phone = fields.Char(related='order_id.phone', readonly=False)
#     user_id = fields.Many2one(related='order_id.user_id', readonly=False)
#     priority = fields.Selection(related='order_id.priority', readonly=False)
#
#     state = fields.Selection(related='order_id.state', readonly=False)
#
#     priority_levels = fields.Many2one(related='order_id.priority_levels', readonly=False)
#     p_delivery_date = fields.Date(related='order_id.p_delivery_date', readonly=False)
#     customer_remark = fields.Char(related='order_id.customer_remark', readonly=False)
#     remark = fields.Char(related='order_id.remark', readonly=False)
#
#     symptoms_lines_ids = fields.One2many(related='order_id.symptoms_lines_ids', readonly=False)
#     symptoms_lines_id = fields.Many2one(related='order_id.symptoms_lines_id', readonly=False)
#     special_notes_ids = fields.One2many(related='order_id.special_notes_ids', readonly=False)
#
#     repair_status = fields.Selection(related='order_id.repair_status', readonly=False)
#
#     product_receive_date = fields.Date(related='order_id.product_receive_date', readonly=False)
#     delivery_date = fields.Date(related='order_id.delivery_date', readonly=False)
#     item_receive_branch = fields.Many2one(related='order_id.item_receive_branch', readonly=False)
#     item_receive_status = fields.Char(related='order_id.item_receive_status', readonly=False)
#     receive_customer = fields.Boolean(related='order_id.receive_customer', readonly=False)
#
#     so_transfer = fields.Boolean(related='order_id.so_transfer', readonly=False)
#     is_sms = fields.Boolean(related='order_id.is_sms', readonly=False)
#     special_note = fields.Char(related='order_id.special_note', readonly=False)
#     branch_name = fields.Many2one(related='order_id.branch_name', readonly=False)
#     qc_line_ids= fields.One2many('quality.assurance.lines','qa_id',string='QC Check List')
#
# class QualityCheckListLines(models.Model):
#     _name="quality.assurance.lines"
#     name=fields.Many2one('quality.list', string="QC Category")
#     description=fields.Many2one("quality.list.lines",name="Description")
#     qa_id=fields.Many2one('quality.assurance',string='QA Line')
#

from odoo import api, fields, models, _
from datetime import date

class QualityAssurance(models.Model):
    _name = "quality.assurance"
    _description = "quality assurance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="order_id"

    order_id = fields.Many2one('field.service',string="Order No")
    order_date = fields.Date(related="order_id.order_date",string="Order Date")
    retail = fields.Many2one(related="order_id.retail", string="Retailer/Customer")

    communication_media = fields.Many2one(related='order_id.communication_media', string='Communication Media', tracking=True)

    service_type = fields.Many2one('service.type', string='Service Type', tracking=True)
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
    qa_details_ids=fields.One2many('quality.assurance.details','qa_details',string='QA Details ')
    qa_result = fields.Float(string="QA Result", compute='compute_result')
    qc_category=fields.Many2one('quality.list',string='QC Category')


    @api.onchange("order_id")
    def _onchange_order_id(self):
        self.service_type=self.order_id.service_type.id

    @api.onchange('order_id')
    def onchange_order(self):
        self.qa_details_ids= [(5, 0, 0)]
        val_list = []
        vals = (0, 0, {
            'order_id': self.order_id.id,
            'order_date': self.order_date,
            'product_id': self.product_id.id,
            'warranty_status': self.warranty_status,

        })
            #print(self.service_order_id.customer_id.id)
        val_list.append(vals)

        self.qa_details_ids = val_list

    @api.onchange('qc_line_ids')
    def _onchange_qc_line_ids1(self):
        c = 0
        print(c)
        for i in self.qc_line_ids:
            if i.checked == True:
                c += 1
        x = len(self.qc_line_ids)
        print(x)
        if x != 0:
            self.qa_result = (c / x) * 100
            self.qa_details_ids.qa_status = str((c / x) * 100) + "% passed"
            print(self.qa_result)

    @api.onchange('qc_category')
    def _onchange_qc_line_ids(self):
        #vals = (0, 0, { 'qc_category': self.qc_category})
        qc_check=self.env['quality.list'].search([('category','=',self.qc_category.category)])
        print(qc_check.category_ids)
        for i in qc_check.category_ids:
            print(i.name)
            val_list = []
            vals = (0, 0, {
                'description1': i.name,
                'name':qc_check.category,

            })
            val_list.append(vals)
            self.qc_line_ids = val_list


class QualityAssuranceDetails(models.Model):
    _name = "quality.assurance.details"
    _description = "Quality Assurance Details"
    order_id = fields.Many2one('field.service',string="Order No")
    product_id = fields.Many2one('product.product', readonly=False)
    warranty_status = fields.Many2one('warranty.status', readonly=False)
    symptoms = fields.Many2one('symptoms.lines', readonly=False)
    problem = fields.Many2one('symptoms.lines', readonly=False)
    diagonisis_date = fields.Date(string="Order Date")
    order_date = fields.Date(string="Order Date")
    service_charge=fields.Integer(string="Service Charge")
    total_amount = fields.Integer(string="Total Amount")
    customer_confirmaation=fields.Char(string="Cust")
    task_status=fields.Char(string='Repair Status',readonly=False)
    remarks=fields.Char(string='remarks')
    qa_status= fields.Char(string="QA status")
    qa_comments=fields.Char(string="QA Comments")
    qa_result = fields.Float(string="QA Result", compute='compute_result')

    qa_details = fields.Many2one('quality.assurance', string='QA Details')
    qa_details1 = fields.Many2one('field.service', string='QA Details')







class QualityCheckListLines(models.Model):
    _name="quality.assurance.lines"
    _rec_name="name"

    #qc_id=fields.Many2one('quality.list', string="QC Category")
    name=fields.Char(string="Name")
    description1 = fields.Char(string="Description1")
    sl_no= fields.Integer(string="serial number")
    description=fields.Many2one("quality.list.lines",name="Description",domain=[('category_id','=','name')])
    qa_id=fields.Many2one('quality.assurance',string='QA Line')
    qa_id1 = fields.Many2one('field.service', string='QA Line')
    checked=fields.Boolean(string="Is Checked")

    @api.onchange('name')
    def _onchange_name(self):
        domain= {'description':[('category_id','=',self.name.id)]}
        return {'domain':domain}
