from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from datetime import datetime
import xlsxwriter
from io import StringIO, BytesIO
from odoo.tools import image_process



class pos_wizard(models.TransientModel):
    _name = 'sale_categ.wizard'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    customer_id = fields.Many2one('res.partner','Customer')
    warehouse_id = fields.Many2one('stock.warehouse','Warehouse',required=True)
    sale_person = fields.Many2one('res.users','Sale person')
    category_id = fields.Many2many('product.category','sale_wiz_categ_rel','sale_wiz','categ_id','Categories',required=True)
    uom_id = fields.Many2one('uom.uom','Unit of measure')
    # pdf method
    def generate_report(self):
        categ_names=''
        for categ in self.category_id:
            categ_names = categ_names + str(categ.name) + ', '


        location_id= self.warehouse_id.lot_stock_id.id




        data = {'start_date': self.start_date,'end_date': self.end_date, 'customer_id': self.customer_id.id,'warehouse_id':self.warehouse_id.id,'customer_name':self.customer_id.name
                ,'sale_person':self.sale_person.id,'sale_person_name':self.sale_person.name,'location_id':location_id,'category_id':self.category_id.ids,'uom_id':self.uom_id.id,'warehouse_name':self.warehouse_id.name,'categories':categ_names}
        return self.env.ref('sale_fadil.sale_detail_wiz_report').report_action([], data=data)


    # Excel method

    def print_excel(self):
        for report in self:
            comp_logo = report.env.user.company_id.logo
            resized_logo = image_process(comp_logo, size=(200, 200))
            company_id = report.env['res.company'].search([('id', '=', self.env.user.company_id.id)])
            address1 = company_id.street
            address2 = company_id.street2
            country = company_id.country_id.name
            phone = company_id.phone
            website = company_id.website
            report_title = 'Sales Details on category base '
            file_name = _('sales details report.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('Sales details Report')
            image_data = BytesIO(base64.b64decode(resized_logo))  # to convert it to base64 file
            excel_sheet.insert_image('A2', 'logo.png', {'image_data': image_data})

            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': '#0080ff', 'border': 1})
            header_format_sequence = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white'})
            header_format.set_align('center')
            header_format.set_align('vertical center')
            header_format.set_text_wrap()
            format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10'})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format.set_align('center')
            format.set_align('center')
            header_format_sequence.set_align('center')
            format.set_text_wrap()
            format.set_num_format('#,##0.000')
            format_details = workbook.add_format()
            sequence_format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            sequence_format.set_align('center')
            sequence_format.set_text_wrap()
            total_format = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': '#808080', 'border': 1, 'font_size': '10'})
            total_format.set_align('center')
            total_format.set_text_wrap()
            format_details.set_num_format('#,##0.00')
            sequence_id = 0
            col = 0
            row = 7
            first_row = 9
            # excel_sheet.write_merge(0, 5, 1, 5, report_title, style_header_thin_all_main1)
            excel_sheet.merge_range(0, 1, 5, 5, report_title, title_format)
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Start Date:', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, str(report.start_date), format)
            row +=1
            col=0
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'End Date:', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, str(report.end_date), format)
            row +=1
            col=0
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Warehouse:', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, report.warehouse_id.name, format)
            # row +=1
            # col=0
            # excel_sheet.set_column(col, col, 20)
            # excel_sheet.write(row, col, 'Unit of measure:', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 25)
            # excel_sheet.write(row, col, report.uom_id.name, format)
            row +=1
            col=0
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Customer:', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, report.customer_id.name, format)
            row +=1
            col=0
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Sale person:', header_format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, report.sale_person.name, format)
            row +=1
            col=0
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Categories:', header_format)
            col += 1
            for line in report.category_id:
                excel_sheet.set_column(col, col, 25)
                excel_sheet.write(row, col, line.name, format)
                col +=1
            row +=2
            col=0
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Product No', header_format)
            col +=1
            excel_sheet.set_column(col, col, 30)
            excel_sheet.write(row, col, 'Product Name', header_format)
            col +=1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Sold Quantity', header_format)
            col +=1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Unit of measure', header_format)
            col +=1
            excel_sheet.set_column(col, col, 20)
            excel_sheet.write(row, col, 'Unit sale price', header_format)
            col +=1

            excel_sheet.set_column(col, col, 30)
            excel_sheet.write(row, col, 'Stock quantity', header_format)
            col =0
            row +=1
            if report.customer_id and report.sale_person:
                orders_lines_ids = self.env['sale.order.line'].search([('order_id.date_order','>=',report.start_date),('order_id.date_order','<=',report.end_date),
                                                                       ('order_id.state','=','sale'),('warehouse_id','=',report.warehouse_id.id),('order_id.partner_id','=',report.customer_id.id),
                                                                       ('order_id.user_id','=',report.sale_person.id),('product_id.categ_id','in',report.category_id.ids)])
            elif report.customer_id and not report.sale_person:
                orders_lines_ids = self.env['sale.order.line'].search(
                    [('order_id.date_order', '>=', report.start_date), ('order_id.date_order', '<=', report.end_date),
                     ('order_id.state', '=', 'sale'), ('warehouse_id', '=', report.warehouse_id.id),
                     ('order_id.partner_id', '=', report.customer_id.id),('product_id.categ_id','in',report.category_id.ids)])

            elif not report.customer_id and  report.sale_person:
                orders_lines_ids = self.env['sale.order.line'].search(
                    [('order_id.date_order', '>=', report.start_date), ('order_id.date_order', '<=', report.end_date),
                     ('order_id.state', '=', 'sale'), ('warehouse_id', '=', report.warehouse_id.id),
                     ('order_id.user_id', '=', report.sale_person.id),('product_id.categ_id','in',report.category_id.ids)])
            elif not report.customer_id and not report.sale_person:
                orders_lines_ids = self.env['sale.order.line'].search(
                    [('order_id.date_order', '>=', report.start_date), ('order_id.date_order', '<=', report.end_date),
                     ('order_id.state', '=', 'sale'), ('warehouse_id', '=', report.warehouse_id.id),('product_id.categ_id','in',report.category_id.ids)])


            if orders_lines_ids:
                for rec in orders_lines_ids:
                    # sele_convert_qty = rec.product_uom._compute_quantity(rec.product_uom_qty,report.uom_id)
                    qty_ids = self.env['stock.quant'].search([('product_id','=',rec.product_id.id),('location_id','=',rec.warehouse_id.lot_stock_id.id)])
                    qty =sum(qty_ids.mapped('available_quantity'))

                    excel_sheet.write(row, col, rec.product_id.default_code, format)
                    col +=1
                    excel_sheet.write(row, col, rec.product_id.name, format)
                    col +=1
                    excel_sheet.write(row, col,rec.product_uom_qty , format)
                    col +=1
                    excel_sheet.write(row, col,rec.product_uom.name , format)
                    col +=1
                    excel_sheet.write(row, col, rec.price_unit, format)
                    col +=1
                    excel_sheet.write(row, col, qty, format)
                    col =0
                    row +=1
                    # if rec.payment_ids:
                    #
                    #     for line in rec.payment_ids:
                    #         payment_col = col
                    #         excel_sheet.write(row, payment_col, line.payment_method_id.name, title_format)
                    #         payment_col +=1
                    #         excel_sheet.write(row, payment_col, line.amount, format)
                    #         row +=1
                    # col=0

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['sale_categ.wizard.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_mode': 'form',
                'res_model': 'sale_categ.wizard.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }

class pos_report_Excel(models.TransientModel):
    _name = 'sale_categ.wizard.report.excel'
    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)

