# -*- coding: utf-8 -*-

from odoo import api, models, _


class ReportBypayslips(models.AbstractModel):
    _name = 'report.report_by_payslips.report_by_payslips_temp'
    _description = 'payslips Report'


    @api.model
    def _get_report_values(self, docids, data=None):
       
        st_date = data['form']['date_from']
        end_date = data['form']['date_to']
        docs = []
        docss = []    
        total_all = 0.0
        total_Meal = total_Medical = total_House_Rent_Allowance = 0.0

        basic = Travel = Meal = Medical = House_Rent_Allowance = Dearness_Allowance = Gross = loan = Incentive = net = Other = 0.0
        total_Travel = total_basic = total_Dearness_Allowance = total_Gross = total_Incentive = total_loan = total_net = total_Other = 0.0

        if st_date and end_date  :
            payslip_month_ids = self.env['hr.payslip'].search([('date_from','>=', st_date),('date_to','<=',end_date)])
            if payslip_month_ids:
            
                for payslip in payslip_month_ids:

                    
                    
                    employee_name = payslip.employee_id.name
                    date  =  payslip.date_from
                    slip_ids = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id)])
                    if slip_ids:
                        for slip_line in slip_ids:
                            category = slip_line.code
                            if category == 'BASIC':
                                basic = slip_line.total
                            if category == 'Travel':
                                Travel = slip_line.total
           
                            if category == 'Meal':
                                Meal = slip_line.total
                                
                            if category == 'Medical':
                                Medical = slip_line.total
                            if category == 'HRA':
                                House_Rent_Allowance = slip_line.total
                            if category == 'DA':
                                Dearness_Allowance = slip_line.total
                            if category == 'Other':
                                Other = slip_line.total
                            if category == 'GROSS':
                                Gross = slip_line.total
                            if category == 'LO':
                                loan = slip_line.total
                            if category == 'INC':
                                Incentive = slip_line.total
                            if category == 'NET':
                                net = slip_line.total


                        docs.append({
                            'employee_name': employee_name,
                            'date': date,
                            'basic':basic,
                            'Meal':Meal,
                            'Travel':Travel,
                            'Medical':Medical,
                            'House_Rent_Allowance':House_Rent_Allowance,
                            'Dearness_Allowance':Dearness_Allowance,
                            'Gross':Gross,
                            'loan':loan,
                            'Other':Other,
                            'Incentive':Incentive,
                            'net':net,
                            })
                        total_basic += basic
                        total_Travel += Travel
                        total_Meal += Meal
                        total_Medical += Medical
                        total_House_Rent_Allowance += House_Rent_Allowance
                        total_Dearness_Allowance += Dearness_Allowance
                        total_Gross += Gross
                        total_Incentive += Incentive
                        total_loan += loan
                        total_net += net
                        total_Other += Other

            docss.append({
                'total_basic': total_basic,
                'total_Travel': total_Travel,
                'total_Meal': total_Meal,
                'total_Medical': total_Medical,
                'total_House_Rent_Allowance': total_House_Rent_Allowance,
                'total_Dearness_Allowance': total_Dearness_Allowance,
                'total_Gross': total_Gross,
                'total_Incentive': total_Incentive,
                'total_loan': total_loan,
                'total_net': total_net,
                'total_Other': total_Other,


        })
        print('rrrrrrrrrrrrrrrrrrrrr',docss)
        return {
	    'doc_ids': data['ids'],
	    'doc_model': data['model'],
	    'st_date':st_date,
	    'end_date':end_date,
	    'docs':docs,
	    'docss':docss,

	    }


 
