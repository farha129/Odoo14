# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, sql_db, _
from odoo.tools.mimetypes import guess_mimetype
import requests
import json
import base64
from datetime import datetime
import time
import html2text
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def get_link(self):
        for sale in self:
            base_url = sale.get_base_url()
            share_url = sale._get_share_url(redirect=True, signup_partner=True)
            url = base_url + share_url
            return url
     
    
    def _get_whatsapp_server(self):
        WhatsappServer = self.env['ir.whatsapp_server']
        whatsapp_ids = WhatsappServer.search([('status','=','authenticated')], order='sequence asc', limit=1)
        if whatsapp_ids:
            return whatsapp_ids
        return False
    
    def send_whatsapp_automatic(self):
        for sale in self:
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            MailMessage = self.env['mail.message']
            WhatsappComposeMessage = self.env['whatsapp.compose.message']
            Attachment = self.env['ir.attachment']
            #template_id = self.env.ref('aos_whatsapp_sale.sales_confirm_status', raise_if_not_found=False)
            template_id = self.env.ref('aos_whatsapp_sale.sales_confirm_status', raise_if_not_found=False)
            if self._get_whatsapp_server() and self._get_whatsapp_server().status == 'authenticated':
                KlikApi = self._get_whatsapp_server().klikapi()
                KlikApi.auth()
                #===============================================================
                #CREATE ATTAHCMENT
                #===============================================================
                # res_name = sale.name.replace('/', '_')
                # report = report_id.report_template
                # report_service = report.report_name
                # if report.report_type not in ['qweb-html', 'qweb-pdf']:
                #     raise UserError(_('Unsupported report type %s found.') % report.report_type)
                # res, format = report.render_qweb_pdf([sale.id])
                # res = base64.b64encode(res)
                # if not res_name:
                #     res_name = 'report.' + report_service
                # ext = "." + format
                # if not res_name.endswith(ext):
                #     res_name += ext
                # mimetype = guess_mimetype(base64.b64decode(res))
                # if mimetype == 'application/octet-stream':
                #     mimetype = 'video/mp4'
                # str_mimetype = 'data:' + mimetype + ';base64,'
                # attachment = str_mimetype + str(res.decode("utf-8"))
                # message_attach = {
                #     'body': attachment,
                #     'filename': res_name,
                #     'caption': res_name,
                # }

                # if template.report_template:
                # for res_id in template_res_ids:
                attachments = []
                report_name = sale.name.replace('/','_')
                # report_name = template._render_field('report_name', [res_id])[res_id]
                # report = template.report_template
                # report_service = report.report_name
                
                report = self.env.ref('sale.action_report_saleorder')#._render_qweb_pdf(inv.id)
                if report.report_type in ['qweb-html', 'qweb-pdf']:
                    result, format = report._render_qweb_pdf([sale.id])
                else:
                    res = report._render([sale.id])
                    if not res:
                        raise UserError(_('Unsupported report type %s found.', report.report_type))
                    result, format = res

                # TODO in trunk, change return format to binary to match message_post expected format
                result = base64.b64encode(result)
                if not report_name:
                    report_name = 'report.' + report_name
                ext = "." + format
                if not report_name.endswith(ext):
                    report_name += ext
                attachments.append((report_name, result))
                for attachment in attachments:
                    attachment_data = {
                        'name': attachment[0],
                        'store_fname': attachment[0],
                        'datas': attachment[1],
                        'type': 'binary',
                        'res_model': 'sale.order',
                        'res_id': sale.id,
                    }
                    Attachment.create(attachment_data)
                #print ('===s===',attachments)
                # results[res_id]['attachments'] = attachments
                #===============================================================             
                template = template_id.generate_email(sale.id, ['body_html', 'subject'])
                body = template.get('body_html')
                subject = template.get('subject')
                try:
                    body = body.replace('_PARTNER_', sale.partner_id.name)
                except:
                    _logger.warning('Failed to send Message to WhatsApp number %s', sale.partner_id.whatsapp)         
                attachment_ids = []
                chatIDs = []
                message_data = {}
                send_message = {}
                status = 'error'
                partner_id_boolean = self.env.user.has_group('base.group_system')

                if partner_id_boolean:
                    group_id = self.env.ref('base.group_system').users
                    partners_ids = group_id.mapped('partner_id')    

                if sale.partner_id:
                    partners = sale.partner_id
                    # if sale.partner_id.child_ids:
                    #     #ADDED CHILD FROM PARTNER
                    #     for partner in sale.partner_id.child_ids:
                    #         partners += partner   
                res_name = sale.name.replace('/', '_')
                # domain = [('res_id', '=', inv.id), ('name', 'like', res_name + '%'), ('res_model', '=', 'account.move')] 
                is_attachment_exists = Attachment.search([('res_id', '=', sale.id), ('name', 'like', res_name + '%'), ('res_model', '=', 'sale.order')], limit=1)# if len(active_ids) == 1 else is_exists
                #print ('==is_attachment_exists==',is_attachment_exists)
                if is_attachment_exists:
                    attachment_ids = is_attachment_exists

                for partner in partners_ids:
                    if partner.whatsapp:
                        if not attachment_ids:
                            #SEND MESSAGE
                            whatsapp = partner._formatting_mobile_number()
                            message_data = {
                                'method': 'sendMessage',
                                'phone': whatsapp,
                                'body': html2text.html2text(body) + sale.get_link(),
                                'origin': sale.name,
                                'link': sale.get_link(),
                            }                        
                            if partner.chat_id:
                                message_data.update({'chatId': partner.chat_id, 'phone': '', 'origin': sale.name, 'link': sale.get_link()})
                            data_message = json.dumps(message_data)
                            send_message = KlikApi.post_request(method='sendMessage', data=data_message)
                            if send_message.get('message')['sent']:
                                chatID = send_message.get('chatID')
                                status = 'send'
                                partner.chat_id = chatID
                                chatIDs.append(chatID)
                                _logger.warning('Success to send Message to WhatsApp number %s', whatsapp)
                            else:
                                status = 'error'
                                _logger.warning('Failed to send Message to WhatsApp number %s', whatsapp)
                            new_cr.commit()
                        elif attachment_ids:
                            #print ('====attachment_ids===',attachment_ids.name)
                            status = 'pending'
                            whatsapp = partner._formatting_mobile_number()
                            print ('nnnnnnnnnnnnnnnnnnnnnnnmmmmmmmm',whatsapp)
                            message_data = {
                                'method': 'sendFile',
                                'body': sale.name,#,html2text.html2text(body) + inv.get_link(),
                                'phone': whatsapp,
                                'chatId': partner.chat_id or '',
                                #'body': attachment_ids.datas.split(",")[0],
                                'filename': attachment_ids.name,
                                'caption': html2text.html2text(body) + sale.get_link(),#body.replace('_PARTNER_', partner.name).replace('_NUMBER_', inv.name).replace('_AMOUNT_TOTAL_', str(inv.format_amount(inv.amount_total, inv.currency_id)) if inv.currency_id else '').replace('\xa0', ' '),#att['caption'],
                            }
                            #print ('===',html2text.html2text(body) + sale.get_link())
                            if partner.chat_id != whatsapp:
                                partner.chat_id = whatsapp
                                message_data.update({'chatId': whatsapp, 'phone': whatsapp, 'origin': sale.name, 'link': sale.get_link()})
                        #time.sleep(3)                
                        #=======================================================
                        #SEND ATTACHMENT
                        #=======================================================
                        # message_attach.update({'phone': mobile})
                        # data_attach = json.dumps(message_attach)
                        # request_attach = requests.post(path + '/sendFile', data=data_attach, params=token_value, headers={'Content-Type': 'application/json'})
                        # if request_attach.status_code == 200:
                        #     data_attach = json.loads(request_attach.text)
                        #     chat_id = data_attach.get('id') and data_attach.get('id').split('_')
                        #     whatsapp_log_obj.create(
                        #         {'name': part.name,
                        #          'msg_date': datetime.now(),
                        #          'link': path + '/sendFile',
                        #          'data': data_attach,
                        #          'chat_id': chat_id[1],
                        #          'message': request_attach.text,
                        #          'message_body': res_name,
                        #          'status': 'send'
                        #     })
                        #     part.chat_id = chat_id[1]
                        # else:
                        #     whatsapp_log_obj.create(
                        #         {'name': part.name,
                        #          'msg_date': datetime.now(),
                        #          'link': path + '/sendFile',
                        #          'data': data_attach,
                        #          'message': request_attach.text,
                        #          'message_body': res_name,
                        #          'status': 'error'
                        #     })
                        # new_cr.commit()
                        # time.sleep(3)
                        #=======================================================

                    AllchatIDs = ';'.join(chatIDs)
                    vals = WhatsappComposeMessage._prepare_mail_message(self.env.user.partner_id.id, AllchatIDs, sale and sale.id,  'sale.order', body, message_data, subject, partner.ids, attachment_ids, send_message, status)
                    MailMessage.sudo().create(vals)
                    new_cr.commit()
                #time.sleep(3)
