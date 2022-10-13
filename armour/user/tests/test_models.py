from django.test import TestCase

from mixer.backend.django import Mixer

from armour.user.models import *

# from armour.legislation.tests.helpers import


class UserManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_manager = User.objects.create_user(username='user', email='mail@mail.com', password='testpas')
        cls.superuser_manager = User.objects.create_superuser(username='superuser', email='mail2@mail.com', password='testpass')

    def test_user_manager_instance(self):
        self.assertFalse(self.user_manager.is_superuser)

    def test_superuser_manager_instance(self):
        self.assertTrue(self.superuser_manager.is_superuser)




class Usertest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(email='mail@mail.com', )
        cls.owner = User.objects.create(email='mail2@mail.com', is_company_owner=True)
        cls.admin = User.objects.create(email='mail3@mail.com', is_company_admin=True)

    def test_is_superuser(self):
        self.assertFalse(self.user.is_company_owner)
        self.assertFalse(self.user.is_company_owner)
        self.assertFalse(self.owner.is_company_admin)
        self.assertTrue(self.owner.is_company_owner)
        self.assertTrue(self.admin.is_company_admin)
        self.assertFalse(self.admin.is_company_owner)