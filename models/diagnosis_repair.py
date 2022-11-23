from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
from odoo.exceptions import ValidationError


class DiagnosisRepair(models.Model):
    _name = 'diagnosis.repair'
    _description = 'Diagnosis Repair'
    _rec_name = "repair_no"
    x = fields.Many2one('assign.engineer.lines', string='test')

    userid = fields.Many2one("res.users", default=lambda self: self.env.user.id)

    repair_no = fields.Char(string='Assign No', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    diagnosis_repair_lines_ids = fields.One2many('diagnosis.repair.lines', 'diagnosis_repair',
                                                 string="Diagnosis Repair")
    order_id = fields.Many2one('field.service', string="Service Order", readonly=True)
    warranty = fields.Many2one(related='order_id.warranty_status')
    customer = fields.Many2one(related='order_id.customer_id', string='Customer')
    contact = fields.Char(related="order_id.phone", string='Contact No', readonly=True)
    item = fields.Many2one(related="order_id.product_id", string="Item")
    priority = fields.Selection(related="order_id.priority", string="Priority")
    priority_lavel_duration = fields.Char(related="order_id.priority_lavel_duration", string='Priority Level Duration')

    possible_solution = fields.Char(string="Possible Solution")
    service_charge = fields.Integer(string="Service Charge")
    qa_status = fields.Char(string="QA Status")
    qa_comments = fields.Char(string="QA Comments")

    # engineer = fields.Many2one('assign.engineer', string="Engineer ID", domain=lambda self: self._get_user_domain())
    # engineer_name = fields.Many2one(related="engineer.engineer_name", string="Engineer Name", domain=lambda self: self._get_user_domain())
    engineer = fields.Many2one('res.users', string="Engineer", domain=lambda self: self._get_user_domain(),
                               readonly=True)
    approval = fields.Boolean(compute='_approval', default=False)
    permission = fields.Boolean(compute='_permission', default=False)
    requisition = fields.Boolean(compute='_requisition', string='requisition', default=False)


    def _requisition(self):
        if self.diagnosis_repair_lines_ids:
            for rec in self.diagnosis_repair_lines_ids:
                if rec.part_check == 0:
                    if rec.customer_confirmation == 'confirmed':
                        self.requisition = True
                    else:
                        self.requisition = False
                else:
                    self.requisition = False
        else:
            self.requisition = False

    # def _requisition(self):
    #     for rec in self:
    #         for i in rec.diagnosis_repair_lines_ids:
    #             if i.part_check == '0':
    #                 if i.customer_confirmation == 'confirmed':
    #                     rec.requisition = True
    #                 else:
    #                     rec.requisition = False
    #             else:
    #                 rec.requisition = False

    def requisition_button(self):
        return

    @api.onchange('diagnosis_repair_lines_ids')
    def set_child_warranty(self):
        for rec in self.diagnosis_repair_lines_ids:
            if self.warranty.name == "Warranty":
                rec.customer_confirmation = 'confirmed'
            # elif if self.warranty.name=="Non Warranty":
            #     rec.customer_confirmation=''

    @api.depends('state')
    def _permission(self):
        for rec in self:
            if rec.approval == True:
                for i in rec.diagnosis_repair_lines_ids:
                    if self.env.user.id in i.task_status1.name.ids:
                        if self.env.user.branch_id in rec.order_id.branch_name:
                            rec.permission = True
                        else:
                            rec.permission = False
                    else:
                        rec.permission = False
            else:
                rec.permission = False

    @api.depends('state')
    def _approval(self):
        for rec in self:
            rec.approval = False
            for i in rec.diagnosis_repair_lines_ids:
                if i.task_status1.is_approval == False:
                    rec.approval = False
                else:
                    rec.approval = True

    # @api.depends('state')
    # def _approval(self):
    #     for rec in self:
    #         if rec.diagnosis_repair_lines_ids.task_status1.is_approval == True:
    #             rec.approval = True
    #         else:
    #             rec.approval = False

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
        ('submit_for_approval', 'Submitted For Approval'),
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
            rec.order_id.active = False

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

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

    symptoms = fields.Many2one('symptoms.type', string="Symptoms", domain="[('id','in',symptoms_domain)]")
    # symptoms = fields.Many2one('symptoms.type', string="Symptoms", domain="[('id','in',symptoms_domain)]")

    learner_id = fields.Char(string="Learner_id")
    engineer_observation = fields.Many2one('engineer.observation', string="Engineer Observation")
    attach_diagnosis_doc = fields.Image(string="Attach Diagnosis Doc")
    diagnosis_date = fields.Date(string="Diagnosis Date", default=fields.Datetime.now)
    part = fields.Many2one('product.product')
    part_check = fields.Integer(string="Stock Availability", compute='_compute_available_part')
    defective_sno = fields.Char(string="Defective CT/Serial No")
    service_charge = fields.Integer(string="Total")
    total_amount = fields.Integer(string="Total Amount")
    customer_confirmation = fields.Selection(
        [('confirmed', 'Agree'), ('cancelled', 'Not Agree')],
        string="Customer Confirmation",
        tracking=True)
    # customer_confirmation = fields.Selection(
    #     [('confirmed', 'Agree'), ('cancelled', 'Not Agree')],
    #     string="Customer Confirmation", compute="_confimation",
    #     tracking=True)
    faulty_tag = fields.Char(string="Faculty Tag")
    remarks = fields.Char(string="Remarks")
    task_status = fields.Selection(
        [('repaired', 'Repaired'), ('under-repair', 'Under-Repair'), ('under-diagnosis', 'Under-Diagnosis'),
         ('return-to-customer', 'Return-To-Customer')], string="Task Status",
        tracking=True)
    task_status1 = fields.Many2one('repair.status', string="Task Status",
                                   default=lambda self: self.env['repair.status'].search(
                                       [('repair_status', '=', 'Under Diagnosis')]))
    # task_status1 = fields.Many2one('repair.status', string="Task Status",
    #                                domain=lambda self: self._domain_task_status() )
    # task_status_domain = fields.Many2one('repair.status', string="Task Status",
    #                                      compute="_domain_task_status",
    #                                      readonly=True,
    #                                      store=False,)
    name = fields.Many2many(related='task_status1.name')
    is_approval = fields.Boolean(related='task_status1.is_approval')
    possible_solution = fields.Many2one("possible.solution.lines", string="Possible Solution")

    qa_status = fields.Char(string="QA Status", readonly="1")
    qa_comments = fields.Char(string="QA Comments", readonly="1" )

    current_date = fields.Date(string='Today', default=datetime.today())

    diagnosis_repair = fields.Many2one('diagnosis.repair', string="Diagnosis & Repair")
    rep_seq =fields.Char(string='Token',default=lambda self: _('New'))

    symptoms_domain = fields.Many2many('symptoms.type',
                                       compute="_sym_cal",
                                       readonly=True,
                                       store=False,
                                       )

    # @api.onchange('task_status1')
    # def onchange_task_status(self):




    @api.depends('part')
    def _compute_available_part(self):
        for rec in self:
            location_id = rec.part.warehouse_id.lot_stock_id.id
            rec.part_check = rec.part.with_context({'location': location_id}).free_qty

    @api.onchange('symptoms')
    def onchange_symptoms(self):
        for rec in self:
            return {'domain': {'possible_solution': [('symptoms_type', '=', rec.symptoms.id)]}}

    @api.depends('diagnosis_repair')
    def _sym_cal(self):
        for rec in self:
            res = self.env['symptoms.lines'].sudo().search(
                [('order_id', '=', rec.diagnosis_repair.order_id.id)]).symptoms.ids

            sym = self.env['symptoms.type'].sudo().search([('id', 'in', res)])

            rec.symptoms_domain = sym

    @api.onchange('diagnosis_date')
    def onchange_date(self):
        t_day = date.today()
        print(t_day)
        print(self.diagnosis_date)
        if self.diagnosis_date and self.diagnosis_date > t_day:
            raise ValidationError(_("You Cannot Enter Future Dates"))

    @api.onchange('task_status1')
    def so_repair_status(self):
        for rec in self:
            rec.diagnosis_repair.order_id.repair_status1 = rec.task_status1

    def requisition_button(self):
        return {

            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'view_id': self.env.ref('usl_service_erp.stock_picking_inherit_form_view').id,
            # 'context': {'default_reference': self.order_id.id},
            'target': 'current',
            # 'domain': [('reference', '=', self.order_id.id)],
        }