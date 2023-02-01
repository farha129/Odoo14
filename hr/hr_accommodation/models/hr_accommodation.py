# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import  arabic_reshaper

class Hraccommodation(models.Model):
    _name = 'hr.accommodation'

    _description = 'Accommodation'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Ref", default="/", readonly=True)
    number = fields.Char(string="Number", required=True)
    date = fields.Date(string="Date",)
    date_end = fields.Date(string="End Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    name_eng = fields.Char(string='Name English')
    place_issue = fields.Char('Place Issue')
    date_issue = fields.Date(string="Date Issue",)
    date_birth = fields.Date(string="Date Of Birth",)
    job_position = fields.Many2one('hr.job', string ='Job Position')
    country_id = fields.Many2one('res.country', string ='Nationality')
    religion_id = fields.Many2one('hr.religion',string = 'Religion')
    employer = fields.Char(string = 'Employer')
    state = fields.Selection([('draft', 'Draft'),
        ('draft', 'New'),
        ('run', 'Running'),
        ('end', 'Expired'),
        ('cancel', 'Canceled'),], string="State", default='draft', track_visibility='onchange', copy=False,)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.accommodation.seq') or ' '
        res = super(Hraccommodation, self).create(vals)
        return res

    @api.onchange('employee_id')
    def onchange_employee(self):
        # self.job_position =self.employee_id.job_title
        self.country_id =self.employee_id.country_id
        self.date_birth =self.employee_id.birthday
        self.name_eng =self.employee_id.name_eng
        if self.employee_id.religion_id:
            self.religion_id =self.employee_id.religion_id

        print('8888888888888888888888888888888888888888888888888888888',self.employee_id)


    def action_run(self):
        self.write({'state': 'run'})



    def action_cancel(self):
        self.write({'state': 'cancel'})


    def alarm_expiar(self):
        accom_obj = self.env['hr.accommodation'].search([])

        for rec in accom_obj:

            if rec.date_end:
                today = fields.Date.today()

                if rec.date_end == today and rec.state and rec.state == 'run':
                    print("bbbbbbbbbbbbbbb", today)

                    rec.update({'state': 'end'})
                    group_id = self.env.ref('hr.group_hr_manager').users
                    print("bbbbbbbbbbbbbbb",group_id)
                    partners_ids = group_id.mapped('partner_id').ids
                    print('hhhhhhhhhhhhhhhhhhhhhh', partners_ids)

                    for partenr in partners_ids:
                        obj_name = rec.employee_id.name

                        text = 'هذا الموظف انتهت اقامته'
                        masaage = '(' + format(
                            obj_name) + ')' + '  ' + arabic_reshaper.reshape(text)


                        message_id = self.message_post(body=masaage, subtype_id=self.env.ref('mail.mt_comment').id,
                                                       subject=masaage,
                                                       author_id=self.create_uid.partner_id.id,
                                                       partner_ids=[partenr])
                        self.env['mail.notification'].create({
                            'mail_message_id': message_id.id,
                            'res_partner_id': partenr,
                        })
                        # subtype = self.env['mail.message.subtype'].search([('name', '=', 'Activities')])
                        # admin = self.env['res.users'].search([('id', '=', 2)])
                        # massage_ids = self.env['mail.mail'].create({
                        #     'subject': masaage,
                        #     # 'body_html': 'Dear %s ' % obj_name + '<br/>This record need you action <a href="%s/web#model=%s&amp;id=%s&amp;view_type=form" target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Go record</a>' % (
                        #     #    ),
                        #     # 'email_from': admin.partner_id.email,
                        #     'email_to': admin.partner_id.email,
                        #     'auto_delete': True,
                        #     'state': 'outgoing',
                        #     # 'mail_message_id': mail_mass.id,
                        #     'body': masaage,
                        # })
                        #
                        # massage_ids.send()
                        #
                        # mail_mass = self.env['mail.message'].create({
                        #     # 'email_from': partenr.email,
                        #     # 'email_to':6,
                        #     'author_id':self.create_uid.partner_id.id,
                        #     'model': 'hr.accommodation',
                        #     'message_type': 'notification',
                        #     'body': masaage,
                        #     'channel_ids': [(6, 0, [subtype.id])],
                        #     'subtype_id': subtype.id,
                        #     'moderation_status': 'accepted',
                        #     # 'needaction_partner_ids':[(4, pid) for pid in rec.groups.users.partner_id],
                        #     'notification_ids': [(0, 0, {
                        #         'res_partner_id': partenr,
                        #         'mail_id': massage_ids.id,
                        #         'notification_type': 'email',
                        #         'is_read': True,
                        #         'notification_status': 'ready',
                        #     })],
                        # })

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_accommodation(self):
        """This compute the Accommodtion amount  count of an employee.
            """
        self.acc_count = self.env['hr.accommodation'].search_count([('employee_id', '=', self.id)])

    acc_count = fields.Integer(string="Accommodation Count", compute='_compute_employee_accommodation')








