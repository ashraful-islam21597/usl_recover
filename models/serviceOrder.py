# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date
import datetime
from odoo.exceptions import ValidationError


class FieldService(models.Model):
    _name = "field.service"
    _description = "Field Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'order_no'
    _order = 'order_no DESC'
    order_no = fields.Char(string='Order No', required=True, copy=False, readonly=True,
                           default=lambda self: _('New'))
    order_date = fields.Date(string="Order Date", default=fields.Datetime.now, readonly=True, )
    retail = fields.Many2one(
        'res.partner',
        string='Dealer/Retail',
        domain=['|', ('category_id', '=', 'Dealer'), ('category_id', '=', 'Retailer')]
    )
    communication_media = fields.Many2one('communication.media', string='Communication Media', tracking=True)

    service_type = fields.Many2one('service.type', string='Service Type', tracking=True)
    imei_no = fields.Char(string='IMEI/Serial No', readonly=False, state={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', string="Product", readonly=True,
                                 state={'draft': [('readonly', False)]})
    invoice = fields.Char(string='Invoice No', tracking=True, readonly=True, state={'draft': [('readonly', False)]})
    in_attachment = fields.Binary(string='Invoice Attachment')
    p_date = fields.Date(string='POP Date')
    customer_id = fields.Many2one('res.partner', string='Customer', tracking=True, readonly=True,
                                  state={'draft': [('readonly', False)]})
    warranty_status = fields.Many2one('warranty.status', string=' Warranty Status', tracking=True)
    warranty_expiry_date_l = fields.Date(string='Warranty Expiry Date(L)', readonly=True,
                                         state={'draft': [('readonly', False)]})
    warranty_expiry_date_p = fields.Date(string='Warranty Expiry Date(P)', readonly=True,
                                         state={'draft': [('readonly', False)]})
    warranty_void_reason_1 = fields.Many2one('warranty.void.reason', string="warranty Void Reason", tracking=True)
    guaranty_expiry_date = fields.Date(string='Guaranty Expiry Date')
    departments = fields.Many2one('field.service.department', required=True, string='Department', tracking=True, )
    priority_lavel_duration = fields.Char(string='Priority Level Duration')
    phone = fields.Char(string='Phone')
    user_id = fields.Many2one('res.users', string='users', tracking=True, default=lambda self: self.env.user)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string="Priority")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('service_for_approval', 'Submitted For Approval'),
        ('approval', 'Approved'),
        ('cancel', 'Canceled')], default='draft', string="Status", required=True)

    priority_levels = fields.Many2one('field.service.priority.level', string='Priority Level', tracking=True)
    p_delivery_date = fields.Date(string='Possible Delivery Date')
    customer_remark = fields.Char(string='Customer Remark')
    remark = fields.Char(string='Remark', tracking=True)
    symptoms_lines_ids = fields.One2many('symptoms.lines', 'order_id', string="Symptoms")
    symptoms_lines_id = fields.Many2one('symptoms.lines', string="Symptoms")
    special_notes_ids = fields.One2many('special.notes', 'order_id', string="Special Notes", )
    qa_details_ids = fields.One2many('quality.assurance.details', 'qa_details1', string='QA Details ')
    repair_status = fields.Selection([
        ('pending', 'Pending'),
        ('not_repaired', 'Not-repaired'),
        ('repairing', 'Repairing'),
        ('repaired', 'Repaired'),
        ('ready for qc', 'Ready For QC')
    ], string='Repair Status', tracking=True, default='pending')

    product_receive_date = fields.Date(string='Product Receive Date')
    delivery_date = fields.Date(string='Delivery Date')
    item_receive_branch = fields.Many2one('res.branch', string='Item Receive Branch')
    item_receive_status = fields.Char(string='Item Receive Status')
    receive_customer = fields.Boolean(string='Is Receive From Customer', default=False)
    so_transfer = fields.Boolean(string='Is So Transfer')
    is_sms = fields.Boolean(string='Is SMS')
    special_note = fields.Char(string="Special Note")
    branch_name = fields.Many2one('res.branch', tracking=True, required=True)
    current_branch = fields.Many2one('res.branch', tracking=True)

    def transfer_button(self):
        for rec in self:
            print(self.id)

            if rec.state != "approval":
                raise ValidationError("Service Order is not approved yet")
            else:
                if rec.receive_customer != True:
                    raise ValidationError("Service Order Item is not received yet")
                else:
                    user = self.env['res.users'].browse(self._context.get('uid'))
                    warehouse_data = self.env['stock.warehouse'].search([
                        ('branch_id', '=', rec.branch_name.id),
                        ('company_id', '=', user.company_id.id),

                    ])
                    picking_type = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_data.id),
                         ('code', '=', 'internal')], limit=1)
                    picking = self.env['stock.picking'].search(
                        [('picking_type_id', '=', picking_type.id),
                         ('service_order_id', '=', rec.id)]).id
                    print(picking)
                    result = self.env["ir.actions.actions"]._for_xml_id('usl_service_erp.action_order_transfer')
                    if picking:
                        result['domain'] = [('id', '=', picking)]
                    else:
                        # override the context to get rid of the default filtering on operation type
                        result['context'] = {'default_service_order_id': rec.id,
                                             'default_picking_type_id': picking_type.id}
                        # choose the view_mode accordingly

                        res = self.env.ref('usl_service_erp.view_picking_form_field_service_transfer', False)
                        form_view = [(res and res.id or False, 'form')]
                        result['views'] = form_view + [(state, view) for state, view in result.get('views', []) if
                                                       view != 'form']
                        # result['res_id'] = engineers.id
                    return result
    def receive_button(self):
        for rec in self:
            print(self.id)
            user = self.env['res.users'].browse(self._context.get('uid'))
            warehouse_data = self.env['stock.warehouse'].search([
                ('branch_id', '=', rec.branch_name.id),
                ('company_id', '=', user.company_id.id),

            ])
            picking_type = self.env['stock.picking.type'].search(
                [('warehouse_id', '=', warehouse_data.id),
                 ('code', '=', 'incoming')], limit=1)
            picking = self.env['stock.picking'].search(
                [('picking_type_id', '=', picking_type.id),
                 ('service_order_id', '=', rec.id)]).id

            if rec.state != "approval":
                raise ValidationError("Service Order is not approved yet")
            else:
                print(picking)
                result = self.env["ir.actions.actions"]._for_xml_id('usl_service_erp.action_order_receive')
                if picking:
                    result['domain'] = [('id', '=', picking)]
                else:
                    result['context'] = {'default_service_order_id': rec.id,
                                         'default_picking_type_id': picking_type.id,
                                         'default_partner_id': self.customer_id.id,

                                         }

                    res = self.env.ref('usl_service_erp.view_picking_form_field_service_receive', False)
                    form_view = [(res and res.id or False, 'form')]
                    result['views'] = form_view + [(state, view) for state, view in result.get('views', []) if
                                                   view != 'form']
                return result


    def set_line_number(self):
        sl_no = 0
        for line in self.symptoms_lines_ids:
            sl_no += 1
            line.sl_no = sl_no
        return

    def set_line_number_ids(self, ids):
        sl_no = 0
        for line in ids:
            sl_no += 1
            line.sl_no = sl_no
        return sl_no

    @api.model
    def create(self, vals):
        if vals.get('order_no', _('New')) == _('New'):
            x = datetime.datetime.now()
            s = str(x.year)[2:] + str(x.month) + str(x.day)
            s1 = str(self.env['ir.sequence'].next_by_code('field.service') or _('New'))
            s2 = s1[:2] + s + s1[2:]
            vals['order_no'] = s2

        if vals.get('symptoms_lines_ids') != []:
            res = super(FieldService, self).create(vals)
            if res.qa_details_ids !=[]:
                res.set_line_number()
                res.qa_details_ids = [(5, 0, 0)]
                val_list = []
                vals = (0, 0, {
                    'order_id': res.order_no,
                    'order_date': res.order_date,
                    'product_id': res.product_id.id,
                    #'warranty_status': res.warranty_status,
                    'diagonisis_date': res.order_date,
                    'task_status': res.repair_status,

                })
                val_list.append(vals)
                res.qa_details_ids = val_list
            self.env['assign.engineer.details'].create({'order_id': res.id})
            return res
        else:
            raise ValidationError("Service Order will not be created with blank symptoms line")

    @api.onchange("warranty_void_reason_1")
    def _onchange_iwarranty_void_reason(self):
        if self.warranty_void_reason_1 != None:
            self.warranty_status = None

    @api.onchange("imei_no")
    def _onchange_imei_number(self):
        user = self.env['res.users'].browse(self._context.get('uid'))
        imei_number = self.env['field.service.data'].search([('serial_no', '=', self.imei_no)])
        # self.serial_no = self.order_id.imei_no.serial_no
        self.product_id = imei_number.product_id
        self.customer_id = imei_number.customer_id
        self.warranty_status = imei_number.warranty_status
        self.invoice = imei_number.invoice
        self.warranty_expiry_date_l = imei_number.warranty_expiry_date_l
        self.warranty_expiry_date_p = imei_number.warranty_expiry_date_p
        self.branch_name = user.branch_id
        self.item_receive_branch = user.branch_id
        self.current_branch = self.branch_name.id

        # self.in_attachment=imei_number.invoice
        if self.receive_customer != True:
            self.item_receive_status = "Pending"

    def actions_test(self):
        return


    def reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_service_for_approval(self):
        for rec in self:
            rec.state = 'service_for_approval'

    def action_approval(self):
        for rec in self:
            rec.state = 'approval'


    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_symptoms(self):
        return

    def write(self, vals):
        res = super().write(vals)
        if self.qa_details_ids:
            self.set_line_number_ids(self.qc_line_ids)
        if self.symptoms_lines_ids:
            self.set_line_number_ids(self.symptoms_lines_ids)
        return res

    def action_view_assign(self):
        data = self.env['assign.engineer.details'].search([('order_id', '=', self.id)])

        if data:
            print('succes')
        else:
            print("create")
            self.env['assign.engineer.details'].create({'order_id': self.id})
        data = self.env['assign.engineer.details'].search([('order_id', '=', self.id)])

        print("**********", data)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': f"/web#id={data.id}&cids=1&menu_id=316&action=437&model=assign.engineer.details&view_type=form"

        }

    def action_diagnosis_repair(self):

        return {
            'name': _('Diagnosis Repair'),
            'type': 'ir.actions.act_window',
            'res_model': 'diagnosis.repair',
            'view_mode': 'tree,form',
            'context': {'default_order_id': self.id},
            'target': 'current',
            'domain': [('order_id', '=', self.id)],
        }


class ResUsers(models.Model):
    _inherit = "res.users"
    _rec_name = "name"

    task_count = fields.Integer(string='Task Count', compute='_compute_task_count')

    def _compute_task_count(self):
        for rec in self:
            task_count = self.env['diagnosis.repair'].search_count([('engineer', '=', rec.name)])
            rec.task_count = task_count

    def name_get(self):
        list = []
        for rec in self:
            name = str(rec.name) + ' ' + '(' + str(rec.task_count) + ')'
            list.append((rec.id, name))
        return list

    def _get_domain(self):
        for rec in self:
            if rec.has_group('usl_service_erp.group_service_manager'):
                return []
            if rec.has_group('usl_service_erp.group_service_engineer'):
                return [('engineer', '=', rec.id)]

            else:
                return []


class SymptomsLines(models.Model):
    _name = "symptoms.lines"
    _description = "Symptoms Lines"

    symptoms = fields.Many2one('symptoms.type', required=True, string="Symptoms")
    reason = fields.Many2one("reasons.type", required=True, string="Reason", readonly=False)
    sl_no = fields.Integer(string='SLN.')
    order_id = fields.Many2one('field.service', required=True, string="Order")


class SpecialNotes(models.Model):
    _name = "special.notes"
    _description = "Special Notes"

    sl_no = fields.Integer(string='SLN.')
    wui = fields.Char(string="Windows User Id")
    wup = fields.Char(string="Windows User Password")
    bui = fields.Char(string="BIOS User Id")
    bup = fields.Char(string="BIOS User Password")
    order_id = fields.Many2one('field.service', string="Order")
