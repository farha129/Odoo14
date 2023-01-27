from odoo import models, fields, api, _


class AccConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    incentive_approve = fields.Boolean(default=True, string="Approval from Accounting Department",
                                  help="incentive Approval from account manager")


    def get_values(self):
        res = super(AccConfig, self).get_values()
        res.update(
            incentive_approve=self.env['ir.config_parameter'].sudo().get_param('account.incentive_approve')
        )
        return res


    def set_values(self):
        super(AccConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('account.incentive_approve', self.incentive_approve)

