from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from exchange_core.models import Accounts, Statement, Currencies
from exchange_payments.gateways.tcoin import rpc_proxy


class Command(BaseCommand):
	help = 'Confirm TCOIN deposits'

	def handle(self, *args, **options):
		txs = rpc_proxy._call('listtransactions')

		for tx in txs:
			with transaction.atomic():
				# Valida se o tipo e o valor da transacao atendedem os requisitos para deposito
				if tx['category'] != 'receive' or tx['amount'] <= 0:
					continue

				# Pega a conta TCOIN do usuario usando a carteira dele
				currency = Currencies.objects.get(symbol=settings.TCOIN_CURRENCY_SYMBOL)
				accounts = Accounts.objects.filter(currency=currency, deposit_address=tx['address'])

				# Se a conta para a carteira nao existir, vai para a proxima transacao
				if not accounts.exists():
					continue

				account = accounts.first()

				# Valida se a transacao ja foi processada
				statements = Statement.objects.get(account=account, tx_id=tx['txid'])
				if statements.exists():
					continue

				# Deposita o valor para o usuario
				statement = Statement()
				statement.account = account
				statement.amount = Decimal(tx['amount'])
				statement.description = 'Deposit'
				statement.type = Statement.TYPES.deposit
				statement.tx_id = tx['txid']
				statement.save()

				account.deposit += Decimal(tx['amount'])
				account.save()

				print('Pagando {} para a conta TCOIN do usuario {}'.format(tx['amount'], account.user.username))
