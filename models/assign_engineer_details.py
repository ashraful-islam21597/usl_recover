from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError


class AssignEngineerDetails(models.Model):
    _name = 'assign.engineer.details'
    _description = 'Assign Engineer Details'
    _rec_name = "assign_no"

    assign_no = fields.Char(string='Assign No', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    assign_engineer_lines_ids = fields.One2many('assign.engineer.lines', 'engineer_id', string="Assign Engineer")
    order_id = fields.Many2one('field.service', string="Service Order", readonly=True)
    contact = fields.Char(related="order_id.phone", string='Contact No', readonly=True)
    # assign_engineer_lines_id = fields.Many2one('assign.engineer.lines', string="Engineer")
    is_qa = fields.Char(string="Is QA?")
    qa_result = fields.Char(string="QA Result")
    qa = fields.Char(string="QA")

    @api.model
    def create(self, vals):
        if vals.get('assign_no', _('New')) == _('New'):
            vals['assign_no'] = self.env['ir.sequence'].next_by_code('assign.engineer.details') or _('New')
        res = super(AssignEngineerDetails, self).create(vals)
        return res

    @api.onchange('assign_engineer_lines_ids')
    def set_engineer_domain(self):
        if self.order_id:
            get_branch = self.order_id.branch_name
            get_enginners = self.env.ref("usl_service_erp.group_service_engineer").users
            get_related_engineer = self.env['res.users'].sudo().search(
                [('branch_id', '=', get_branch.id), ('id', 'in', get_enginners.ids)])
            return {'domain': {'assign_engineer_lines_ids.engineer_name': [('id', 'in', get_related_engineer.ids)]}}


        else:
            return {'domain': {'assign_engineer_lines_ids.engineer_name': [('id', 'in', False)]}}


class AssignEngineerLines(models.Model):
    _name = "assign.engineer.lines"
    _description = "Assign Engineer Lines"
    _rec_name = "engineer_name"

    # engineer_name = fields.Many2one('assign.engineer', required=True, string="Engineer ID" )
    # domain = lambda self: [("groups_id", "=", self.env.ref("usl_service_erp.group_service_engineer").id)]
    # engineer_name = fields.Many2one('res.users', string="Engineer", domain=lambda self: self._get_user_domain())
    engineer_name = fields.Many2one('res.users', string="Engineer", domain="[('id','in',engineer_name_domain)]")
    # engineer_name1 = fields.Many2one(related='engineer_name.engineer_name', string="Engineer Name")
    # engineer_task = fields.Integer(related='engineer_name.task_count', string="Task")
    assign_date = fields.Date(string='Assign Date', default=fields.Datetime.now)
    assign_status1 = fields.Selection([('assigned', 'Assigned'), ('pending', 'Pending')], string="Assign Status",
                                      default='assigned')
    assign_for = fields.Selection(
        [('diagnosis and repair', 'Diagnosis and Repair'), ('quality assurance', 'Quality Assurance'),
         ('over phone communication', 'Over Phone Communication')], string="Assigned For")
    is_qa = fields.Char(string="Is QA?")
    qa_result = fields.Char(string="QA Result")
    qa = fields.Char(string="QA")
    remarks = fields.Char(string="Remarks")
    delivery_date = fields.Date(string="Delivery Date")

    engineer_id = fields.Many2one('assign.engineer.details', string="Assign")

    task_count = fields.Integer(string='Task Count', compute='_compute_task_count')
    engineer_name_domain = fields.Many2many('res.users',
                                            compute="_compute_engineer_domain",
                                            readonly=True,
                                            store=False,
                                            )

    # product_id_domain = fields.Many2many(
    #     default="_compute_product_id_domain",
    #     readonly=True,
    #     store=False,
    # )

    # @api.onchange('engineer_name')
    # def onchange_engineer_name(self):
    #     print(self.engineer_name)
    #
    #     eng_list=[]
    #     for i in self:
    #         if i.engineer_id.order_id.branch1.id == i.engineer_name.branch_id.id:
    #             eng_list.append(i.engineer_name)
    #             print(eng_list)
    #         return eng_list

    @api.depends('engineer_id')
    def _compute_engineer_domain(self):
        if self.env.user.has_group('usl_service_erp.group_service_engineer'):
            if self.engineer_id.order_id:
                get_branch = self.engineer_id.order_id.branch_name
                get_enginners = self.env.ref("usl_service_erp.group_service_engineer").users
                get_related_engineer = self.env['res.users'].sudo().search(
                    [('branch_id', '=', get_branch.id), ('id', '=', self.env.user.id)])
                self.engineer_name_domain = get_related_engineer
            else:
                self.engineer_name_domain = None
        if self.env.user.has_group('usl_service_erp.group_service_manager'):
            if self.engineer_id.order_id:
                get_branch = self.engineer_id.order_id.branch_name
                get_enginners = self.env.ref("usl_service_erp.group_service_engineer").users
                get_related_engineer = self.env['res.users'].sudo().search(
                    [('branch_id', '=', get_branch.id), ('id', 'in', get_enginners.ids)])
                self.engineer_name_domain = get_related_engineer
            else:
                self.engineer_name_domain = None

        # return domain

    def _compute_task_count(self):
        for rec in self:
            task_count = self.env['diagnosis.repair'].search_count([('engineer', '=', rec.engineer_name.id)])
            rec.task_count = task_count

    # def _get_user_domain(self):
    #     if self.order_id:
    #         get_branch=self.order_id.branch1
    #         get_enginners= self.env.ref("usl_service_erp.group_service_engineer").users
    #         get_related_engineer=self.env['res.users'].sudo().search([('branch_id','=',get_branch.id),('id','in',get_enginners.ids)])
    #         domain = [('id', 'in', get_related_engineer.ids)]
    #     else:
    #         domain = [('id', 'in', False)]
    #     return domain
    # all_users = self.env['res.users'].sudo().search([])
    # get_users = self.env.ref("usl_service_erp.group_service_engineer").users
    # if not isinstance(get_users, bool) and get_users:
    #     domain = [('id', 'in', get_users.ids)]
    # else:
    #     domain = [('id', 'in', all_users.ids)]
    # # domain = ["groups_id", "=", self.env.ref("usl_service_erp.group_service_engineer").id]
    # return domain

    @api.onchange('assign_for')
    def onchange_assign_for(self):
        if self.assign_for == 'diagnosis and repair':
            self.env['diagnosis.repair'].create(
                {'order_id': self.engineer_id.order_id.id, 'engineer': self.engineer_name.id,
                 'contact': self.engineer_id.contact})
            # self.env['diagnosis.repair.lines'].create({'symptoms': self.engineer_id.order_id.symptoms_lines_id.symptoms})

    def name_get(self):
        list = []
        for rec in self:
            name = str(rec.engineer_name.name) + ' ' + str(rec.task_count)
            list.append((rec.id, name))
        return list
