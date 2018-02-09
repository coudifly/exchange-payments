from decimal import Decimal

from bitcoin.rpc import Proxy
from django.conf import settings


RPC_USERNAME = settings.TCOIN_RPC_USERNAME
RPC_PASSWORD = settings.TCOIN_RPC_PASSWORD
RPC_URL = settings.TCOIN_RPC_URL
RPC_PROXY = settings.TCOIN_RPC_PROXY

rpc_proxy = Proxy(service_url=RPC_URL, rpc_username=RPC_USERNAME, rpc_password=RPC_PASSWORD, proxy=RPC_PROXY)


class Gateway:
    def create_transaction(self, buyer_email, amount, currency='BTC', currency1='BTC', currency2='BTC'):
        pass

    def get_transactions(self):
        pass

    def get_transaction(self, transaction_id):
        pass

    def get_address(self, account):
        return rpc_proxy.getnewaddress()

    def can_deposit(self, account, data):
        pass

    def to_withdraw(self, withdraw):
        satoshis_amount = 100000000 * abs(withdraw.amount)
        return rpc_proxy.sendtoaddress(withdraw.address, satoshis_amount, subtractfeefromamount=True)
