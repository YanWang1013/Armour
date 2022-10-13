from django.test import TestCase, Client
from django.urls import reverse

from armour.legislation.tests.helpers import *


class SpecificQuestionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.s_q_url = reverse('spec-questions')
        cls.user = mixer.blend('user.user')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.s_q_url, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.s_q_url)
        self.assertRedirects(response, redirect_url)

    # FIXME PaymentValidMixin is not part of this view right now
    # def test_payment_valid_mixin(self):
    #     self.client.force_login(user=self.user)
    #     response = self.client.get(self.s_q_url)
    #     self.assertEqual(response.status_code, 302)


class SetSpecQuestionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.s_s_q_url = reverse('spec-question-set')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.s_s_q_url, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.s_s_q_url)
        self.assertRedirects(response, redirect_url)
# FIXME test actual functionality


class LegislationTopicsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.legislation_topics_url = reverse('iso-standards')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.legislation_topics_url, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.legislation_topics_url)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.legislation_topics_url)
        self.assertEqual(response.status_code, 302)

    def test_get_context(self):
        response = self.client.get(self.legislation_topics_url)
        self.assertIsNone(response.context)


class LegislationTopicsContentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.l_t_c = reverse('iso-standards-content')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.l_t_c, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.l_t_c)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin_ajax(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.l_t_c)
        self.assertEqual(response.status_code, 400)


class SetLegistaltionTopicViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.s_l_t = reverse('iso-standards-content')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.s_l_t, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.s_l_t)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin_ajax(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.s_l_t)
        self.assertEqual(response.status_code, 400)

    def test_post_without_paids(self):
        self.client.force_login(user=self.user)
        response = self.client.post(self.s_l_t)
        self.assertEqual(response.status_code, 400)


class LegislationNonConformanceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.l_n_c = reverse('non-conformance')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.l_n_c, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.l_n_c)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.l_n_c)
        self.assertEqual(response.status_code, 302)


class SetNonConformanceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.s_n_c = reverse('non-conformance-set', kwargs={'pk': 1})
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.s_n_c, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.s_n_c)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin_ajax(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.s_n_c)
        self.assertEqual(response.status_code, 400)

    def test_post_without_LNCR(self):
        self.client.force_login(user=self.user)
        response = self.client.post(self.s_n_c)
        self.assertEqual(response.status_code, 400)


class FinishViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.finish = reverse('finish')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.finish, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.finish)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.finish, follow=True)
        redirect_url = '/legislation/select/your/plan/'
        self.assertRedirects(response, redirect_url)


class LegislationListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.leglist = reverse('product-report')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.leglist, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.leglist)
        self.assertRedirects(response, redirect_url)

    def test_payment_valid_mixin(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.leglist, follow=True)
        redirect_url = '/legislation/select/your/plan/'
        self.assertRedirects(response, redirect_url)

    def test_get_context(self):
        response = self.client.get(self.leglist)
        self.assertIsNone(response.context)


class LegislationDocView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.legdoc = reverse('product-report')
        cls.client = Client()
        cls.user = create_user()

    def test_login_required(self):
        response = self.client.get(self.legdoc, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.legdoc)
        self.assertRedirects(response, redirect_url)
