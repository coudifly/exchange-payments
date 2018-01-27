import importlib

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
from account.decorators import login_required
from jsonview.decorators import json_view

from exchange_core.models import Currencies, Accounts, Statement
from exchange_core.base_views import MultiFormView
from exchange_payments.models import CurrencyGateway, BankDeposits
from exchange_payments.gateways.coinpayments import Gateway
from exchange_payments.forms import NewDepositForm, ConfirmDepositForm


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