from django.urls import re_path, path, include

from . import views


urlpatterns = [
	path('payments/get-address/', views.GetAddressView.as_view(), name='payments>get-address'),
]