# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from datetime import timedelta, datetime


class PartnerStatementWizard(models.TransientModel):
    _name = 'partner.statement.wizard'

    date_start = fields.Date(
        default=lambda self: self.get_last_week(),)
    date_end = fields.Date(
        default=fields.Date.today,)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency"
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        default=lambda self: self.env.user.company_id,
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string="Partners")
    type_report = fields.Selection(
        string='Statement Type',
        selection="get_types",)

    @api.model
    def get_types(self):
        selection_types = []
        if 'active_ids' in self._context:
            active_model = self.env.context['active_model']
            for partner in self.env[active_model].search(
                    [('id', 'in', self._context['active_ids'])]):
                if partner.customer:
                    selection_types.append(('out_invoice', _('Customer')))
                if partner.supplier:
                    selection_types.append(('in_invoice', _('Supplier')))
            selection_types = list(set(selection_types))
        return selection_types

    @api.model
    def default_get(self, fields):
        res = super(PartnerStatementWizard, self).default_get(fields)
        types = self.get_types()
        if len(types) == 1:
            res['type_report'] = types[0][0]
        return res

    @api.model
    def get_last_week(self):
        return fields.Date.from_string(fields.Date.today()) - timedelta(days=7)

    @api.multi
    def get_invoices(self, partner):
        start_period = self.date_start + " 00:00:01"
        end_period = self.date_end + " 23:59:59"
        if self.type_report == 'out_invoice':
            types = ['out_invoice', 'out_refund']
        else:
            types = ['in_invoice', 'in_refund']
        invoices = self.env['account.invoice'].search([
                ('partner_id', '=', partner),
                ('date_invoice', '>=', start_period),
                ('date_invoice', '<=', end_period),
                ('currency_id', '=', self.currency_id.id),
                ('type', 'in', types),
                ('state', 'in', ['open', 'paid'])], order="date_invoice, id")
        return invoices

    @api.multi
    def _get_amount(self, importe):
        minus = False
        amount = "%.2f" % float(importe)
        if '-' in amount:
            amount = amount.replace('-', '')
            minus = True
        i = amount.index('.')
        while i > 3:
            i = i - 3
            amount = amount[:i] + ',' + amount[i:]
        if minus:
            amount = '-' + amount
        return amount

    @api.multi
    def print_report(self):
        self.ensure_one()
        for partner in self.partner_ids:
            sales = self.get_invoices(partner.id)
        if not sales:
            raise ValidationError(
                _("No results with requested information \n"
                  "Please check!"))
        self.sent = True
        return self.env['report'].get_action(
            self,
            'carbotecnia_partner_statement.partner_statement_report_template'
        )

    @api.model
    def items(self, line, totals, type_doc):
        items = {}
        if type_doc in [_('Invoice'), _('Refund')]:
            if type_doc == _('Refund'):
                totals['refunds_total'] += line.amount_total
                totals['refunds_subtotal'] += line.amount_untaxed
                totals['balance'] -= line.amount_total
                items['sales'] = 0.0
                items['payment'] = line.amount_total
            if type_doc == _('Invoice'):
                totals['invoices_total'] += line.amount_total
                totals['invoices_subtotal'] += line.amount_untaxed
                totals['balance'] += line.amount_total
                items['sales'] = line.amount_total
                items['payment'] = 0.0
            ref = (line.reference
                   if self.type_report == 'in_invoice'
                   else line.origin)
            items['document'] = type_doc
            items['number'] = line.number
            items['ref'] = ref
            items['date_exp'] = line.date_invoice
            items['date_ven'] = line.date_due
            items['total'] = totals['balance']
        elif type_doc == _('Payment'):
            if line.journal_id.type in ['bank', 'cash']:
                if line.currency_id and line.currency_id == self.currency_id:
                    amount = abs(line.amount_currency)
                else:
                    amount = line.credit if line.credit > 0.0 else line.debit
                totals['balance'] -= amount
                items['document'] = type_doc
                items['number'] = line.name
                items['ref'] = line.move_id.name
                items['date_exp'] = line.date
                items['date_ven'] = line.date_maturity
                items['sales'] = 0.0
                items['payment'] = amount
                items['total'] = totals['balance']
        else:
            items = False
        return items, totals

    @api.model
    def convert_date(self, date):
        date_str = datetime.strptime(
            date, '%Y-%m-%d').date().strftime("%d/%m/%Y")
        return date_str

    @api.model
    def _get_lines_print(self, partner):
        for rec in self:
            invoices = self.get_invoices(partner.id)
            lines = [[], []]
            totals = {
                'invoices_total': 0.0,
                'refunds_subtotal': 0.0,
                'invoices_subtotal': 0.0,
                'refunds_total': 0.0,
                'sales_total': 0.0,
                'balance': 0.0
            }
            for invoice in invoices:
                if invoice.type in ['out_refund', 'in_refund']:
                    items, totals = self.items(
                        invoice, totals, _('Refund'))
                else:
                    items, totals = self.items(
                        invoice, totals, _('Invoice'))
                lines[0].append(items)
                for payment in invoice.payment_move_line_ids:
                    items, totals = self.items(
                        payment, totals, _('Payment'))
                    lines[0].append(items)
            payment_type = (
                'inbound' if self.type_report == 'out_invoice'
                else 'outbound')
            payments = self.env['account.payment'].search([
                ('invoice_ids', '=', False),
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted'),
                ('payment_type', '=', payment_type)
            ])
            if payments:
                for payment in payments:
                    totals['balance'] -= payment.amount
                    lines[0].append({
                        'document': _('Payment'),
                        'number': payment.name,
                        'ref': '',
                        'date_exp': payment.payment_date,
                        'date_ven': payment.payment_date,
                        'sales': 0.0,
                        'payment': payment.amount,
                        'total': totals['balance'],
                    })
            totals['sales_total'] = (
                totals['invoices_subtotal'] - totals['refunds_subtotal'])
            lines[1] = totals
        return lines
