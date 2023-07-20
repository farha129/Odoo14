# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    journal_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'), ], related='journal_id.type',
        help="Technical field used to adapt the interface to the journal selected.", readonly=True)

    def _check_payment_constraints(self):
        if self.journal_type == 'bank' and not self.partner_id.bank_ids:
            raise ValidationError(_('Please set "%s"''s bank account.' % (self.partner_id.name)))

        if not self.company_id.ceo_id:
            raise ValidationError(
                _('Please set CEO of this company: "%s" \nConfigure it in Accounting/Configuration/Settings') %
                (self.company_id.name))

        if not self.company_id.accountant_id:
            raise ValidationError(
                _('Please set general accountant of this company: "%s" \nConfigure it in Accounting/Configuration/Settings') %
                (self.company_id.name))

    def print_es_cash_receipt(self):
        self._check_payment_constraints()
        self.ensure_one()
        res = self.read()
        res = res and res[0] or {}
        datas = {'ids': [],
                 'model': 'account.payment',
                 'form': res
                 }

        return self.env.ref('es_report_payment.action_report_payment_cash_receipt').report_action(self, data=datas)

    def print_es_bank_receipt(self):
        self._check_payment_constraints()
        self.ensure_one()
        res = self.read()
        res = res and res[0] or {}
        datas = {'ids': [],
                 'model': 'account.payment',
                 'form': res
                 }

        return self.env.ref('es_report_payment.action_report_payment_bank_receipt').report_action(self, data=datas)
