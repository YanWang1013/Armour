from django.test import TestCase, Client
from django.urls import reverse

from armour.legislation.tests.helpers import *


class CCUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cc_update = reverse('cc-update')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.cc_update, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.cc_update)
        self.assertRedirects(response, redirect_url)


class CCConfirmViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cc_confirm = reverse('cc-confirm')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.cc_confirm, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.cc_confirm)
        self.assertRedirects(response, redirect_url)

    def test_c_card_required_mixin(self):
        company = create_company()
        self.user.company = company
        self.client.force_login(user=self.user)
        response = self.client.post(self.cc_confirm, follow=True)
        redirect_url = '/company/credit-cart/update/'
        self.assertRedirects(response, redirect_url)


class CCSuccessViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.cc_success = reverse('cc-success', kwargs={'uuid': cls.user.pk})

    def test_login_required(self):
        response = self.client.get(self.cc_success, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.cc_success)
        self.assertRedirects(response, redirect_url)

    def test_c_card_required_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.cc_success, follow=True)
        redirect_url = '/company/credit-cart/update/'
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.cc_success, follow=True)
        redirect_url = '/company/credit-cart/update/'
        self.assertRedirects(response, redirect_url)


class OrganizationUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.cc_success = reverse('organization-update')

    def test_login_required(self):
        response = self.client.get(self.cc_success, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.cc_success)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        company = create_company()
        self.user.company = company
        response = self.client.get(self.cc_success, follow=True)
        redirect_url = '/legislation/select/your/plan/'
        self.assertRedirects(response, redirect_url)


class EmployeeAddViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.employee = reverse('employee-add')

    def test_login_required(self):
        response = self.client.get(self.employee, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.employee)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.employee, follow=True)
        redirect_url = '/legislation/select/your/plan/'
        self.assertRedirects(response, redirect_url)


class EmployeeListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.employee_list = reverse('employee-list')

    def test_login_required(self):
        response = self.client.get(self.employee_list, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.employee_list)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.employee_list, follow=True)
        redirect_url = '/legislation/select/your/plan/'
        self.assertRedirects(response, redirect_url)


class EmployeeEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.employee_edit = reverse('employee-edit', kwargs={'pk': cls.user.pk})

    def test_login_required(self):
        response = self.client.get(self.employee_edit, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.employee_edit)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.employee_edit, follow=True)
        redirect_url = '/legislation/select/your/plan/'
        self.assertRedirects(response, redirect_url)


class EmployeeDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.employee_delete = reverse('employee-delete', kwargs={'pk': cls.user.pk})

    def test_login_required(self):
        response = self.client.get(self.employee_delete, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.employee_delete)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.employee_delete, follow=True)
        redirect_url = '/legislation/select/your/plan/'
        self.assertRedirects(response, redirect_url)


class OrganizationAdminsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.org_admin = reverse('organization-admins')

    def test_login_required(self):
        response = self.client.get(self.org_admin, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.org_admin)
        self.assertRedirects(response, redirect_url)

    def test_organization_owner_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.org_admin, follow=True)
        self.assertEqual(response.status_code, 403)


class OrganizationAdminsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.org_admin_list = reverse('organization-admins-list')

    def test_login_required(self):
        response = self.client.get(self.org_admin_list, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.org_admin_list)
        self.assertRedirects(response, redirect_url)

    def test_organization_owner_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.org_admin_list, follow=True)
        self.assertEqual(response.status_code, 403)


class OrganizationAdminsAddViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.org_admin_add = reverse('organization-admins-add')

    def test_login_required(self):
        response = self.client.get(self.org_admin_add, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.org_admin_add)
        self.assertRedirects(response, redirect_url)

    def test_organization_owner_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.org_admin_add, follow=True)
        self.assertEqual(response.status_code, 403)


class OrganizationAdminsEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.org_admin_edit = reverse('organization-admins-edit', kwargs={'pk': cls.user.pk})

    def test_login_required(self):
        response = self.client.get(self.org_admin_edit, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.org_admin_edit)
        self.assertRedirects(response, redirect_url)

    def test_organization_owner_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.org_admin_edit, follow=True)
        self.assertEqual(response.status_code, 403)


class OrganizationAdminsDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.org_admin_delete = reverse('organization-admins-delete', kwargs={'pk': cls.user.pk})

    def test_login_required(self):
        response = self.client.get(self.org_admin_delete, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.org_admin_delete)
        self.assertRedirects(response, redirect_url)

    def test_organization_owner_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.org_admin_delete, follow=True)
        self.assertEqual(response.status_code, 403)


class CompanyUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.company_update = reverse('profile-update')

    def test_login_required(self):
        response = self.client.get(self.company_update, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.company_update)
        self.assertRedirects(response, redirect_url)


class LegalUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = create_user()
        cls.legal_update = reverse('legal-info')

    def test_login_required(self):
        response = self.client.get(self.legal_update, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.legal_update)
        self.assertRedirects(response, redirect_url)

    def test_organization_owner_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.legal_update, follow=True)
        self.assertEqual(response.status_code, 403)
