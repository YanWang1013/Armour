from django.test import TestCase
from django.test.client import RequestFactory

from armour.company.forms import *
from armour.legislation.tests.helpers import *


class BillingCompanyFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.form = BillingCompanyForm(request='POST')

    def test_form_fields_present(self):
        fields = ['name', 'billstreet', 'billzipcode', 'billcity', 'billcountry', 'card_num', 'year_expires',
                  'month_expires', 'card_code', 'fname', 'lname', 'email', 'card_token', 'currency']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class PaymentFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.request.session = dict()
        cls.form = PaymentForm(request=cls.request)

    def test_form_fields_present(self):
        fields = ('hidden_field',)
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class OrganizationCompanyFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = OrganizationCompanyForm(request=cls.request)

    def test_form_fields_present(self):
        fields = ['street', 'image', 'email', 'category', 'first_name', 'country', 'currency', 'name', 'city',
                  'zipcode', 'usemail', 'website', 'last_name', 'scope', 'req']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class EmployeeFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = EmployeeForm(request=cls.request)

    def test_form_fields_present(self):
        fields = ['fname', 'lname', 'email', 'position', 'status']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class AdminFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = AdminForm(request=cls.request)

    def test_form_fields_present(self):
        fields = ['first_name', 'last_name', 'email', 'password1', 'is_active']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class ProfileCompanyFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = ProfileCompanyForm(request=cls.request)

    def test_form_fields_present(self):
        fields = ['name', 'street', 'zipcode', 'city', 'email', 'usemail', 'website', 'country',  'currency',
                  'first_name', 'last_name', 'image']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())


class LegalFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.client = RequestFactory()
        cls.request = cls.client.get('')
        cls.request.user = cls.user
        cls.form = TopicForm(request=cls.request)

    def test_form_fields_present(self):
        fields = ['topics', 'locations']
        self.assertEqual(set(self.form.fields), set(fields))

    def test_form_invalid(self):
        self.assertFalse(self.form.is_valid())
