from django.contrib import admin

from exchange_core.admin import BaseAdmin
from exchange_payments.models import CurrencyGateway, CompanyBanks, BankDeposits


@admin.register(CurrencyGateway)
class CurrencyGatewayAdmin(BaseAdmin):
    list_display = ('currency', 'code', 'gateway')

    def code(self, o):
        return o.currency.code


@admin.register(CompanyBanks)
class CompanyBanksAdmin(BaseAdmin):
    list_display = ('name', 'bank', 'agency', 'account_type', 'account_number', 'document', 'is_active')


@admin.register(BankDeposits)
class BankDepositsAdmin(BaseAdmin):
    list_display = ('company_bank', 'amount', 'range_amount', 'receipt', 'authentication_code')