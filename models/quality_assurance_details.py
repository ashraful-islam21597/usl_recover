
from odoo import api, fields, models, _
from datetime import date
from .diagnosis_repair import DiagnosisRepair, DiagnosisRepairLines


class QualityAssurance(models.Model):
    _inherit = "field.service"

    qc_line_ids = fields.One2many('quality.assurance.lines', 'qa_id', string='QC Check List')
    qa_details_ids = fields.One2many('quality.assurance.details', 'qa_details', string='QA Details')
    qa_result = fields.Float(string="QA Result")
    qc_category = fields.Many2one('quality.list', string='QC Category')
    repair_and_diagnosis_id=fields.Many2one('diagnosis.repair',string="Repair and diagonis")


    def _quality_assurance_view_render(self):
        tree_id = self.env.ref("usl_service_erp.view_service_order_quality_tree")
        form_id = self.env.ref("usl_service_erp.view_service_order_quality_form")
        print(self.env['res.users'].browse(self._context.get('uid')).branch_id.name)
        user = self.env['res.users'].browse(self._context.get('uid'))
        if user.has_group('usl_service_erp.group_service_manager'):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quality Assurance',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'field.service',
                'domain': [
                    #('id', 'in', so_list_for_assigned_qa),
                    ('current_branch', '=', self.env['res.users'].browse(self._context.get('uid')).branch_id.id)],
                'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
                'target': 'current',

            }

        else:

            assign_engineer_lines = self.env['assign.engineer.lines'].search([

                ('engineer_name', '=', self.env['res.users'].browse(self._context.get('uid')).id),
                ('assign_for', '=', 'quality assurance'),
                                                        ])
            so_list_for_assigned_qa=[]
            for i in assign_engineer_lines:
                so_list_for_assigned_qa.append(i.engineer_id.order_id.id)


            print(user.has_group('usl_service_erp.group_service_manager'))

            d = self.env['assign.engineer.lines'].search(
                [('engineer_name', '=', self.env['res.users'].browse(self._context.get('uid')).id)])
            # d=self.env['assign.engineer.details'].search([('engineer_name', '=', self.env['res.users'].browse(self._context.get('uid')).id)])


            return {
                'type': 'ir.actions.act_window',
                'name': 'Quality Assurance',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'field.service',
                'domain': [
                           ('id','in',so_list_for_assigned_qa),
                           ('current_branch', '=', self.env['res.users'].browse(self._context.get('uid')).branch_id.id)],
                'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
                'target': 'current',

            }

    @api.onchange('repair_and_diagnosis_id')
    def _onchange_qa_line_ids(self):
        repair_diagonis_id=self.env['diagnosis.repair'].search([('order_id','=',self.id)])
        print("Hello")
        self.qa_details_ids = [(5, 0, 0)]
        val_list = []
        # vals = (0, 0, {
        #     'order_id': self.order_no,
        #     'order_date': self.order_date,
        #     'product_id': self.product_id.id,
        #     'warranty_status': self.warranty_status,
        #
        # })
        # val_list.append(vals)
        # self.qa_details_ids = val_list

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
    product_id = fields.Many2one('product.product', readonly=False,string="Part")
    warranty_status = fields.Many2one('warranty.status', readonly=False)
    symptoms = fields.Char(string="Symptoms")
    problem = fields.Many2one('symptoms.lines', readonly=False)
    diagnosis_date = fields.Date(string="Diagnosis Date")
    order_date = fields.Date(string="Order Date")
    service_charge = fields.Integer(string="Service Charge")
    total_amount = fields.Integer(string="Total Amount")
    customer_confirmaation = fields.Char(string="Cost")
    qa_status = fields.Many2one('repair.status', string="QA Status",
                                   domain=lambda self: self._get_repair_status())

    remarks = fields.Char(string='remarks')
    task_status = fields.Char(string="QA status")
    qa_comments = fields.Char(string="QA Comments")
    qa_result = fields.Float(string="QA Result (%)")
    qa_details = fields.Many2one('field.service', string='QA Details')
    learner_id = fields.Char(string="Learner_id")
    rep_seq = fields.Char(string='Token')
    diagnosis_repair_id= fields.Many2one('diagnosis.repair', string="Diagnosis && Repair")



    def _get_repair_status(self):
        get_repair_status = self.env['repair.status'].sudo().search(
            ['|','|',
             ('repair_status', '=', 'Ready For QC'),
             ('repair_status', '=', 'Ready To Deliver'),
             ('repair_status', '=', 'QA Return')])
        domain = [('id', 'in', get_repair_status.ids)]
        return domain

    def write(self, values):
        res=super(QualityAssuranceDetails, self).write(values)

        x=self.env['field.service'].search([('id','=',self.qa_details.id)])
        #x = self.env['repair.status'].search([('id','=',values['qa_status'])]).id
        x.repair_status1 = self.env['repair.status'].search([('id','=',values['qa_status'])]).id
        print(self.env['repair.status'].search([('id','=',values['qa_status'])]).repair_status)
        return res

    def write(self, values):
        res = super(QualityAssuranceDetails, self).write(values)
        # z=self.env['field.service'].search([('id','=',self.qa_details.id)])
        # #x = self.env['repair.status'].search([('id','=',values['qa_status'])]).id
        #
        # z.repair_status1 = self.env['repair.status'].search([('id','=',values['qa_status'])]).id
        print(self.env['repair.status'].search([('id','=',values['qa_status'])]).repair_status)
        # print(self.qa_details.id,values['qa_comments'])
        # self.env['diagnosis.repair'].search([('order_id', '=', self.qa_details.id)])
        for rec in self:
            x = self.env['diagnosis.repair'].search([('order_id', '=', rec.qa_details.id)])
            for i in x.diagnosis_repair_lines_ids:
                if i.rep_seq ==rec.rep_seq:
                    i.qa_comments = rec.qa_comments



                #if i.qa_comments == False:


            # print(x.diagnosis_repair_lines_ids[-1],x.diagnosis_repair_lines_ids[-1].task_status1)
            # x = self.env['repair.status'].search([('id', '=', values['qa_status'])]).id
            # x.repair_status1 = self.env['repair.status'].search([('id', '=', values['qa_status'])]).id
            # print(self.env['repair.status'].search([('id', '=', values['qa_status'])]).repair_status)
            return res
    @api.onchange('qa_status')
    def so_qa_status(self):
        for rec in self:
            print(rec.qa_details.id)
            rec.qa_details.repair_status1 = rec.qa_status

class diagnosisRepair(models.Model):
    _inherit='diagnosis.repair.lines'

    @api.model
    def create(self, vals):
        res = super(DiagnosisRepairLines, self).create(vals)
        if vals.get('serial', _('New')) == _('New'):
            print("repair")
            val = self.env['ir.sequence'].next_by_code('diagnosis.repair') or _('New')
            res.rep_seq = val
        s2 = self.env['diagnosis.repair'].search([('id', '=', res.diagnosis_repair.id)])
        print(s2.diagnosis_repair_lines_ids)
        # res.diagnosis_repair.order_id.qa_details_ids = [(5, 0, 0)]
        # val_list = []
        # for j in s2:
        #s2.order_id.qa_details_ids = [(5, 0, 0)]
        for i in s2.diagnosis_repair_lines_ids:
            print(s2.order_id.qa_details_ids)
            print(i.rep_seq)
            val_list = []
        for i in s2.diagnosis_repair_lines_ids:
            print(i.rep_seq)

            val_list = []
            if i.task_status1.repair_status == 'Ready For QC':
                vals = (0, 0, {
                    'order_id': i.diagnosis_repair.order_id.order_no,
                    'order_date': i.diagnosis_repair.order_id.order_date,
                    'product_id': i.part.id,
                    'warranty_status': i.diagnosis_repair.order_id.warranty_status.id,
                    'service_charge' : i.diagnosis_repair.service_charge,
                    'diagnosis_date': i.diagnosis_date,
                    'qa_status': i.task_status1.id,
                    'task_status': i.task_status1.id,
                    'total_amount':i.total_amount,
                    'symptoms': i.symptoms.symptom,
                    'learner_id': i.learner_id,
                    'diagnosis_repair_id':i.diagnosis_repair.id,
                    'rep_seq': i.rep_seq

                })
                val_list.append(vals)
        s2.order_id.qa_details_ids = val_list
        return res

    def write(self, values):
        res = super(DiagnosisRepairLines, self).write(values)
        s=self.env['diagnosis.repair.lines'].search([('rep_seq', '=', self.rep_seq)])
        s1=self.env['quality.assurance.details'].search([('rep_seq', '=', self.rep_seq)])
        print(s1)
        print(values,s.symptoms.symptom)
        return res


class QualityCheckListLines(models.Model):
    _name = "quality.assurance.lines"
    _rec_name = "name"

    # qc_id=fields.Many2one('quality.list', string="QC Category")
    name = fields.Char(string="Name")
    description1 = fields.Char(string="Description1")
    sl_no = fields.Integer(string="serial number")
    description = fields.Many2one("quality.list.lines", name="Description", domain=[('category_id', 'ilike', 'name')])
    # qa_id=fields.Many2one('quality.assurance',string='QA Line')
    qa_id = fields.Many2one('field.service', string='QA Line')
    checked = fields.Boolean(string="Is Checked")
