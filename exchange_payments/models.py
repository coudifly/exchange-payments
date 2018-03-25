import random
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from exchange_core.models import BaseModel
from model_utils.models import TimeStampedModel
from model_utils import Choices

from exchange_core.choices import BR_BANKS_CHOICES, BR_ACCOUNT_TYPES_CHOICES


"""
" O gateway serve para gerar as novas carteiras para a moeda X dentro do sistema,
" servindo também para o pagamento das solicitações de saque da mesma moeda X
"""

# Diz para o moeda X que gateway ela deverá usar
class CurrencyGateway(TimeStampedModel, BaseModel):
    currency = models.OneToOneField('exchange_core.Currencies', related_name='gateway', verbose_name=_("Currency"), on_delete=models.CASCADE)
    gateway = models.CharField(max_length=50, choices=settings.SUPPORTED_PAYMENT_GATEWAYS, verbose_name=_("Gateway"))

    def __str__(self):
        return self.currency.name

    class Meta:
        verbose_name = _("Currency gateway")
        verbose_name_plural = _("Currencies gateway")


# Armazena os bancos que serão usados para os depósitos feitos em REAL
class CompanyBanks(TimeStampedModel, BaseModel):
    bank = models.CharField(max_length=10, choices=BR_BANKS_CHOICES, verbose_name=_("Bank"))
    agency = models.CharField(max_length=10, verbose_name=_("Agency"))
    account_type = models.CharField(max_length=20, choices=BR_ACCOUNT_TYPES_CHOICES, verbose_name=_("Account type"))
    account_number = models.CharField(max_length=20, verbose_name=_("Account number"))
    title = models.CharField(max_length=100, verbose_name=_("Title"), null=True)
    name = models.CharField(max_length=100, verbose_name=_("Company Name"))
    document = models.CharField(max_length=20, verbose_name=_("CNPJ"))
    # Caso o banco entre em desuso, o registro não deverá ser apagado, mas sim inativado através da flag is_active
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    def __str__(self):
        return self.title or ''


    class Meta:
        verbose_name = _("Company bank")
        verbose_name_plural = _("Company banks")


class BankDeposits(TimeStampedModel, BaseModel):
    STATUS = Choices('pending', 'confirmed', 'deposited', 'expired')

    company_bank = models.ForeignKey(CompanyBanks, related_name='bank_deposits', on_delete=models.CASCADE, verbose_name=_("Company bank"))
    user = models.ForeignKey('exchange_core.Users', related_name='bank_deposits', on_delete=models.CASCADE, verbose_name=_("User"))
    # Valor original do depósito
    amount = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0.00'), verbose_name=_("R$ Amount"))
    # O range_amount varia de acordo com o RANGE, se o range estiver desabilitado, range_amount será igual a 0
    range_amount = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0.00'), verbose_name=_("Range amount"))
    # Armazena o valor liquido do depósito, que é o valor do amount - o valor da taxa de depósito
    credited_amount = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0.00'), verbose_name=_("Credited amount"))
    
    holder_bank = models.CharField(max_length=10, choices=BR_BANKS_CHOICES, verbose_name=_("Holder bank"), null=True, blank=True)
    holder_agency = models.CharField(max_length=10, verbose_name=_("Holder agency"), null=True, blank=True)
    holder_account_type = models.CharField(max_length=20, choices=BR_ACCOUNT_TYPES_CHOICES, verbose_name=_("Holder account type"), null=True, blank=True)
    holder_account_number = models.CharField(max_length=20, verbose_name=_("Holder account number"), null=True, blank=True)
    holder_name = models.CharField(max_length=100, verbose_name=_("Holder name"), null=True, blank=True)
    holder_document = models.CharField(max_length=20, verbose_name=_("Holder document CPF/CNPJ"), null=True, blank=True)

    receipt = models.ImageField(null=True, blank=True)
    authentication_code = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Authentication code"))

    status = models.CharField(max_length=20, verbose_name=_("Status"), default=STATUS.pending, choices=STATUS)

    class Meta:
        verbose_name = _("Bank deposit")
        verbose_name_plural = _("Bank deposits")

    @classmethod
    def gen_range_amount(cls, amount, tries=0):
        if tries > 100:
            raise Exception('Too many tries for charge amount generation')

        range_amount = round(amount + Decimal(random.uniform(settings.BR_DEPOSIT_RANGE_START, settings.BR_DEPOSIT_RANGE_END)), 2)
        bank_deposits_today = cls.objects.filter(created__date=timezone.now(), range_amount=range_amount)

        # Se existir um deposito do usuário com o mesmo
        if bank_deposits_today.exists():
            return cls.gen_range_amount(amount, tries)

        return range_amount

    @property
    def status_title(self):
        return self.status.title()

    # Propriedade para pegar a classe de alerta no template
    @property
    def status_type(self):
        if self.status == self.STATUS.pending:
            return 'danger'
        if self.status == self.STATUS.confirmed:
            return 'warning'
        if self.status == self.STATUS.deposited:
            return 'success'
        if self.status == self.STATUS.expired:
            return 'info'


class Credentials(TimeStampedModel, BaseModel):
    PROVIDERS = Choices(*[i[0] for i in settings.SUPPORTED_PAYMENT_GATEWAYS])

    provider = models.CharField(max_length=20, choices=PROVIDERS, verbose_name=_("Provider"))
    code = models.CharField(max_length=255, verbose_name=_("Your credential: email/code"))
    user = models.ForeignKey('exchange_core.Users', null=True, related_name='credentials', verbose_name=_("User"), on_delete=models.CASCADE)

    class Meta:
        unique_together = (('provider', 'user'),)
        verbose_name = _("Credential")
        verbose_name_plural = _("Credentials")
