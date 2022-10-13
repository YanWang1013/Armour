from django.test import TestCase
from mixer.backend.django import mixer
from datetime import datetime
from armour.company.models import CompanyCC, Payments, PaymentsPositions, Employee
from armour.legislation.tests.helpers import *


class CompanyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company_1 = create_company()

    def test___str__(self):
        self.assertEqual(str(self.company_1), 'test name')

    def test_gen_price(self):
        self.assertEqual(self.company_1.gen_price(), 0)

    def test_gen_products(self):
        self.products = self.company_1.gen_products()
        self.assertEqual(len(self.products['locations']), 0)
        self.assertEqual(len(self.products['topics']), 0)
        self.assertEqual(len(self.products['questions']), 0)

    def test_check_valid_payment(self):
        self.assertFalse(self.company_1.check_valid_payment())

    def test_get_open_legislation(self):
        self.assertIsNone(self.company_1.get_open_isoproduct())


class CompanyCCTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = create_company()
        cls.company_cc = CompanyCC.objects.create(company=cls.company, cc4='TEST', stripe_id='test stripe', name='test name', surname='test surname', email='mail@example.com')

    def test___str__(self):
        self.assertEqual(str(self.company), 'test name')

    def test_foreign_keys(self):
        self.assertEqual(self.company_cc.company, self.company)


class PaymentsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = create_company()
        cls.payment = Payments.objects.create(company=cls.company, stripe_subs_id='test city', stripe_plan_id='another test city', price=1.9, validate=datetime.now())

    def test___str__(self):
        self.assertEqual(str(self.payment), str(self.payment.price))

    def test_foreign_keys(self):
        self.assertEqual(self.payment.company, self.company)


class PaymentsPositionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.payment = Payments.objects.create(company=create_company(), stripe_subs_id='test city', stripe_plan_id='another test city', price=1.9, validate=datetime.now())
        cls.payment_position = PaymentsPositions.objects.create(payment=cls.payment, price=2.2, location=mixer.blend('legislation.location'), topic=mixer.blend('legislation.topic'))

    def test___str__(self):
        self.assertEqual(str(self.payment), str(self.payment.price))

    def test_foreign_keys(self):
        self.assertEqual(self.payment_position.payment, self.payment)

    def test_get_questions(self):
        self.assertEqual(len(self.payment_position.get_questions()), 0)


class EmployeeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = create_company()
        cls.employee = Employee.objects.create(company=cls.company, fname = 'test first name', lname='test last name', email='test@test.com', position='test position', status='dead')

    def test___str__(self):
        self.assertEqual(str(self.employee), str("test first name test last name"))