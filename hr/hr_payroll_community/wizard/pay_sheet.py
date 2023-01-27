# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import xlsxwriter
import base64
import datetime
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from dateutil import relativedelta
import babel
import time
import io

class WizardPayslip(models.TransientModel):
    _name = 'wizard.paysheet'
    _description = 'Print Payslips'

    from_date = fields.Date(string='Date From', required=True, default=time.strftime('%Y-%m-01'))
    to_date = fields.Date(string='Date To', required=True,
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
                          )


    def print_report(self):
        for report in self:
            from_date = report.from_date
            to_date = report.to_date
            # location_id = report.location_id
            logo = report.env.user.company_id.logo
            if self.from_date > self.to_date:
                raise UserError(_("You must be enter start date less than end date !"))

            # report.name = 'Pay-Sheet From ' + str(from_date) + ' To ' + str(to_date)
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(str(from_date), "%Y-%m-%d")))
            locale = self.env.context.get('lang', 'ar_SA')
            report_date = (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
            month_date = (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM', locale=locale)))
            report_title = 'Pay-sheet' + ' ' + report_date
            report_title2 = 'Pay Back' + ' ' + report_date
            file_name = _(report_title + '.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Payroll  ' + '' + report_date)
            excel_sheet2 = workbook.add_worksheet('Pay Back ' + '' + report_date)
            date_format = workbook.add_format(
                {'num_format': 'mm/dd/yyyy', 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'align':'center'})
            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': 'gray', 'border': 1})
            header_format_sequence = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            num_format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            num_format.set_align('center')
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white'})
            title_format.set_align('center')
            format.set_align('right')
            header_format_sequence.set_align('center')
            header_format.set_align('center')
            header_format.set_text_wrap()
            header_format.set_num_format('#,##0.00')
            excel_sheet.set_row(5, 20)
            # excel_sheet.set_column('F:U', 20)
            format.set_text_wrap()
            format.set_num_format('#,##0.00')
            format_details = workbook.add_format()
            format_details.set_num_format('#,##0.00')
            payslip_month_ids = []
            payback_ids = []
            sequence_id = 0
            sequence_id2 = 0
            col = 0
            col2 = 0
            row = 5
            row2 = 5
            first_row = 7
            excel_sheet.set_column(0, 4, 20)
            excel_sheet.set_row(5, 30)
            excel_sheet.merge_range(0, 0, 1, 8, 'My Company', title_format)
            excel_sheet.merge_range(0, 9, 1, 23, '', title_format)
            excel_sheet.merge_range(2, 0, 2, 8, 'Saudia  Country Office', title_format)
            excel_sheet.merge_range(2, 9, 2, 23, '', title_format)
            excel_sheet.merge_range(3, 0, 3, 8, report_title, title_format)
            excel_sheet.merge_range(3, 9, 3, 23, '', title_format)
            excel_sheet.merge_range(4, 0, 4, 23, '', title_format)

            # if logo:
            #     resized_logo = tools.image_get_resized_images(logo)
            #     # resized_logo = image(logo, size=(150, 75))
            #     image_data = io.BytesIO(base64.b64decode(resized_logo))  # to convert it to base64 file
            #     excel_sheet.insert_image('A1', 'logo.png', {'image_data': image_data})


            excel_sheet.write(row, col, '#', header_format)
            col += 1
            excel_sheet.write(row, col, 'ID No', header_format)
            col += 1

            excel_sheet.set_column(col, col, 30)
            excel_sheet.write(row, col, 'Name', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Position', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Starting Date', header_format)
            col += 1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Ending Date', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Basic Salary', header_format)
            col += 1

            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Travel Allowance', header_format)
            col += 1

            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Meal Allowance', header_format)
            col += 1

            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Medical Allowance', header_format)
            col += 1

            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Other Allowance', header_format)
            col += 1


            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Overtime', header_format)
            col += 1

            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Incentive', header_format)
            col += 1

            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Gross', header_format)
            col += 1


            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Loan', header_format)
            col += 1

            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Absence', header_format)
            col += 1

            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'Total Deduction', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, ' Net Salary', header_format)
            col += 1

            payslip_month_ids = report.env['hr.payslip'].search([('date_to', '<=', to_date), ('date_from', '>=', from_date)], order='payslip_run_id ASC')

            if payslip_month_ids:
                for payslip in payslip_month_ids:
                    travel = 0.0
                    incentive = 0.0
                    absent = 0.0
                    loan = 0.0
                    over = 0.0
                    basic = 0.0
                    medical = 0.0
                    loan = 0.0

                    total_deduction = 0.0
                    net = 0.0
                    meal = 0.0
                    Other = 0.0

                    id_no = int(payslip.employee_id.identification_id)
                    job = payslip.employee_id.job_id.name
                    col = 0

                    sequence_id += 1
                    row += 1

                    excel_sheet.write(row, col, sequence_id, header_format_sequence)
                    col += 1
                    excel_sheet.write(row, col,id_no, num_format)

                    col += 1
                    excel_sheet.write(row, col, payslip.employee_id.name, num_format)
                    col += 1
                    if job:
                        excel_sheet.write(row, col, job, num_format)
                    else:
                        excel_sheet.write(row, col, ' ', format)
                    col += 1
                    excel_sheet.write(row, col, payslip.date_from, date_format)
                    col += 1
                    excel_sheet.write(row, col, payslip.date_to, date_format)

                    slip_ids = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id)])
                    if slip_ids:
                        for slip_line in slip_ids:
                            category = slip_line.code
                            if category == 'BASIC':
                                basic = slip_line.total
                            if category == 'Travel':
                                travel = slip_line.total
                            if category == 'Meal':
                                meal = slip_line.total
                            if category == 'Medical':
                                medical = slip_line.total
                            if category == 'Other':
                                Other = slip_line.total
                            if category == 'OVT':
                                over = slip_line.total
                            
                            if category == 'INC':
                                incentive = slip_line.total
                          
                                
                            if category == 'GROSS':
                                over = slip_line.total
                            if category == 'LO':
                                loan = slip_line.total
                            if category == 'ABS':
                                absent = slip_line.total
                            if category == 'DED':
                                total_deduction = slip_line.total
                            if category == 'NET':
                                net = slip_line.total

                        # Sheet1
                        col += 1
                        excel_sheet.write(row, col, basic, format)
                        col += 1
                        excel_sheet.write(row, col, travel, format)
                        col += 1
                        excel_sheet.write(row, col, meal, format)
                        col += 1

                        excel_sheet.write(row, col, medical, format)
                        col += 1
                        excel_sheet.write(row, col, Other, format)
                        col += 1
                        excel_sheet.write(row, col, over, format)
                        col += 1
                        excel_sheet.write(row, col, incentive, format)
                        col += 1

                        excel_sheet.write(row, col, loan, format)
                        col += 1
                        excel_sheet.write(row, col, absent, format)
                        col += 1


                        excel_sheet.write(row, col, total_deduction, format)
                        col += 1
                        excel_sheet.write(row, col, net, format)
                        col += 1






            col = 8
            row += 1

            col2 = 8
            row2 += 1

            excel_sheet.merge_range(row, 0, row, col, 'Total', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(J' + str(first_row) + ':j' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(K' + str(first_row) + ':k' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(L' + str(first_row) + ':l' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(M' + str(first_row) + ':m' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(N' + str(first_row) + ':n' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(O' + str(first_row) + ':o' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(P' + str(first_row) + ':p' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(Q' + str(first_row) + ':q' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(R' + str(first_row) + ':r' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(S' + str(first_row) + ':s' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(T' + str(first_row) + ':t' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(U' + str(first_row) + ':u' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(V' + str(first_row) + ':v' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(W' + str(first_row) + ':w' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(X' + str(first_row) + ':x' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(Y' + str(first_row) + ':y' + str(row) + ')', header_format)
            col += 1
            excel_sheet.write_formula(row, col, 'SUM(Z' + str(first_row) + ':z' + str(row) + ')', header_format)


            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['payslip.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payslip.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }


class payslip_report_excel(models.TransientModel):
    _name = 'payslip.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)

