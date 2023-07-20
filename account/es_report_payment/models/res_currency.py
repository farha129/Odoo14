# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import models, tools, api, _
import logging

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def amount_to_mongolian_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(self.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang='mn'),
            amt_word=self.currency_unit_label,
        )
        if not self.is_zero(amount - integer_value):
            amount_words += ' ' + 'ба' + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=_num2words(fractional_value, lang='mn'),
                amt_word=self.currency_subunit_label,
            )
        return amount_words
