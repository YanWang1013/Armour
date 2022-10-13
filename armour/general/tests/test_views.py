from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from mixer.backend.django import mixer


class TipsViewTest(TestCase):
    def setUp(self):
        self.user = mixer.blend('user.user')
        # self.tip = Tip.objects.create(name='Pro Tip', content="Content of this pro tip",)
        self.tips_url = reverse('tips-list')
        self.tip_url = reverse('tip-details', kwargs={'pk': 1})

    def test_list_view_login_required(self):
        response = self.client.get(self.tips_url, follow=True)
        redirect_url = '{}?next={}'.format(reverse(settings.LOGIN_URL), self.tips_url)
        self.assertRedirects(response, redirect_url)


    def test_list_view(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.tips_url)
        self.assertEqual(response.status_code, 200)


# pagination test maybe?

class ContactViewTest(TestCase):
    def setUp(self):
        self.contact_url = reverse('contact-form')
        response = self.client.get(self.contact_url)

        self.assertEquals(response.status_code, 200)
