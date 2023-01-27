# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Hrforms(models.Model):
    _name = 'hr.forms'

    _description = 'Forms'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Ref", default="/", readonly=True)
    name_forms = fields.Char(string="Name", required=True)
    attachment_id = fields.Binary('Attachment', help='Please Attachment Form', required=True)
    note = fields.Char(string="Nots")
    categroy_id = fields.Many2one('hr.forms.categroy', string='Categroy')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.forms.seq') or ' '
        res = super(Hrforms, self).create(vals)
        return res


class Hrformscategroy(models.Model):
    _name = 'hr.forms.categroy'

    _description = 'Forms Categroy'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Name",)
    note = fields.Char(string="Nots",)
    company_id = fields.Many2one('res.company', string = 'Company', default=lambda self: self.env.company)



