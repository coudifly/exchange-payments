from django.urls import re_path, path, include

from . import views

urlpatterns = [
    path('payments/get-address/', views.GetAddressView.as_view(), name='payments>get-address'),
    path('payments/bank-deposit/', views.BankDepositView.as_view(), name='payments>bank-deposit'),
    path('payments/new-withdraw/', views.NewWithdrawView.as_view(), name='payments>new-withdraw'),
    path('payments/approve-withdraw/<withdraw_hash>/', views.ApproveWithdrawView.as_view(),
         name='payments>approve-withdraw'),
    path('payments/confirm-deposit/<bank_deposit_pk>/', views.ConfirmDepositView.as_view(),
         name='payments>confirm-deposit'),
    path('payments/process-webhook/<gateway>/<account_pk>/', views.ProcessWebhookView.as_view(),
         name='payments>proccess-webhook')
]
