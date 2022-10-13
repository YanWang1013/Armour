from django.core.mail import EmailMessage
from django.core import mail
from django.test import TestCase

from mixer.backend.django import mixer

from ..forms import MassEmailAdminForm, ContactForm


class MassMailFormTest(TestCase):
    def setUp(self):
        self.user = mixer.blend('user.user', is_company_owner=True)
        self.message = 'Test message'
        self.subject = 'Test subject'
        self.recipients = ['to1@example.com', 'to2@example.com', 'to3@example.com']
        self.form = MassEmailAdminForm()

    def test_massmail_form_fields_present(self):
        self.assertEqual(set(self.form.fields.keys()), {'locations', 'lnk', 'topics', 'content'})

    def test_send_email(self):
        mail.send_mail(
            self.subject, self.message,
            self.user,
            self.recipients,
            fail_silently=False
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test subject')
        self.assertEqual(mail.outbox[0].body, 'Test message')
        self.assertEqual(mail.outbox[0].from_email, self.user)
        self.assertEqual(len(mail.outbox[0].to), 3)
        self.assertIn('to2@example.com', mail.outbox[0].to)

    # SEND EMAIL TEST TO BE DONE WITH @override_settings ?


class ContactFormTest(TestCase):
    def setUp(self):
        self.form = ContactForm

    def test_contact_form_fields_present(self):
        self.assertEquals(set(self.form.base_fields), {'email', 'name', 'message', 'captcha'})
