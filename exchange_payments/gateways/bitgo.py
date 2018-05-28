from decimal import Decimal

import requests
from django.conf import settings


BITGO_SERVER_URL = settings.BITGO_SERVER_URL
BITGO_ACCESS_TOKEN = settings.BITGO_ACCESS_TOKEN

def create_request(request_type, path, data={}, **kwargs):
    headers = {'authorization': "Bearer " + BITGO_ACCESS_TOKEN}
    endpoint = '{}{}'.format(BITGO_SERVER_URL, path)
    return requests.request(request_type, endpoint, headers=headers, json=data, **kwargs).json()



class Gateway:
    def create_transaction(self, buyer_email, amount, currency='BTC', currency1='BTC', currency2='BTC'):
        pass

    def get_wallets(self):
        return create_request('GET', '/wallet')

    def get_transactions(self, wallet):
        return create_request('GET', '/wallet/{}/tx'.format(wallet))

    def get_transaction(self, transaction_id):
        pass

    def get_address(self, account):
        coin = account.currency.symbol.lower()
        wallets = create_request('GET', '/{}/wallet'.format(coin))
        path = '/{}/wallet/{}/address/0'.format(coin, wallets['wallets'][0]['id'])
        new_address = create_request('POST', path)
        return new_address['address']

    def can_deposit(self, account, data):
        pass

    def to_withdraw(self, withdraw):
        pass
