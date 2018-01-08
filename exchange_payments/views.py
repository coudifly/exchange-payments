import importlib

from django.views.generic import View
from django.utils.decorators import method_decorator
from account.decorators import login_required
from jsonview.decorators import json_view

from exchange_core.models import Currencies, Accounts
from exchange_payments.models import CurrencyGateway
from exchange_payments.gateways.coinpayments import Gateway


@method_decorator([login_required, json_view], name='dispatch')
class GetAddressView(View):
	def post(self, request):
		address = None
		coin = request.POST['coin']
		currencies = Currencies.objects.filter(symbol=coin)

		if currencies.exists():
			currency = currencies.first()
			account = Accounts.objects.get(user=request.user, currency=currency)

			if account.deposit_address:
				address = account.deposit_address
			else:
				# Importa dinamicamente o modulo do gateway configurado para a moeda
				currency_gateway = CurrencyGateway.objects.get(currency=currency)
				gateway_module = importlib.import_module('exchange_payments.gateways.{}'.format(currency_gateway.gateway))
				gateway = gateway_module.Gateway()
				address = gateway.get_address(currency.symbol)

				# Associa a nova carteira a conta da moeda do usuário
				account.deposit_address = address
				account.save()

		return {'address': address}
