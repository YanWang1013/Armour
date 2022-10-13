from django.conf.urls import url
from .views import ArmourLoginView, ArmourLogoutView, PasswordChangeView, RegisterView, AskLogoutView, ResetPassView, \
    ResetPassInfoView, ResetPassConfirmView, ResetPassConfirmInfoView, AcivateAccountView, ConfirmInfoView
from django.conf import settings

urlpatterns = [
    url(r'^login/$', ArmourLoginView.as_view(), {}, 'login'),
    url(r'^logout/$', ArmourLogoutView.as_view(), {}, 'logout'),
    url(r'^logout/confirmation/$', AskLogoutView.as_view(), {}, 'logout-ask'),
    url(r'^password/change/$', PasswordChangeView.as_view(), {}, 'change-password'),
    url(r'^password/reset/$', ResetPassView.as_view(), {}, 'reset-password'),
    url(r'^password/reset/info/$', ResetPassInfoView.as_view(), {}, 'reset-password-info'),
    url(r'^password/reset/change/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ResetPassConfirmView.as_view(), {}, 'reset-password-change'),
    url(r'^password/reset/confirm/$', ResetPassConfirmInfoView.as_view(), {}, 'reset-password-confirm'),
    url(r'^activate/(?P<uuid>[0-9A-Fa-f-]+)/$', AcivateAccountView.as_view(), {}, 'activate-account'),
    url(r'^activate/email/confirmation/$', ConfirmInfoView.as_view(), {}, 'activate-email-conf'),
]

if settings.REGISTARTION_VIEW:
    urlpatterns.append(url(r'^register/$', RegisterView.as_view(), {}, 'register'), )
