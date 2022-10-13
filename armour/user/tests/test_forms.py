from django.test import TestCase
from django.test.client import RequestFactory

from armour.user.forms import *
from armour.legislation.tests.helpers import *

from mixer.backend.django import mixer


class LoginFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = LoginForm(request=cls.request)

    def test_form_fields_present(self):
        fields = ['username', 'password']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class MyUserChangeFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = MyUserChangeForm()

    def test_form_fields_present(self):
        fields = ['username', 'password', 'date_joined', 'user_permissions', 'is_company_owner', 'is_staff', 'groups', 'last_name', 'company',
                  'is_superuser', 'last_login', 'is_active', 'phone_number', 'is_company_admin', 'first_name', 'email', 'activate_lnk', 'terms', 'country']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class MyUserCreationFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = MyUserCreationForm()

    def test_form_fields_present(self):
        fields = ["email", "password1", "password2"]
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class MyUserMixinFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = MyUserMixinForm()

    def test_form_fields_present(self):
        fields = ['password1', 'password2', 'password', 'date_joined', 'is_company_owner', 'is_staff','last_name',
                  'company','is_superuser', 'last_login', 'is_active', 'phone_number', 'is_company_admin', 'first_name',
                  'email', 'activate_lnk', 'terms', 'country']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class ChangePasswordFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = ChangePasswordForm()

    def test_form_fields_present(self):
        fields = ['new_password1', 'new_password2']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class RegisterCompanyFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = RegisterCompanyForm(request=cls.request)

    def test_form_fields_present(self):
        fields = ['name', 'street', 'zipcode', 'city', 'email', 'usemail', 'website', 'country', 'topics', 'locations',
                  'currency', 'last_name', 'password1', 'captcha', 'first_name', 'password2', 'image']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())
