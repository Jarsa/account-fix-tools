# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"

    filter_currencies = True

    @api.model
    def _get_options(self, previous_options=None):
        options = super()._get_options(previous_options=previous_options)
        options['currencies'] = self.env['res.currency'].search([]).read(['name'])
        return options

    @api.model
    def _init_filter_currencies(self, options, previous_options=None):
        if not self.filter_currencies:
            return
        selected_currency = previous_options and previous_options.get('selected_currency')
        if selected_currency and isinstance(selected_currency, int):
            options['selected_currency_name'] = self.env['res.currency'].browse(selected_currency).name
            options['selected_currency'] = selected_currency
        else:
            options['selected_currency'] = 'company_currency'
            options['selected_currency_name'] = _('Company currency')

    @api.model
    def _get_lines(self, options, line_id=None):
        context = self._context.copy()
        context['selected_currency'] = options.get('selected_currency')
        return super(ReportAccountAgedPartner, self.with_context(context))._get_lines(options, line_id)


class ReportAccountReportAgedPartnerBalance(models.AbstractModel):
    _inherit = 'report.account.report_agedpartnerbalance'

    def _get_partner_move_lines(self, account_type, date_from, target_move, period_length):
        res, total, lines = super()._get_partner_move_lines(
            account_type, date_from, target_move, period_length)  # noqa: E501
        selected_currency = self._context.get('selected_currency')
        if selected_currency and selected_currency == 'company_currency':
            return res, total, lines
        company_currency_id = self.env.user.company_id.currency_id.id
        company_currency = selected_currency == company_currency_id
        new_lines = {}
        import ipdb; ipdb.set_trace()
        for partner_id, values in lines.items():
            for value in values:
                line = value['line']
                if (line.currency_id.id == selected_currency):
                    new_lines.setdefault(partner_id, []).append({
                        'line': line,
                        'amount': line.amount_currency,
                        'period': value['period'],
                    })
                if not line.currency_id and company_currency:
                    new_lines.setdefault(partner_id, []).append({
                        'line': line,
                        'amount': line.balance,
                        'period': value['period'],
                    })
        return res, total, new_lines

    # @api.model
    # def _get_sql(self):
    #     res = super()._get_sql()
    #     options = self.env.context['report_options']
    #     selected_currency = options.get('selected_currency')
    #     if selected_currency and selected_currency != 'company_currency':
    #         res = res.replace(
    #             'COALESCE(company_currency.rate, 1) / COALESCE(used_currency.rate, 1)',
    #             'currency_table.rate'
    #         ).replace(
    #             "WHERE account.internal_type = 'payable'",
    #             "WHERE account.internal_type = 'payable' AND "
    #             "account_move_line.currency_id = %s" % selected_currency
    #         )
    #     return res
