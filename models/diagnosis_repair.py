from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
from odoo.exceptions import ValidationError


class DiagnosisRepair(models.Model):
    _name = 'diagnosis.repair'
    _description = 'Diagnosis Repair'
    _rec_name = "repair_no"
    x = fields.Many2one('assign.engineer.lines', string='test')

    repair_no = fields.Char(string='Assign No', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    diagnosis_repair_lines_ids = fields.One2many('diagnosis.repair.lines', 'diagnosis_repair',
                                                 string="Diagnosis Repair")
    order_id = fields.Many2one('field.service', string="Service Order", readonly=True)
    warranty = fields.Many2one(related='order_id.warranty_status')
    customer = fields.Many2one(related='order_id.customer_id', string='Customer')
    contact = fields.Char(related="order_id.phone", string='Contact No', readonly=True)
    item = fields.Many2one(related="order_id.product_id", string="Item")
    possible_solution = fields.Char(string="Possible Solution")
    service_charge = fields.Integer(string="Service Charge")
    qa_status = fields.Char(string="QA Status")
    qa_comments = fields.Char(string="QA Comments")

    # engineer = fields.Many2one('assign.engineer', string="Engineer ID", domain=lambda self: self._get_user_domain())
    # engineer_name = fields.Many2one(related="engineer.engineer_name", string="Engineer Name", domain=lambda self: self._get_user_domain())
    engineer = fields.Many2one('res.users', string="Engineer", domain=lambda self: self._get_user_domain(),
                               readonly=True)

    def _get_user_domain(self):
        all_users = self.env['res.users'].sudo().search([])
        get_users = self.env.ref("usl_service_erp.group_service_engineer").users
        if not isinstance(get_users, bool) and get_users:
            domain = [('id', 'in', get_users.ids)]
        else:
            domain = [('id', 'in', all_users.ids)]
        # domain = ["groups_id", "=", self.env.ref("usl_service_erp.group_service_engineer").id]
        return domain

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('cancel', 'Canceled')], default='draft', string="Status", required=True)

    def action_test(self):
        return

    def action_service_for_approval(self):
        for rec in self:
            rec.state = 'submit_for_approval'

    def action_approval(self):
        for rec in self:
            rec.state = 'approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    # amount_total = fields.Monetary(string='Total', compute='_compute_amount_total')
    #
    # @api.depends('diagnosis_repair_lines_ids')
    # def _compute_amount_total(self):
    #     for rec in self:
    #         amount_total = 0
    #         for line in rec.client_ids:
    #             amount_total += line.service_charge
    #         rec.amount_total = amount_total

    @api.model
    def create(self, vals):
        if vals.get('repair_no', _('New')) == _('New'):
            vals['repair_no'] = self.env['ir.sequence'].next_by_code('diagnosis.repair') or _('New')
        res = super(DiagnosisRepair, self).create(vals)
        return res

    def action_in_consultation(self):
        return


class DiagnosisRepairLines(models.Model):
    _name = "diagnosis.repair.lines"
    _description = "Assign Engineer Lines"

    item = fields.Char(string="Item")
    # warranty_status= fields.Selection([('warranty', 'Warranty'), ('non-warranty', 'Non-warranty')], string="Warranty Status",
    #                                         tracking=True)

    # reference = fields.Many2one('field.service', string='Service Order')
    symtoms_lines = fields.Many2one('symptoms.lines')
    symptoms = fields.Many2one('symptoms.type', string="Symptoms", domain=lambda self: self._get_symtoms())
    learner_id = fields.Char(string="Learner_id")
    engineer_observation = fields.Many2one('engineer.observation', string="Engineer Observation")
    attach_diagnosis_doc = fields.Image(string="Attach Diagnosis Doc")
    diagnosis_date = fields.Date(string="Diagnosis Date")
    part = fields.Many2one('product.product')
    defective_sno = fields.Char(string="Defective CT/Serial No")
    service_charge = fields.Integer(string="Total")
    total_amount = fields.Integer(string="Total Amount")
    customer_confirmation = fields.Selection(
        [('confirmed', 'Confirmed'), ('pending', 'Pending'), ('cancelled', 'Cancelled')],
        string="Customer Confirmation",
        tracking=True)
    faulty_tag = fields.Char(string="Faculty Tag")
    remarks = fields.Char(string="Remarks")
    task_status = fields.Selection(
        [('repaired', 'Repaired'), ('under-repair', 'Under-Repair'), ('under-diagnosis', 'Under-Diagnosis'),
         ('return-to-customer', 'Return-To-Customer')], string="Task Status",
        tracking=True)
    qa_status = fields.Char(string="QA Status")
    qa_comments = fields.Char(string="QA Comments")

    current_date = fields.Date(string='Today', default=datetime.today())

    diagnosis_repair = fields.Many2one('diagnosis.repair', string="Diagnosis & Repair")

    # warranty_status = fields.Many2one(related='diagnosis.repair.warranty')

    # @api.onchange('customer_confirmation')
    # def onchange_customer_confirmation(self):
    #     print("success")
    #     if(self.customer_confirmation == 'cancelled'):
    #         print(self.customer_confirmation)
    #         print(self.diagnosis_repair.state)
    #         self.diagnosis_repair.state='submit_for_approval'
    #         print(self.diagnosis_repair.state)

    # @api.onchange('diagnosis_date')
    # def onchange_diagnosis_date(self):
    #     today = date.today()
    #     print(today)
    #     print(diagnosis_date)
    #     print(today)
    #     if self.diagnosis_date > today:
    #         raise ValidationError(_("You Cannot Enter Future Dates"))

    def _get_symtoms(self):
        return

    @api.onchange('diagnosis_date')
    def onchange_date(self):
        t_day = date.today()
        print(t_day)
        print(self.diagnosis_date)
        if self.diagnosis_date and self.diagnosis_date > t_day:
            raise ValidationError(_("You Cannot Enter Future Dates"))

    @api.onchange('warranty_status')
    def onchange_diagnosis_date(self):
        if self.warranty_status == 'warranty':
            self.customer_confirmation = 'confirmed'
