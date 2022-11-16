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
    _inherit = "field.service"

    qc_line_ids= fields.One2many('quality.assurance.lines','qa_id',string='QC Check List')
    qa_details_ids=fields.One2many('quality.assurance.details','qa_details',string='QA Details')
    qa_result = fields.Float(string="QA Result")
    qc_category=fields.Many2one('quality.list',string='QC Category')

    def _quality_assurance_view_render(self):
        tree_id = self.env.ref("usl_service_erp.view_service_order_quality_tree")
        form_id = self.env.ref("usl_service_erp.view_service_order_quality_form")
        print(self.env['res.users'].browse(self._context.get('uid')).branch_id.name)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quality Assurance',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'field.service',
            'domain': [('repair_status', '=', 'ready for qc'),('current_branch', '=', self.env['res.users'].browse(self._context.get('uid')).branch_id.id)],
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
            'target': 'current',

        }
    @api.onchange('id')
    def _onchange_qa_line_ids(self):
        print("Hello")
        self.qa_details_ids= [(5, 0, 0)]
        val_list = []
        vals = (0, 0, {
            'order_id': self.order_no,
            'order_date': self.order_date,
            'product_id': self.product_id.id,
            'warranty_status': self.warranty_status,

        })
        val_list.append(vals)
        self.qa_details_ids = val_list

    @api.onchange('qc_line_ids')
    def _onchange_qc_line_ids1(self):
        c = 0
        print(c)
        for i in self.qc_line_ids:
            if i.checked == True:
                c += 1
        len_qc_line_ids = len(self.qc_line_ids)

        if len_qc_line_ids != 0:
            self.qa_result = (c / len_qc_line_ids) * 100
            self.qa_details_ids.qa_result = (c / len_qc_line_ids) * 100


    @api.onchange('qc_category')
    def _onchange_qc_line_ids(self):
        qc_check=self.env['quality.list'].search([('category','ilike',self.qc_category.category)])
        self.qc_line_ids = [(5, 0, 0)]
        for i in qc_check.category_ids:

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
    order_id = fields.Char(string="Order No")
    product_id = fields.Many2one('product.product', readonly=False)
    warranty_status = fields.Many2one('warranty.status', readonly=False)
    symptoms = fields.Many2one('symptoms.lines', readonly=False)
    problem = fields.Many2one('symptoms.lines', readonly=False)
    diagonisis_date = fields.Date(string="Order Date")
    order_date = fields.Date(string="Order Date")
    service_charge=fields.Integer(string="Service Charge")
    total_amount = fields.Integer(string="Total Amount")
    customer_confirmaation=fields.Char(string="Cust")
    task_status=fields.Selection([
        ('pending', 'Pending'),
        ('not_repaired', 'Not-repaired'),
        ('repairing', 'Repairing'),
        ('repaired', 'Repaired'),
        ('ready for qc','Ready For QC')
    ], string='Repair Status', tracking=True, default='pending')
    remarks=fields.Char(string='remarks')
    qa_status= fields.Char(string="QA status")
    qa_comments=fields.Char(string="QA Comments")
    qa_result = fields.Float(string="QA Result (%)")
    qa_details = fields.Many2one('field.service', string='QA Details')







class QualityCheckListLines(models.Model):
    _name="quality.assurance.lines"
    _rec_name="name"

    #qc_id=fields.Many2one('quality.list', string="QC Category")
    name=fields.Char(string="Name")
    description1 = fields.Char(string="Description1")
    sl_no= fields.Integer(string="serial number")
    description=fields.Many2one("quality.list.lines",name="Description",domain=[('category_id','ilike','name')])
    #qa_id=fields.Many2one('quality.assurance',string='QA Line')
    qa_id= fields.Many2one('field.service', string='QA Line')
    checked=fields.Boolean(string="Is Checked")
