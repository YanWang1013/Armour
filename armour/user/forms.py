# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm, PasswordResetForm, \
    SetPasswordForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UsernameField
from captcha.fields import ReCaptchaField
from ..company.models import Company
from ..legislation.models import Location, Topic
from django.contrib.auth import login, authenticate
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.sites.models import Site

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = UsernameField(
        max_length=254, required=True,
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )

    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = _("Username")
        self.fields['username'].label = ''
        self.fields['username'].widget.attrs['class'] = "form-control"
        self.fields['password'].label = ''
        self.fields['password'].widget = forms.PasswordInput(
            attrs={'placeholder': _("Password"), 'autocomplete': 'off', 'data-toggle': 'password',
                   'class': "form-control"})


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2",)


class MyUserMixinForm(UserCreationForm, UserChangeForm):
    addfields = ['password1', 'password2', 'username', 'email', 'phone_number', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(MyUserMixinForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)

        if instance:
            self.fields['password1'].required = False
            self.fields['password1'].widget = forms.HiddenInput()

            self.fields['password2'].required = False
            self.fields['password2'].widget = forms.HiddenInput()

            self.fields['password'].help_text = "Raw passwords are not stored, so there is no way to see this user's " \
                                                "password, but you can change the password using <a " \
                                                "href='/admin/user/user/%s/password/' target='__blank'>this " \
                                                "form</a>." % instance.id

        else:
            for f in self.fields:
                if f not in self.addfields:
                    self.fields[f].required = False
                    self.fields[f].widget = forms.HiddenInput()

    class Meta:
        model = User
        exclude = ('groups', 'user_permissions', 'username')


class ChangePasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        required=True,
        min_length=6,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
        required=True,
        min_length=6,
    )

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['class'] = "form-control form-control-lg icon-right"
        self.fields['new_password2'].widget.attrs['class'] = "form-control form-control-lg icon-right"

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))

        return password2


class RegisterUserForm(forms.ModelForm):
    captcha = ReCaptchaField()
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, strip=False, required=True,
                                min_length=9)
    password2 = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput, strip=False, required=True,
                                min_length=9)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.logusser = None

        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = "form-control"
        self.fields['first_name'].widget.attrs['class'] = "form-control"
        self.fields['last_name'].widget.attrs['class'] = "form-control"
        self.fields['password1'].widget.attrs['class'] = "form-control"
        self.fields['password2'].widget.attrs['class'] = "form-control"
        self.fields['country'].widget.attrs['class'] = "form-control"
        self.fields['terms'].widget.attrs['class'] = "form-check-input"
        self.fields['terms'].required = True

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))

        return password2

    def save(self, commit=True, *args, **kwargs):
        obj = super(RegisterUserForm, self).save(commit=False)
        obj.is_company_owner = True
        obj.is_company_admin = True
        obj.is_active = False
        obj.save()
        self.save_m2m()
        data = self.cleaned_data

        obj.set_password(data['password1'])
        obj.save()

        current_site = Site.objects.get_current()
        protocol = settings.IS_HTTPS and "https://" or "http://"
        baseurl = protocol + current_site.domain

        ctx = {'user': obj, 'baseurl': baseurl}
        content = render_to_string("email/register-confirmation.html", ctx, request=self.request)

        mail = EmailMessage(subject="Activation email", body=content,
                            from_email=settings.DEFAULT_FROM_EMAIL, to=[data['email']])
        mail.content_subtype = 'html'
        mail.send()

        messages.add_message(self.request, messages.SUCCESS,
                             'An activation link has been sent to the email address provided', )

        # self.logusser = authenticate(self.request, username=data['email'], password=data['password1'])
        # login(self.request, self.logusser)
        return obj

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'captcha', 'password1', 'password2', 'terms', 'email', 'country')


class RegisterCompanyForm(forms.ModelForm):
    captcha = ReCaptchaField()
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, strip=False, required=True,
                                min_length=6)
    password2 = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput, strip=False, required=True,
                                min_length=6)
    first_name = forms.CharField(label=_("First name"), required=True, )
    last_name = forms.CharField(label=_("Last name"), required=True, )
    usemail = forms.CharField(label=_("Email"), required=True, )

    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.filter(published=True),
                                            widget=forms.CheckboxSelectMultiple(),
                                            required=True)
    locations = forms.ModelMultipleChoiceField(queryset=Location.objects.filter(published=True),
                                               widget=forms.CheckboxSelectMultiple(),
                                               required=True)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.logusser = None

        super(RegisterCompanyForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = "form-control"
        self.fields['first_name'].widget.attrs['class'] = "form-control"
        self.fields['last_name'].widget.attrs['class'] = "form-control"
        self.fields['password1'].widget.attrs['class'] = "form-control"
        self.fields['password2'].widget.attrs['class'] = "form-control"
        self.fields['name'].widget.attrs['class'] = "form-control"
        self.fields['street'].widget.attrs['class'] = "form-control"
        self.fields['zipcode'].widget.attrs['class'] = "form-control"
        self.fields['city'].widget.attrs['class'] = "form-control"
        self.fields['country'].widget.attrs['class'] = "form-control"
        self.fields['website'].widget.attrs['class'] = "form-control"
        self.fields['usemail'].widget.attrs['class'] = "form-control"
        self.fields['currency'].widget.attrs['class'] = "form-control"
        self.fields['currency'].required = True

    def clean_usemail(self):
        usemail = self.cleaned_data.get('usemail')

        if User.objects.filter(email=usemail).count() > 0:
            raise forms.ValidationError(_("You can not use this email, use another one."))

        return usemail

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))

        return password2

    def save(self, commit=True, *args, **kwargs):
        obj = super(RegisterCompanyForm, self).save(commit=False)
        obj.save()
        self.save_m2m()
        data = self.cleaned_data
        us = User(company=obj, email=data['usemail'], first_name=data['first_name'], last_name=data['last_name'],
                  is_company_admin=True)
        us.save()
        us.set_password(data['password1'])
        us.is_company_owner = True
        us.is_company_admin = True
        us.save()

        self.logusser = authenticate(self.request, username=data['usemail'], password=data['password1'])
        login(self.request, self.logusser)
        return obj

    class Meta:
        model = Company
        fields = ('name', 'street', 'zipcode', 'city', 'email', 'usemail', 'website', 'country', 'topics', 'locations',
                  'currency', 'image',)


class PassResetForm(PasswordResetForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(PassResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = "form-control"


class PassResetSetPasswordForm(SetPasswordForm):
    def __init__(self, request=None, *args, **kwargs):
        super(PassResetSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['class'] = "form-control form-control-lg icon-right"
        self.fields['new_password2'].widget.attrs['class'] = "form-control form-control-lg icon-right"
