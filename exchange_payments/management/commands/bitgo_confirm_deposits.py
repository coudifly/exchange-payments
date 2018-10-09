import time
import gevent

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from exchange_core.models import Accounts, Statement
from exchange_payments.gateways.bitgo import Gateway


bitgo = Gateway()


def check_transaction(entry):
    with transaction.atomic():
        accounts = Accounts.objects.filter(deposit_address=entry['address'])

        if not accounts.exists():
            return

        account = accounts.first()
        print('Processando conta do usuario {}'.format(account.user.username))

        if Statement.objects.filter(account=account, tx_id=entry['id']).exists():
            return

        satoshis = Decimal(entry['value'])

        if satoshis < 0:
            return

        amount = satoshis / Decimal('100000000')
        account.deposit += amount
        account.save()

        statement = Statement()
        statement.account = account
        statement.tx_id = entry['id']
        statement.amount = amount
        statement.description = 'Deposit'
        statement.type = Statement.TYPES.deposit
        statement.save()

        print("Transfering {} to {} account".format(amount, account.pk))


MAXIMUM_STACK_SIZE = 30

class Command(BaseCommand):
    help = 'Confirm bitgo transfers'

    def handle(self, *args, **options):
        wallets = bitgo.get_wallets()

        while True:
            for wallet in wallets['wallets']:
                transactions = bitgo.get_transactions(wallet['id'])

                for transfer in transactions['transfers']:
                    gevent.wait([gevent.spawn(check_transaction, entry) for entry in transfer['entries']])

            time.sleep(30)
