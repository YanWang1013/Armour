from django.urls import path

from .views import ContactView, PaneView, TMPView, TipsListView, TipDetailView, home_redirect

urlpatterns = [
    path('', home_redirect, name='home'),
    path('panel/', PaneView.as_view(), name='panel'),
    path('forms/contact/', ContactView.as_view(), name='contact-form'),
    path('templates/', TMPView.as_view(), name='tmp'),
    path('tips/', TipsListView.as_view(), name='tips-list'),
    path('tips/<int:pk>/', TipDetailView.as_view(), name='tip-details'),
]
