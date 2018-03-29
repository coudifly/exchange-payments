import hmac
import hashlib
import requests

from decimal import Decimal
from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse


API_URL = 'https://www.coinpayments.net/api.php'
API_VERSION = 1
API_REQUEST_FORMAT = 'json'
API_PUBLIC_KEY = settings.COINPAYMENTS_PUBLIC_KEY
API_PRIVATE_KEY = settings.COINPAYMENTS_PRIVATE_KEY


def post(command, data={}, headers={}, **kwargs):
    data['cmd'] = command
    data['key'] = API_PUBLIC_KEY
    data['version'] = API_VERSION
    data['format'] = API_REQUEST_FORMAT

    encoded_data = urlencode(data)
    hmac_header = hmac.new(API_PRIVATE_KEY.encode('utf8'), encoded_data.encode('utf8'), hashlib.sha512).hexdigest()
    headers['hmac'] = hmac_header

    return requests.post(API_URL, data=data, headers=headers, **kwargs).json()


class Gateway:
    def create_transaction(self, buyer_email, amount, currency='BTC', currency1='BTC', currency2='BTC'):
        return post('create_transaction', data={
            'currency': currency,
            'currency1': currency1,
            'currency2': currency2,
            'buyer_email': buyer_email,
            'amount': amount
        })

    def get_transactions(self):
        return post('get_tx_ids')

    def get_transaction(self, transaction_id):
        return post('get_tx_info', data={'txid': transaction_id})

    def get_address(self, account):
        ipn_url = settings.DOMAIN + reverse('payments>proccess-webhook', kwargs={'gateway': 'coinpayments', 'account_pk': account.pk})
        address = post('get_callback_address', data={'currency': account.currency.symbol, 'ipn_url': ipn_url})
        return address['result']['address']

    def can_deposit(self, account, data):
        ipn_type = data['ipn_type']
        currency = data['currency']
        status = int(data['status'])
        amount = Decimal(data['amount'])
        fee = Decimal(data['fee'])

        # Checa se o deposito e valido
        if ipn_type == 'deposit' and account.currency.symbol.upper() == currency.upper() and status >= 100:
            # Verifica se e para descontar ou nao o valor do fee de 0.5% da coinpayments
            if not settings.COINPAYMENTS_DEPOSIT_WITH_FEE:
                fee = Decimal('0.00')

            self.deposit_amount = amount - fee
            return True

    def to_withdraw(self, withdraw):
        data = {
            'amount': withdraw.amount_with_discount,
            'currency': withdraw.account.currency.symbol,
            'address': withdraw.address
        }
        withdraw_response = post('create_withdrawal', data=data)
        return withdraw_response['result']['id']
