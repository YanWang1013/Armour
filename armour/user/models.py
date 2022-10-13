# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser, UserManager
from phonenumber_field.modelfields import PhoneNumberField
from armour.company.models import Company
import uuid
from django_countries.fields import CountryField

class UserManager(UserManager):
    def _create_user(self, username=None, email=None, password=None, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=email, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(verbose_name=_(u'Username'), max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField(null=True,blank=True)
    email = models.EmailField(_('Email address'), blank=False, null=False, unique=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="companyusers")
    is_company_admin = models.BooleanField(_('Company admin'), default=False)
    is_company_owner = models.BooleanField(_('Company owner'), default=False)
    uuid = models.UUIDField(editable=False, null=True,blank=True)
    country = CountryField(_('Country'), null=True, blank=False)
    terms = models.BooleanField(_('By signing up you agree to our Terms & Conditions and Privacy Policy.'), default=False,)
    activate_lnk = models.BooleanField(_('Activate link'), default=False,)


    def get_fullname(self):
        return not self.first_name and self.username or self.get_full_name()

    def get_or_create_uuid(self):
        uid = self.uuid and self.uuid or str(uuid.uuid4())
        if not self.uuid:
            self.uuid = uid
            self.save()

        return uid

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
            self.save()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        db_table = 'auth_users'
        verbose_name = _(u'User')
        verbose_name_plural = _(u'Users')

