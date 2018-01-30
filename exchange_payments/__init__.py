from decimal import Decimal

from django.conf import settings
from prettyconf.configuration import Configuration

# Diz ao pretty conf o path do .env caso não existam variáveis de ambiente para a respectiva config
config = Configuration(starting_path=settings.BASE_DIR)

# Define o nome do modulo
PACKAGE_NAME = 'exchange_payments'

# Diz ao Django aonde está a configuração desse modulo
default_app_config = PACKAGE_NAME + '.apps.Config'

# Coin Payments configurações de autenticação
settings.COINPAYMENTS_PUBLIC_KEY = config('COINPAYMENTS_PUBLIC_KEY', default=None)
settings.COINPAYMENTS_PRIVATE_KEY = config('COINPAYMENTS_PRIVATE_KEY', default=None)

# Lista de gateways de pagamento suportados
settings.SUPPORTED_PAYMENT_GATEWAYS = [
	('coinpayments', 'CoinPayments')
]

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
settings.WITHDRAW_FEE = config('WITHDRAW_FEE', default=Decimal('0.005'), cast=Decimal)
settings.WITHDRAW_MIN_AMOUNT = config('WITHDRAW_MIN_AMOUNT', default=Decimal('0.001'), cast=Decimal)
settings.WITHDRAW_MAX_AMOUNT = config('WITHDRAW_MAX_AMOUNT', default=Decimal('1000000.00'), cast=Decimal)
settings.WITHDRAW_RECEIVE_HOURS = config('WITHDRAW_RECEIVE_HOURS', default=48, cast=int)