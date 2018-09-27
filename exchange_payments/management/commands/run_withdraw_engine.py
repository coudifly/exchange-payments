import importlib
from django.db import transaction
from django.core.management.base import BaseCommand

from exchange_core.models import BankWithdraw
from exchange_payments.models import CurrencyGateway


class Command(BaseCommand):
    help = 'Do withdraws automatically if configure'

    def handle(self, *args, **options):
        while True:
            for withdraw in BankWithdraw.objects.filter(status=BankWithdraw.STATUS.requested):
                with transaction.atomic():
                    currency_gateway = CurrencyGateway.objects.get(currency=withdraw.account.currency)
                    gateway_module = importlib.import_module('exchange_payments.gateways.{}'.format(currency_gateway.gateway))
                    gateway = gateway_module.Gateway()

                    withdraw.status = BankWithdraw.STATUS.paid
                    withdraw.tx_id = gateway.to_withdraw(withdraw)
                    withdraw.save()
