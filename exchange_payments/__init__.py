from decimal import Decimal

from django.conf import settings
from prettyconf.configuration import Configuration

# Diz ao pretty conf o path do .env caso não existam variáveis de ambiente para a respectiva config
config = Configuration(starting_path=settings.BASE_DIR)

# Define o nome do modulo
PACKAGE_NAME = 'exchange_payments'

# Diz ao Django aonde está a configuração desse modulo
default_app_config = PACKAGE_NAME + '.apps.Config'

# Coin Payments configurações
settings.COINPAYMENTS_PUBLIC_KEY = config('COINPAYMENTS_PUBLIC_KEY', default=None)
settings.COINPAYMENTS_PRIVATE_KEY = config('COINPAYMENTS_PRIVATE_KEY', default=None)
settings.COINPAYMENTS_DEPOSIT_WITH_FEE = config('COINPAYMENTS_DEPOSIT_WITH_FEE', default=True, cast=config.boolean)

# Tcoin configurações
settings.TCOIN_RPC_USERNAME = config('TCOIN_RPC_USERNAME', default=None)
settings.TCOIN_RPC_PASSWORD = config('TCOIN_RPC_PASSWORD', default=None)
settings.TCOIN_RPC_URL = config('TCOIN_RPC_URL', default=None)
settings.TCOIN_RPC_PROXY = config('TCOIN_RPC_PROXY', default=None)
settings.TCOIN_SUBTRACT_FEE_FROM_AMOUNT = config('TCOIN_SUBTRACT_FEE_FROM_AMOUNT', default=False, cast=config.boolean)
settings.TCOIN_CONFIRM_PAYMENTS_WAIT_SECONDS = config('TCOIN_CONFIRM_PAYMENTS_WAIT_SECONDS', default=5, cast=int)

# Bitgo configuracoes
settings.BITGO_SERVER_URL = config('BITGO_SERVER_URL', default=None)
settings.BITGO_ACCESS_TOKEN = config('BITGO_ACCESS_TOKEN', default=None)

# Lista de gateways de pagamento suportados
settings.SUPPORTED_PAYMENT_GATEWAYS = [
	('coinpayments', 'CoinPayments'),
	('tcoin', 'Tcoin'),
	('bitgo', 'BitGo'),
	('advcash', 'Advcash'),
]

# Configurações do Real Brasileiro
settings.BRL_CURRENCY_SYMBOL = config('BRL_CURRENCY_SYMBOL', default='BRL')
# Configuracoes da TCOIN
settings.TCOIN_CURRENCY_SYMBOL = config('TCOIN_CURRENCY_SYMBOL', default='TCN')

# Configurações de depósito
settings.DEPOSIT_FEE = config('DEPOSIT_FEE', default=Decimal('0.05'), cast=Decimal)
settings.BR_DEPOSIT_MIN = config('BR_DEPOSIT_MIN', default=Decimal('50.00'), cast=Decimal)
settings.BR_DEPOSIT_MAX = config('BR_DEPOSIT_MAX', default=Decimal('1000000.00'), cast=Decimal)
# O deposit range para a conta BRL é usado para identificar os depositos automaticamente
settings.BR_DEPOSIT_ENABLE_RANGE = config('BR_DEPOSIT_ENABLE_RANGE', default=False, cast=config.boolean)
settings.BR_DEPOSIT_RANGE_START = config('BR_DEPOSIT_RANGE_START', default=0, cast=int)
settings.BR_DEPOSIT_RANGE_END = config('BR_DEPOSIT_RANGE_END', default=5, cast=int)
settings.BR_DEPOSIT_DAILY_LIMIT = config('BR_DEPOSIT_DAILY_LIMIT', default=5, cast=int) # Limite de depositos permitidos por dia

# Configurações de saque
settings.WITHDRAW_APPROVE_EMAILS = config('WITHDRAW_APPROVE_EMAILS', cast=config.list)