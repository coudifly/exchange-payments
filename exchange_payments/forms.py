from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django_otp import user_has_device, match_token

from exchange_core.mixins import RequiredFieldsMixin
from exchange_core.choices import BR_BANKS_CHOICES
from exchange_core.models import Accounts
from exchange_payments.models import BankDeposits, CompanyBanks, Credentials


class NewDepositForm(forms.ModelForm):
    form_name = forms.CharField(widget=forms.HiddenInput(), initial='new_deposit')
    company_bank = forms.ModelChoiceField(queryset=CompanyBanks.objects.filter(is_active=True), empty_label=_("-- Select company bank --"))

    class Meta:
        model = BankDeposits
        fields = ('amount', 'company_bank',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)


    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount < settings.BR_DEPOSIT_MIN:
            raise forms.ValidationError(_("Min deposit is: ") + str(settings.BR_DEPOSIT_MIN))

        if amount > settings.BR_DEPOSIT_MAX:
            raise forms.ValidationError(_("Max deposit is: ") + str(settings.BR_DEPOSIT_MAX))

        if BankDeposits.objects.filter(user=self.user, created__date=timezone.now()).count() >= settings.BR_DEPOSIT_DAILY_LIMIT:
            raise forms.ValidationError(_("You've achieve the daily deposit limit of: ") + str(settings.BR_DEPOSIT_DAILY_LIMIT))

        return amount


class ConfirmDepositForm(RequiredFieldsMixin, forms.ModelForm):
    form_name = forms.CharField(widget=forms.HiddenInput(), initial='confirm_deposit')

    class Meta:
        model = BankDeposits
        fields = (
            'holder_bank',
            'holder_agency',
            'holder_account_type',
            'holder_account_number',
            'holder_name',
            'holder_document',
            'authentication_code',
            'receipt',
        )
        fields_required = (
            'holder_bank',
            'holder_agency',
            'holder_account_type',
            'holder_account_number',
            'holder_name',
            'holder_document',
            'authentication_code',
            'receipt',
        )


class NewWithdrawForm(forms.Form):
    amount = forms.DecimalField()
    address = forms.CharField()
    password = forms.CharField()
    code = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        account = self.account

        if amount < account.currency.withdraw_min:
            raise forms.ValidationError(_("Min withdraw is: ") + str(account.currency.withdraw_min))
        if amount > account.currency.withdraw_max:
            raise forms.ValidationError(_("Max withdraw is: ") + str(account.currency.withdraw_max))
        if amount > account.deposit:
            raise forms.ValidationError(_("You doesn't have enought balance"))
        
        return amount

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(_("Wrong password informed"))
        return password


    def clean_code(self):
        code = self.cleaned_data['code']
        if user_has_device(self.user) and not match_token(self.user, code):
            raise forms.ValidationError(_("Wrong two factor code informed"))
        return code


class CredentialForm(forms.ModelForm):
    password = forms.CharField(label=_("Your {} password").format(settings.PROJECT_NAME), widget=forms.PasswordInput())

    class Meta:
        model = Credentials
        fields = ('code', 'password',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(_("Wrong password informed"))
        return password