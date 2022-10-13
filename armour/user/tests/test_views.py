from django.test import TestCase, RequestFactory
from django.urls import reverse

from armour.legislation.tests.helpers import *


class PasswordChangeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.change_pass = reverse('change-password')
        cls.client = RequestFactory()
        cls.user = create_user()

    def test_login_required_mixin(self):
        response = self.client.get(self.change_pass, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.change_pass)
        self.assertRedirects(response, redirect_url)


# class RegisterViewtest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.register = reverse('register')
#         cls.client = RequestFactory()
#         cls.user = create_user()
#
#     def test_anonymous_mixin(self):
#         self.client.force_login(user=self.user)
#         response = self.client.get(self.register, follow=True)
#         redirect_url = '{}'.format(reverse(settings.LOGIN_URL))
#         self.assertRedirects(response, redirect_url)


class AskLogoutViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ask_logout = reverse('logout-ask')
        cls.client = RequestFactory()
        cls.user = create_user()

    def test_login_required_mixin(self):
        response = self.client.get(self.ask_logout, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.ask_logout)
        self.assertRedirects(response, redirect_url)


# class ResetPassViewTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.reset = reverse('reset-password')
#         cls.client = RequestFactory()
#         cls.user = create_user()
#
#     def test_anonymous_mixin(self):
#         response = self.client.get(self.reset, follow=True)
#         redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.reset)
#         self.assertRedirects(response, redirect_url)


