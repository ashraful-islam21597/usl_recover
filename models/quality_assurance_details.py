
from odoo import api, fields, models, _
from datetime import date


class QualityAssurance(models.Model):
    _inherit = "field.service"

    qc_line_ids = fields.One2many('quality.assurance.lines', 'qa_id', string='QC Check List')
    qa_details_ids = fields.One2many('quality.assurance.details', 'qa_details', string='QA Details')
    qa_result = fields.Float(string="QA Result")
    qc_category = fields.Many2one('quality.list', string='QC Category')
    def _quality_assurance_view_render(self):
        assign_engineer_lines = self.env['assign.engineer.lines'].search([
            ('engineer_name', '=', self.env['res.users'].browse(self._context.get('uid')).id),
            ('assign_for', '=', 'quality assurance')])
        so_list_for_assigned_qa=[]
        for rec in assign_engineer_lines:
            so_list_for_assigned_qa.append(rec.engineer_id.order_id.id)
        tree_id = self.env.ref("usl_service_erp.view_service_order_quality_tree")
        form_id = self.env.ref("usl_service_erp.view_service_order_quality_form")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quality Assurance',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'field.service',
            'domain': [('repair_status', '=', 'ready for qc'),
                       ('id','in',so_list_for_assigned_qa),
                       ('state', '=', 'approval'),
                       ('receive_customer', '=', True),
                       ('current_branch', '=', self.env['res.users'].browse(self._context.get('uid')).branch_id.id)],
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
            'target': 'current',

        }

    @api.onchange('id')
    def _onchange_qa_line_ids(self):
        s=self.env['diagonisis.repair'].search('order_id','=',self.id)
        print(s)
        self.qa_details_ids = [(5, 0, 0)]
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
        qc_check = self.env['quality.list'].search([('category', 'ilike', self.qc_category.category)])
        self.qc_line_ids = [(5, 0, 0)]
        for i in qc_check.category_ids:
            val_list = []
            vals = (0, 0, {
                'description1': i.name,
                'name': qc_check.category,
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
    service_charge = fields.Integer(string="Service Charge")
    total_amount = fields.Integer(string="Total Amount")
    customer_confirmaation = fields.Char(string="Cust")
    task_status = fields.Selection([
        ('pending', 'Pending'),
        ('not_repaired', 'Not-repaired'),
        ('repairing', 'Repairing'),
        ('repaired', 'Repaired'),
        ('ready for qc', 'Ready For QC')
    ], string='Repair Status', tracking=True, default='pending')
    remarks = fields.Char(string='remarks')
    qa_status = fields.Char(string="QA status")
    qa_comments = fields.Char(string="QA Comments")
    qa_result = fields.Float(string="QA Result (%)")
    qa_details = fields.Many2one('field.service', string='QA Details')




class QualityCheckListLines(models.Model):
    _name = "quality.assurance.lines"
    _rec_name = "name"

    name = fields.Char(string="Name")
    description1 = fields.Char(string="Description1")
    sl_no = fields.Integer(string="serial number")
    description = fields.Many2one("quality.list.lines", name="Description", domain=[('category_id', 'ilike', 'name')])
    qa_id = fields.Many2one('field.service', string='QA Line')
    checked = fields.Boolean(string="Is Checked")
