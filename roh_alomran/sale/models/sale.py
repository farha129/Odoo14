# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

from . import amount_to_ar




class SaleOrder(models.Model):
    _inherit = 'sale.order'

    type = fields.Selection([('direct', 'Direct Sale'),
                             ('deferred', 'Deferred sale')], 'Payment Type', required=True)
    installation = fields.Boolean('Installation requested?')
    destination = fields.Char(string='Destination', readonly=False)
    is_delivery = fields.Boolean('Delivery request?')
    invoice_type = fields.Selection([('wholesale', 'Wholesale'),
                                     ('retail', 'Retail')], 'invoice Type', related='team_id.invoice_type',
                                    required=False, )
    location_source = fields.Selection(selection=[('show_room', 'Show Room'),
                                                  ('main', 'Main WH'), ], string="Location Source", required=False,
                                       related='warehouse_id.location_source')

    state = fields.Selection(selection_add=[('gm_assistant', 'GM Assistant'),
                                            # ('approve', 'Approved'),
                                            ('to_confirm', 'To confirm')])
    department_id = fields.Many2one('hr.department', string='Department',
                                    default=lambda self: self.env.user.department_id.id)
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])

    # member_ids = fields.One2many('res.users', related='team_id.member_ids', string='Channel Members')
    # allow_member_ids = fields.Many2many('res.users', related='team_id.allow_member', string='Allowed Channel Members')

    total_amount_in_words = fields.Char(string="Amount in Words", required=False, compute='_compute_amount_total')
    amount_in_words_arabic = fields.Char(string="Amount in Words Arabic", required=False,
                                         compute='_compute_amount_total')

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        for line in self.order_line:
            line.warehouse_id = self.warehouse_id.id

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoice_status(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.
        """
        unconfirmed_orders = self.filtered(lambda so: so.state not in ['submit', 'to_confirm', 'sale', 'done', ])
        unconfirmed_orders.invoice_status = 'no'
        confirmed_orders = self - unconfirmed_orders
        if not confirmed_orders:
            return
        line_invoice_status_all = [
            (d['order_id'][0], d['invoice_status'])
            for d in self.env['sale.order.line'].read_group([
                ('order_id', 'in', confirmed_orders.ids),
                ('is_downpayment', '=', False),
                ('display_type', '=', False),
            ],
                ['order_id', 'invoice_status'],
                ['order_id', 'invoice_status'], lazy=False)]
        for order in confirmed_orders:
            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]
            if order.state not in ('submit', 'to_confirm', 'sale', 'done',):
                order.invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                order.invoice_status = 'to invoice'
            elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                order.invoice_status = 'invoiced'
            elif line_invoice_status and all(
                    invoice_status in ('invoiced', 'upselling') for invoice_status in line_invoice_status):
                order.invoice_status = 'upselling'
            else:
                order.invoice_status = 'no'

    def ks_calculate_discount(self):
        res = super(SaleOrder, self).ks_calculate_discount()
        for rec in self:
            for tax in rec.taxes_id:
                rec.amount_tax = (rec.total_after_discount * tax.amount) / 100
                rec.amount_total = rec.total_after_discount + rec.amount_tax
        return res

    @api.depends('amount_total', )
    def _compute_amount_total(self):
        self.total_amount_in_words = self.currency_id.amount_to_text(self.amount_total) if self.currency_id else ''
        self.total_amount_in_words = self.total_amount_in_words.replace(" And ", " ")
        self.total_amount_in_words = self.total_amount_in_words.replace(" and ", " ")
        self.amount_in_words_arabic = self.currency_id.with_context(lang='ar_001').amount_to_text(
            self.amount_total) if self.currency_id else False
        self.total_amount_in_words = self.total_amount_in_words + " Only"
        self.amount_in_words_arabic = 'فقط ' + str(self.amount_in_words_arabic) + ' ' + str(
            self.currency_id.subucurrency_symbol)

    @api.onchange('taxes_id')
    def _onchange_taxes_id(self):
        for rec in self:
            for line in rec.order_line:
                if not rec.taxes_id:
                    line.tax_id = False
                else:
                    line.tax_id = self.taxes_id.ids


    # address delivery fields
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', )
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    def _create_invoices(self, grouped=False, final=False, date=None):
        rec = super(SaleOrder, self)._create_invoices(grouped, final, date)
        self.write({'state': 'to_confirm'})
        return rec

    # @api.constrains('order_line', 'order_line.product_uom_qty')
    # def _check_product_uom_qty(self):
    #     for line in self.order_line:
    #         if line.product_id.type == 'product':
    #             qty = line.product_uom_qty
    #             if qty > line.product_id.virtual_available:
    #                 raise ValidationError(_('Not enough inventory! \n'
    #                                         'You plan to sell %s but you only have %s %s available' % (
    #                                             qty, line.product_id.virtual_available,
    #                                             line.product_id.name,)))

    @api.onchange('partner_id')
    def onchange_partner_id_address(self):
        for rec in self:
            rec.street = rec.partner_id.street
            rec.street2 = rec.partner_id.street2
            rec.city = rec.partner_id.city
            rec.state_id = rec.partner_id.state_id.id
            rec.country_id = rec.partner_id.country_id.id

    def action_submit(self):
        self.ensure_one()
        for line in self.order_line:
            if line.product_id.type == 'product':
                qty = line.product_uom_qty
                if qty > line.product_id.virtual_available:
                    raise ValidationError(_('Not enough inventory! \n'
                                            'You plan to sell %s but you only have %s %s available' % (
                                                qty, line.product_id.virtual_available,
                                                line.product_id.name,)))

        if not self.order_line:
            raise UserError(_('You can not submit the order without fill order lines'))
        if not self.approve_line_ids and not self.invoice_type == 'wholesale':
            self.state = 'submit'
        elif not self.approve_line_ids and self.invoice_type == 'wholesale' or self.type == 'deferred':
            self.state = 'gm_assistant'
        else:
            for line in self.approve_line_ids:
                if self.env.user.id in line.group_id.users.ids:
                    self.write({'state': 'submit'})
                else:
                    self.write({'state': 'wait_dis_approve', 'level_discount_approval': line.level_approve})

    def action_gm_assistant_approve(self):
        self.write({'state': 'approved'})

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'draft').with_context(tracking_disable=True).write({'state': 'submit'})
        return super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def create_picking(self):
        self.order_line._action_launch_stock_rule()

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'department_id': self.department_id.id,
                             'sale_id': self.id, })
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[]")


    department_id = fields.Many2one('hr.department', string='Department',
                                    related='order_id.department_id', )

    team_id = fields.Many2one(comodel_name="crm.team", string="Sales Team", required=False,
                              related='order_id.team_id')
    warehouse_id = fields.Many2one('stock.warehouse', related='order_id.warehouse_id', readonly=False, store=True)

    def _check_line_unlink(self):
        """
        Check wether a line can be deleted or not.

        Lines cannot be deleted if the order is confirmed; downpayment
        lines who have not yet been invoiced bypass that exception.
        :rtype: recordset sale.order.line
        :returns: set of lines that cannot be deleted
        """
        return self.filtered(
            lambda line: line.state in ('submit', 'to_confirm', 'sale', 'done',) and (
                    line.invoice_lines or not line.is_downpayment))

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status(self):
        """OverWrite"""
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('submit', 'to_confirm', 'sale', 'done',):
                line.invoice_status = 'no'
            elif line.is_downpayment and line.untaxed_amount_to_invoice == 0:
                line.invoice_status = 'invoiced'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and \
                    float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
                line.invoice_status = 'upselling'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

    # @api.onchange('team_id')
    # def on_change_team_ids(self):
    #     warehouse_ids = []
    #     self.warehouse_id = self.team_id.warehouse_id.id
    #     for record in self.team_id:
    #         for warehouse in record.allow_warehouse_ids:
    #             warehouse_ids.append(warehouse.id)
    #         if record.warehouse_id.id:
    #             warehouse_ids.append(record.warehouse_id.id)
    #
    #     return {'domain': {'warehouse_id': [('id', 'in', warehouse_ids or [])]}}

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        if self.order_id.type == 'direct' and not self.order_id.invoice_ids:
            # raise UserError(_('You can not create delivery before invoice is genrated since sale type is Direct sale..'))
            return
        else:
            res = super(SaleOrderLine, self)._action_launch_stock_rule()
            return res

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['submit', 'approved', 'sale', 'done']:

                if not line.qty_delivered:
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('state', 'price_reduce', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered', 'product_uom_qty')
    def _compute_untaxed_amount_to_invoice(self):
        """ Total of remaining amount to invoice on the sale order line (taxes excl.) as
                total_sol - amount already invoiced
            where Total_sol depends on the invoice policy of the product.

            Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
            come only from the SO lines.
        """
        for line in self:
            amount_to_invoice = 0.0
            if line.state in ['sale', 'done']:
                # Note: do not use price_subtotal field as it returns zero when the ordered quantity is
                # zero. It causes problem for expense line (e.i.: ordered qty = 0, deli qty = 4,
                # price_unit = 20 ; subtotal is zero), but when you can invoice the line, you see an
                # amount and not zero. Since we compute untaxed amount, we can use directly the price
                # reduce (to include discount) without using `compute_all()` method on taxes.
                price_subtotal = 0.0
                umo_qty_to_consider = line.qty_delivered if line.order_id.invoicing_policy == 'order' else line.product_uom_qty
                price_subtotal = line.price_reduce * umo_qty_to_consider
                if len(line.tax_id.filtered(lambda tax: tax.price_include)) > 0:
                    # As included taxes are not excluded from the computed subtotal, `compute_all()` method
                    # has to be called to retrieve the subtotal without them.
                    # `price_reduce_taxexcl` cannot be used as it is computed from `price_subtotal` field. (see upper Note)
                    price_subtotal = line.tax_id.compute_all(
                        line.price_reduce,
                        currency=line.order_id.currency_id,
                        quantity=umo_qty_to_consider,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id)['total_excluded']

                if any(line.invoice_lines.mapped(lambda l: l.discount != line.discount)):
                    # In case of re-invoicing with different discount we try to calculate manually the
                    # remaining amount to invoice
                    amount = 0
                    for l in line.invoice_lines:
                        if len(l.tax_ids.filtered(lambda tax: tax.price_include)) > 0:
                            amount += l.tax_ids.compute_all(
                                l.currency_id._convert(l.price_unit, line.currency_id, line.company_id,
                                                       l.date or fields.Date.today(), round=False) * l.quantity)[
                                'total_excluded']
                        else:
                            amount += l.currency_id._convert(l.price_unit, line.currency_id, line.company_id,
                                                             l.date or fields.Date.today(), round=False) * l.quantity

                    amount_to_invoice = max(price_subtotal - amount, 0)
                else:
                    amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced

            line.untaxed_amount_to_invoice = amount_to_invoice

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({
            'department_id': self.order_id.department_id.id})
        return values

