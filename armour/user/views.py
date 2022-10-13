# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import FormView, CreateView

from .forms import LoginForm, ChangePasswordForm, PassResetForm, PassResetSetPasswordForm, RegisterUserForm
from .models import User
from ..general.mixins import AnonymousMixin


class ArmourLoginView(AnonymousMixin, LoginView):
    template_name = 'user/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        url = super().get_success_url()

        if self.request.POST.get('next', None):
            return self.request.POST.get('next')
        return url


class ArmourLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'user/logout.html'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        from loginas.utils import restore_original_login
        restore_original_login(request)
        return HttpResponseRedirect(reverse_lazy('login'))


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'user/change-password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('organization-update')

    def form_valid(self, form):
        password = form.cleaned_data['new_password1']
        self.request.user.set_password(password)
        self.request.user.save()
        update_session_auth_hash(self.request, self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class RegisterView(AnonymousMixin, CreateView):
    template_name = 'user/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy("activate-email-conf")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class AskLogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'user/logout_ask.html'


class ResetPassView(AnonymousMixin, PasswordResetView):
    form_class = PassResetForm
    template_name = 'user/password-reset.html'
    subject_template_name = 'email/password_reset_subject.txt'
    email_template_name = 'email/password_reset_email.html'
    success_url = reverse_lazy('reset-password-info')


class ResetPassInfoView(AnonymousMixin, TemplateView):
    template_name = 'user/password-reset-sent.html'


class ResetPassConfirmView(AnonymousMixin, PasswordResetConfirmView):
    template_name = 'user/reset-password-change.html'
    success_url = reverse_lazy('reset-password-confirm')
    form_class = PassResetSetPasswordForm


class ResetPassConfirmInfoView(AnonymousMixin, TemplateView):
    template_name = 'user/password-reset-confirm.html'


class ConfirmInfoView(AnonymousMixin, TemplateView):
    template_name = 'user/activation-confirmation.html'


class AcivateAccountView(AnonymousMixin, RedirectView):
    pattern_name = 'login'

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, uuid=kwargs.get('uuid'), activate_lnk=False, )
        user.is_active = True
        user.activate_lnk = True
        user.save()

        messages.add_message(self.request, messages.SUCCESS, 'Account has been activated', )

        return HttpResponseRedirect(reverse_lazy(self.pattern_name))
