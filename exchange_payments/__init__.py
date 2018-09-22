from decimal import Decimal

from django.conf import settings
from prettyconf.configuration import Configuration

# Tells to prettyconf the env path to starting search the .env config file
config = Configuration(starting_path=settings.BASE_DIR)

# Define module name
PACKAGE_NAME = 'exchange_payments'

# Tells to Django where is the configuration of this package
default_app_config = PACKAGE_NAME + '.apps.Config'

# Coin Payments config
settings.COINPAYMENTS_PUBLIC_KEY = config('COINPAYMENTS_PUBLIC_KEY', default=None)
settings.COINPAYMENTS_PRIVATE_KEY = config('COINPAYMENTS_PRIVATE_KEY', default=None)
settings.COINPAYMENTS_DEPOSIT_WITH_FEE = config('COINPAYMENTS_DEPOSIT_WITH_FEE', default=True, cast=config.boolean)
settings.COINPAYMENTS_WITHDRAW_AUTO_CONFIRM = config('COINPAYMENTS_WITHDRAW_AUTO_CONFIRM', default='0')

# Bitcoinz config
settings.BITCOINZ_RPC_USERNAME = config('BITCOINZ_RPC_USERNAME', default=None)
settings.BITCOINZ_RPC_PASSWORD = config('BITCOINZ_RPC_PASSWORD', default=None)
settings.BITCOINZ_RPC_URL = config('BITCOINZ_RPC_URL', default=None)
settings.BITCOINZ_RPC_PROXY = config('BITCOINZ_RPC_PROXY', default=None)
settings.BITCOINZ_SUBTRACT_FEE_FROM_AMOUNT = config('BITCOINZ_SUBTRACT_FEE_FROM_AMOUNT', default=False,
                                                    cast=config.boolean)
settings.BITCOINZ_CONFIRM_PAYMENTS_WAIT_SECONDS = config('BITCOINZ_CONFIRM_PAYMENTS_WAIT_SECONDS', default=5, cast=int)

# Bitcoin config
settings.BITCOIN_RPC_USERNAME = config('BITCOIN_RPC_USERNAME', default=None)
settings.BITCOIN_RPC_PASSWORD = config('BITCOIN_RPC_PASSWORD', default=None)
settings.BITCOIN_RPC_URL = config('BITCOIN_RPC_URL', default=None)
settings.BITCOIN_RPC_PROXY = config('BITCOIN_RPC_PROXY', default=None)
settings.BITCOIN_SUBTRACT_FEE_FROM_AMOUNT = config('BITCOIN_SUBTRACT_FEE_FROM_AMOUNT', default=False,
                                                   cast=config.boolean)
settings.BITCOIN_CONFIRM_PAYMENTS_WAIT_SECONDS = config('BITCOIN_CONFIRM_PAYMENTS_WAIT_SECONDS', default=5, cast=int)

# Bitgo config
settings.BITGO_SERVER_URL = config('BITGO_SERVER_URL', default=None)
settings.BITGO_ACCESS_TOKEN = config('BITGO_ACCESS_TOKEN', default=None)

# Supported gateways list
settings.SUPPORTED_PAYMENT_GATEWAYS = [
    ('coinpayments', 'CoinPayments'),
    ('tcoin', 'Tcoin'),
    ('bitcoin', 'Bitcoin'),
    ('bitcoinz', 'Bitcoin Z'),
    ('bitgo', 'BitGo'),
]

# Currencies config
settings.BRL_CURRENCY_CODE = config('BRL_CURRENCY_CODE', default='BRL')
settings.TCOIN_CURRENCY_CODE = config('TCOIN_CURRENCY_CODE', default='TCN')
settings.BITCOINZ_CURRENCY_CODE = config('BITCOINZ_CURRENCY_CODE', default='BTCZ')
settings.BITCOIN_CURRENCY_CODE = config('BITCOIN_CURRENCY_CODE', default='BTC')

# Deposit config
settings.DEPOSIT_FEE = config('DEPOSIT_FEE', default=Decimal('0.05'), cast=Decimal)
settings.BR_DEPOSIT_MIN = config('BR_DEPOSIT_MIN', default=Decimal('50.00'), cast=Decimal)
settings.BR_DEPOSIT_MAX = config('BR_DEPOSIT_MAX', default=Decimal('1000000.00'), cast=Decimal)

# Deposit range for BRL accounts is used for automatically identify new deposits
settings.BR_DEPOSIT_ENABLE_RANGE = config('BR_DEPOSIT_ENABLE_RANGE', default=False, cast=config.boolean)
settings.BR_DEPOSIT_RANGE_START = config('BR_DEPOSIT_RANGE_START', default=0, cast=int)
settings.BR_DEPOSIT_RANGE_END = config('BR_DEPOSIT_RANGE_END', default=5, cast=int)
settings.BR_DEPOSIT_DAILY_LIMIT = config('BR_DEPOSIT_DAILY_LIMIT', default=5,
                                         cast=int)  # Daily deposits limit allowed per day

# Withdrawal config
settings.WITHDRAW_APPROVE_EMAILS = config('WITHDRAW_APPROVE_EMAILS', cast=config.list)

# Send withdraw confirmation to user
settings.WITHDRAW_USER_SEND_CONFIRMATION = config('WITHDRAW_USER_SEND_CONFIRMATION', cast=config.boolean, default=True)
