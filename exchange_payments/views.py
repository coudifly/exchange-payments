import importlib
from decimal import Decimal

from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django_otp import user_has_device
from account.decorators import login_required
from jsonview.decorators import json_view
from simplecrypt import encrypt, decrypt

from exchange_core.models import Currencies, Accounts, Statement, BankWithdraw, CryptoWithdraw
from exchange_core.base_views import MultiFormView
from exchange_payments.models import CurrencyGateway, BankDeposits
from exchange_payments.gateways.coinpayments import Gateway
from exchange_payments.forms import NewDepositForm, ConfirmDepositForm, NewWithdrawForm
from templated_email import send_templated_mail


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
                address = gateway.get_address(account)

                # Associa a nova carteira a conta da moeda do usuário
                account.deposit_address = address
                account.save()

        return {'address': address}


@method_decorator([csrf_exempt, json_view], name='dispatch')
class ProcessWebhookView(View):
    def post(self, request, gateway, account_pk):
        # Importa dinamicamente o modulo do gateway configurado para a moeda
        gateway_module = importlib.import_module('exchange_payments.gateways.{}'.format(gateway))
        gateway = gateway_module.Gateway()
        account = Accounts.objects.get(pk=account_pk)

        # Checa se o deposito pode ser feito
        if gateway.can_deposit(account, request.POST):
            # Adiciona o saldo na conta do usuario, e cria a entrada no extrato
            with transaction.atomic():
                account.deposit += gateway.deposit_amount
                account.save()

                statement = Statement()
                statement.account = account
                statement.description = 'Deposit'
                statement.amount = gateway.deposit_amount
                statement.type = Statement.TYPES.deposit
                statement.save()
                
                return {'amount': statement.amount}

        return {'error': _("Deposit can't be done.")}


@method_decorator([login_required], name='dispatch')
class BankDepositView(MultiFormView):
    template_name = 'payments/bank-deposit.html'
    
    forms = {
        'new_deposit': NewDepositForm
    }

    pass_user = [
        'new_deposit'
    ]

    def get_view_data(self):
        data = {}
        data['deposit_fee_percent'] = '{}%'.format(round(settings.DEPOSIT_FEE * 100, 0))
        data['deposits'] = BankDeposits.objects.filter(user=self.request.user)
        data['today_deposits'] = BankDeposits.objects.filter(user=self.request.user, created__date=timezone.now())
        return data

    def new_deposit_form_valid(self, form):
        bank_deposit = form.save(commit=False)
        bank_deposit.user = self.request.user
        bank_deposit.range_amount = bank_deposit.amount

        # Se o range para depósitos BR estiver habilitado, gera o range_amount com o range
        if settings.BR_DEPOSIT_ENABLE_RANGE:
            bank_deposit.range_amount = BankDeposits.gen_range_amount(bank_deposit.amount)

        bank_deposit.save()

        messages.success(self.request, _("Your new deposit has been created"))
        return redirect(reverse('payments>bank-deposit'))


@method_decorator([login_required], name='dispatch')
class ConfirmDepositView(MultiFormView):
    template_name = 'payments/confirm-deposit.html'

    forms = {
        'confirm_deposit': ConfirmDepositForm
    }

    def get_confirm_deposit_instance(self):
        statuses = [BankDeposits.STATUS.pending, BankDeposits.STATUS.confirmed]
        return BankDeposits.objects.get(pk=self.kwargs['bank_deposit_pk'], user=self.request.user, status__in=statuses)

    def confirm_deposit_form_valid(self, form):
        bank_deposit = form.save(commit=False)
        bank_deposit.status = BankDeposits.STATUS.confirmed
        bank_deposit.save()
        
        messages.success(self.request, _("Your confirmation has been received"))
        return redirect(reverse('payments>bank-deposit'))


@method_decorator([login_required, json_view], name='dispatch')
class NewWithdrawView(View):
    def post(self, request):
        coin = request.POST['coin']
        # O POST e imutavel por default, sendo assim, 
        # precisamos alterar essa caracteristica do object para alterar seus valores
        request.POST._mutable = True

        # Define um valor padrao para o address caso o deposito seja em reais
        # Fazemos isto, pois esse campo precisa passar pela validacao do formulario
        if coin == settings.BRL_CURRENCY_SYMBOL:
            request.POST['address'] = 'whatever'
        # Define um valor padrao para code do two factor, caso o usuario nao tenha configurado ele ainda
        # Fazemos isto, pois esse campo precisa passar pela validacao do formulario
        if not user_has_device(request.user):
            request.POST['code'] = '123'

        withdraw_form = NewWithdrawForm(request.POST, user=request.user, coin=coin)

        if not withdraw_form.is_valid():
            return {'status': 'error', 'errors': withdraw_form.errors}

        with transaction.atomic():
            account = Accounts.objects.get(user=request.user, currency__symbol=coin)

            if coin == settings.BRL_CURRENCY_SYMBOL:
                withdraw = BankWithdraw()
            else:
                withdraw = CryptoWithdraw()

            fee = (withdraw_form.cleaned_data['amount'] * (account.currency.withdraw_fee / 100)) + account.currency.withdraw_fixed_fee

            withdraw.account = account
            withdraw.deposit = account.deposit
            withdraw.reserved = account.reserved
            withdraw.amount = Decimal('0.00') - withdraw_form.cleaned_data['amount']
            withdraw.fee = fee

            if coin == settings.BRL_CURRENCY_SYMBOL:
                br_bank_account = request.user.br_bank_account

                withdraw.bank = br_bank_account.bank
                withdraw.agency = br_bank_account.agency
                withdraw.account_type = br_bank_account.account_type
                withdraw.account_number = br_bank_account.account_number
            else:
                withdraw.address = withdraw_form.cleaned_data['address']

            withdraw.save()

            if coin != settings.BRL_CURRENCY_SYMBOL:
                withdraw_hash = encrypt(settings.SECRET_KEY, str(withdraw.pk)).hex()
                approve_link = settings.DOMAIN + reverse('payments>approve-withdraw', kwargs={'withdraw_hash': withdraw_hash})

                # Envia o email de confirmacao do deposito
                send_templated_mail(
                    template_name='approve-withdraw', 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    context={'withdraw': withdraw, 'approve_link': approve_link}, 
                    recipient_list=settings.WITHDRAW_APPROVE_EMAILS
                )

            account.deposit -= abs(withdraw.amount)
            account.save()

            statement = Statement()
            statement.account = account
            statement.description = 'Withdraw'
            statement.type = Statement.TYPES.withdraw
            statement.amount = withdraw.amount
            statement.save()

            return {'status': 'success', 'amount': withdraw.amount}


# Automatizacao do saque em Criptomoeda
@method_decorator([json_view], name='dispatch')
class ApproveWithdrawView(View):
    def get(self, request, withdraw_hash):
        # Desencripta e pega o saque da crypto
        withdraw_pk = decrypt(settings.SECRET_KEY, bytes.fromhex(withdraw_hash))
        withdraw = CryptoWithdraw.objects.get(pk=withdraw_pk, status=CryptoWithdraw.STATUS.requested)

        # Pega o gateway de pagamento da Criptomoeda
        currency_gateway = CurrencyGateway.objects.get(currency=withdraw.account.currency)
        gateway_module = importlib.import_module('exchange_payments.gateways.{}'.format(currency_gateway.gateway))
        gateway = gateway_module.Gateway()

        # Chama o metodo de saque da criptomoeda passando o saque ao metodo
        tx_id = gateway.to_withdraw(withdraw)
        withdraw.tx_id = tx_id
        withdraw.status = CryptoWithdraw.STATUS.paid
        withdraw.save()

        return {'status': _("Success"), 'address': withdraw.address}
