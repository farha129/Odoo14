# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Jesni Banu(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api

import datetime
import  arabic_reshaper
from datetime import timedelta


from datetime import datetime


class ProjectTaskTimeSheet(models.Model):
    _inherit = 'account.analytic.line'

    date_start = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='End Date', readonly=1)
    timer_duration = fields.Float(invisible=1, string='Time Duration (Minutes)')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    task_timer = fields.Boolean(string='Timer', default=False)
    is_user_working = fields.Boolean(
        'Is Current User Working',
        help="Technical field indicating whether the current user is working. ")
    duration = fields.Float(
        'Real Duration', compute='_compute_duration', store=True)
    real_date_start = fields.Datetime(
        'Real Start Date', copy=False,
        help="Date at which you plan to start the production.",
        index=True)
    reminder_day = fields.Integer(string="Reminder Day",readonly= True)
    # reminder_period = fields.Integer(string="Reminder Period",readonly= True)# reminder period after delay request for mrp order

    def _get_reminder_day(self):
        mrp_object = self.env['mrp.production'].search([])
        for mrp in mrp_object:
            today_s = fields.Date.today()
            today = today_s.strftime('%Y-%m-%d')
            if mrp.end_date:
                end_date = mrp.end_date
            
                mrp.reminder_day = (end_date - today_s).days

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for mr in self:
            # mrp_object = self.env['mrp.production'].search([('origin', '=', mr.origin)])
            print('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
            mr.task_timer = False
        return res

    def action_start(self):
        for mr in self:

            mrp_object = self.env['mrp.production'].search([('origin', '=', mr.origin)])
            print('llllllllllllllllllllllllllllllllllllllxxxxxl', mrp_object)
            sale_obj = self.env['sale.order'].search([('name', '=', mr.origin)])
            total_mater = sum(rec.product_uom_qty for rec in sale_obj.order_line)

            print('llllllllllllllll888888888llem', sale_obj)
            for so in sale_obj:
                today_s = fields.Date.today()
                today = today_s.strftime('%Y-%m-%d')
                days = so.implemented_period * (so.company_id.percent_period_date / 100)
                date_mrp = fields.Date.to_string(so.date_order + timedelta(days))
                print('oooooooooooooooooooookkkkkkkkkkkkkkkkkkk sooooooooooooooooooooooooooooo', so.name)
                # mrp_object = self.env['mrp.production'].search([('origin', '=', so.name)])
                obj_employees = self.env['hr.employee'].search([])
                employees_cut = []
                employees_gath = []
                employees_glass = []
                employees_install = []
                day_number_cut = 0
                overtime_cut = 0
                day_number_install = 0
                overtime_install = 0
                day_number_gathering = 0
                overtime_gath = 0
                day_number_glass = 0
                overtime_glass = 0
                text = ''
                qty = ''

                for emp in obj_employees:
                    if emp.tech_type == 'tech_cut':
                        employees_cut.append(emp.id)
                    if emp.tech_type == 'tech_gathering':
                        employees_gath.append(emp.id)
                    if emp.tech_type == 'tech_glass':
                        employees_glass.append(emp.id)
                    if emp.tech_type == 'tech_install':
                        employees_install.append(emp.id)
                for p in mrp_object:
                    day_number_cut += p.day_number_cut
                    day_number_install += p.day_number_install
                    day_number_gathering += p.day_number_gathering
                    day_number_glass += p.day_number_glass
                    overtime_cut += p.overtime_cut
                    overtime_install += p.overtime_install
                    overtime_gath += p.overtime_gath
                    overtime_glass += p.overtime_glass
                    p.task_timer = True
                    p.real_date_start = datetime.now()
                    ###################################################################################
                    #if the request delay must be calculated New End Date depandens real_date_start and Except fraiday
                    if p.state == 'delay':
                        taks_object = self.env['project.task'].search([('project_id', '=', p.project_id.id)])
                        if taks_object:
                            for task in taks_object:
                                task.unlink()

                        end_date =   fields.Date.to_string(p.real_date_start + timedelta(p.reminder_day))
                        t1 = datetime.strptime(fields.Date.to_string(p.real_date_start), '%Y-%m-%d')
                        t2 = datetime.strptime(str(end_date), '%Y-%m-%d')
                        delta = timedelta(days=1)
                        count = 0
                        while t1 <= t2 + timedelta(count):
                            t1 += delta
                            if t1.weekday() in [4]:
                                print('holiday', t1.strftime("%Y-%m-%d"))
                                count += 1
                        p.end_date = fields.Date.to_string(
                            datetime.strptime(end_date, "%Y-%m-%d").date() + timedelta(count))

                        p.state = 'confirmed'
                    ################################################################################


                    qty = str(p.product_qty)
                    text += p.product_id.name + arabic_reshaper.reshape(
                        ' مساحتها ') + '      ' + qty + '      ' + "\n"

                deadline_cut = fields.Date.to_string(p[0].real_date_start + timedelta(day_number_cut))

                t1 = datetime.strptime(fields.Date.to_string(p[0].real_date_start) , '%Y-%m-%d')
                t2 = datetime.strptime(str(deadline_cut), '%Y-%m-%d')
                delta = timedelta(days=1)
                count = 0
                while t1 <= t2 + timedelta(count):
                    t1 += delta
                    if t1.weekday() in [4]:
                        print('holiday',t1.strftime("%Y-%m-%d"))

                        count += 1
                deadline_cut = fields.Date.to_string(
                    datetime.strptime(deadline_cut, "%Y-%m-%d").date() + timedelta(count))
                #################################################################################################
                deadline_gathering = fields.Date.to_string(
                    datetime.strptime(deadline_cut, "%Y-%m-%d").date() + timedelta(day_number_gathering))
                t1 = datetime.strptime(str(deadline_cut), '%Y-%m-%d')
                t2 = datetime.strptime(str(deadline_gathering), '%Y-%m-%d')
                delta = timedelta(days=1)
                count = 0
                while t1 <=  t2 + timedelta(count):
                    t1 += delta
                    if t1.weekday() in [4] :
                        print('holiday',t1.strftime("%Y-%m-%d"))
                        count += 1

                deadline_gathering = fields.Date.to_string(
                    datetime.strptime(deadline_gathering, "%Y-%m-%d").date() + timedelta(count))


                #################################################################################################

                deadline_glass = fields.Date.to_string(datetime.strptime(deadline_gathering, "%Y-%m-%d").date() + timedelta(day_number_glass))
                t1 = datetime.strptime(str(deadline_gathering), '%Y-%m-%d')
                t2 = datetime.strptime(str(deadline_glass), '%Y-%m-%d')
                # delta = timedelta(days=1)
                count = 0
                while t1 <= t2 + timedelta(count):
                    t1 += delta
                    if t1.weekday() in [4] :
                        print('holiday',t1.strftime("%Y-%m-%d"))
                        count += 1
                deadline_glass = fields.Date.to_string(datetime.strptime(deadline_glass, "%Y-%m-%d").date() + timedelta(count))

                ###################################################################################################
                deadline_install = fields.Date.to_string(
                    datetime.strptime(deadline_glass, "%Y-%m-%d").date() + timedelta(day_number_install))
                t1 = datetime.strptime(str(deadline_glass), '%Y-%m-%d')
                t2 = datetime.strptime(str(deadline_install), '%Y-%m-%d')
                # delta = timedelta(days=1)
                count = 0
                while t1 <= t2 + timedelta(count):
                    t1 += delta
                    if t1.weekday() in [4] :
                        print('holiday',t1.strftime("%Y-%m-%d"))
                        count += 1
                deadline_install = fields.Date.to_string(
                    datetime.strptime(deadline_install, "%Y-%m-%d").date()  + timedelta(count))

                ################################################################################################
                start_cut =  fields.Date.to_string(p[0].real_date_start)

                vals4 = {'name': arabic_reshaper.reshape('تركيب') + ' ' + arabic_reshaper.reshape(
                    'للعميل ') + ' ' + so.partner_id.name,
                         'project_id': so.project_id.id,
                         'employee_ids': employees_install or False,
                         'task_type': 'installation' or False,
                         'user_id': False,
                         'description': text or False,
                         'total_mater': total_mater or False,

                         'date_start': deadline_glass or False,
                         'date_deadline': deadline_install or False,
                         'partner_id': so.partner_id.id or False,
                         'analytic_account_id': so.analytic_account_id.id or False,
                         # 'mrp_id': p.id or False
                         }

                self.env['project.task'].create(vals4)
                vals3 = {'name': arabic_reshaper.reshape('زجاج') + ' ' + arabic_reshaper.reshape(
                    'للعميل ') + ' ' + so.partner_id.name,
                         'project_id': so.project_id.id,
                         'employee_ids': employees_glass or False,
                         'task_type': 'glass' or False,
                         'user_id': False,
                         'description': text or False,
                         'total_mater': total_mater or False,
                         'date_start': deadline_gathering or False,

                         'date_deadline': deadline_glass or False,
                         'partner_id': so.partner_id.id or False,
                         'analytic_account_id': so.analytic_account_id.id or False,
                         # 'mrp_id': p.id or False
                         }
                self.env['project.task'].create(vals3)
                vals2 = {'name': arabic_reshaper.reshape('تجميع') + ' ' + arabic_reshaper.reshape(
                    'للعميل ') + ' ' + so.partner_id.name,
                         'project_id': so.project_id.id,
                         'employee_ids': employees_gath or False,
                         'task_type': 'gathering' or False,
                         'user_id': False,
                         'description': text or False,
                         'total_mater': total_mater or False,
                         'date_start': deadline_cut or False,
                         'date_deadline': deadline_gathering or False,
                         'partner_id': so.partner_id.id or False,
                         'analytic_account_id': so.analytic_account_id.id or False,
                         # 'mrp_id': p.id or False
                         }
                self.env['project.task'].create(vals2)

                vals = {'name': arabic_reshaper.reshape('قص') + ' ' + arabic_reshaper.reshape(
                    'للعميل ') + ' ' + so.partner_id.name,
                        'project_id': so.project_id.id,
                        'employee_ids': employees_cut or False,
                        'task_type': 'cut' or False,
                        'description': text or False,
                        'total_mater': total_mater or False,
                        'date_start': start_cut  or False,
                        'user_id': False,
                        'date_deadline': deadline_cut,
                        'partner_id': so.partner_id.id or False,
                        'analytic_account_id': so.analytic_account_id.id or False,
                        # 'mrp_id': p.id or False
                        }
                self.env['project.task'].create(vals)
                overtime = {
                    # 'project_id': so.project_id.id,
                    'note': text or False,
                    'deadline_cut': deadline_cut,
                    'deadline_gathering': deadline_gathering,
                    'deadline_glass': deadline_glass,
                    'deadline_install': deadline_install,
                    'number_hours_cut': overtime_cut,
                    'number_hours_gathering': overtime_gath,
                    'number_hours_glass': overtime_glass,
                    'number_hours_install': overtime_install,
                    'customer_id': so.partner_id.id or False,
                    'sale_id': so.id or False,
                    # 'analytic_account_id': so.analytic_account_id.id or False,
                    # 'mrp_id': p.id or False
                }
                self.env['overtime.mrp'].create(overtime)

                install = {
                    # 'project_id': so.project_id.id,
                    'note': text or False,
                    'date_order': deadline_glass,
                    'deadline_install': deadline_install,
                    'period_install': day_number_install,
                    'employee_ids': employees_install,
                    'customer_id': so.partner_id.id or False,
                    'sale_id': so.id or False,
                    # 'analytic_account_id': so.analytic_account_id.id or False,
                    # 'mrp_id': p.id or False
                }
                self.env['install.mrp'].create(install)

    def action_stop(self):
        self.task_timer = False
        # self.real_date_start = datetime.datetime.now()

    # def _compute_is_user_working(self):
    #     """ Checks whether the current user is working """
    #     for order in self:
    #         if order.timesheet_ids.filtered(lambda x: (x.user_id.id == self.env.user.id) and (not x.date_end)):
    #             order.is_user_working = True
    #         else:
    #             order.is_user_working = False

    @api.constrains('task_timer')
    def toggle_start(self):
        if self.task_timer is True:
            self.write({'is_user_working': True})

        else:
            self.write({'is_user_working': False})

            #
