from captcha.fields import ReCaptchaField
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db.models import Prefetch
from django.utils.translation import ugettext_lazy as _

from armour.company.models import Company
from armour.legislation.models import Location, Topic
from armour.user.models import User
from .models import MassEmail
from ckeditor.widgets import CKEditorWidget
from django.contrib.flatpages.forms import FlatpageForm


class ContactForm(forms.Form):
    email = forms.CharField(label='', required=True,
                            widget=forms.EmailInput(attrs={"autocomplete": "email", 'placeholder': 'Email', 'class': "form-control icon-right"}))
    name = forms.CharField(label='', required=True,
                           widget=forms.TextInput(attrs={"autocomplete": "name", 'placeholder': 'Name', 'class': "form-control icon-right"}))
    message = forms.CharField(label='', required=True, widget=forms.Textarea(
        attrs={'rows': "3", 'class': "form-control", 'placeholder': 'Message', }))
    captcha = ReCaptchaField()


class MassEmailAdminForm(forms.ModelForm):
    lnk = forms.CharField(label='Updade link', required=False, initial="112")
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.filter(published=True),
                                            widget=FilteredSelectMultiple('Topics', is_stacked=False),
                                            required=False)
    locations = forms.ModelMultipleChoiceField(queryset=Location.objects.filter(published=True),
                                               widget=FilteredSelectMultiple('Locations', is_stacked=False),
                                               required=False)

    def clean(self):
        data = super().clean()
        topics = data.get('topics')
        locations = data.get('locations')

        if topics.count() == 0 and locations.count() == 0:
            raise ValidationError(_("At least one Topic or Location must be selected to send message!"))

        companies = Company.objects.prefetch_related(
            Prefetch('topics', queryset=topics), Prefetch('locations', queryset=locations)
        )
        companies = companies.distinct('id')
        receivers = User.objects.all().filter(is_company_owner=True).prefetch_related(
            Prefetch('company', queryset=companies)
        )

        if receivers.count() == 0:
            raise ValidationError(_("Message with current selection of locations and/or topics won't reach any recipients!"))

        return data

    def save(self, commit=True):
        instance = super(MassEmailAdminForm, self).save(commit=False)
        instance.save()
        self.save_m2m()

        t = instance.topics.all()
        l = instance.locations.all()

        if t.count() == 0 and l.count() > 0:
            companies = Company.objects.prefetch_related(
                Prefetch('locations', queryset=l)
            )

        elif l.count() == 0 and t.count() > 0:
            companies = Company.objects.prefetch_related(
                Prefetch('topics', queryset=t)
            )
        else:
            companies = Company.objects.prefetch_related(
                Prefetch('topics', queryset=t), Prefetch('locations', queryset=l)
            )

        companies = companies.distinct('id')

        receivers = User.objects.all().filter(is_company_owner=True).prefetch_related(
            Prefetch('company', queryset=companies)
        )

        for receiver in receivers.all():
            instance.sent_to.add(receiver)

        recipients = []
        for recipient in instance.sent_to.all():
            recipients.append(recipient.email)

        mail = EmailMessage(subject="Information email", body=instance.content,
                            from_email=settings.DEFAULT_FROM_EMAIL, bcc=recipients)

        mail.content_subtype = 'html'

        mail.send()

        return instance

    class Meta:
        model = MassEmail
        fields = ('locations', 'topics', 'content', )


class FlatpageCustomForm(FlatpageForm):
    def __init__(self, *args, **kwargs):
        super(FlatpageCustomForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = CKEditorWidget()