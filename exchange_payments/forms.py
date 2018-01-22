from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings

from exchange_core.mixins import RequiredFieldsMixin
from exchange_core.choices import BR_BANKS_CHOICES
from exchange_payments.models import BankDeposits, CompanyBanks


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
