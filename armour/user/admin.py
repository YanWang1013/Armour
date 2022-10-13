# -*- coding: utf-8 -*-
from .models import User
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .forms import MyUserChangeForm, MyUserCreationForm


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'company',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'is_company_owner', 'is_company_admin'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    form = MyUserChangeForm
    add_form = MyUserCreationForm
    readonly_fields = ('date_joined', 'last_login',)
    list_display = ('email', 'first_name', 'last_name', 'company', 'is_active', 'is_superuser',)
    search_fields = ['email', 'first_name', 'last_name']
    change_form_template = 'loginas/change_form.html'

