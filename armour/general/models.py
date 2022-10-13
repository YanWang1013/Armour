from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_currentuser.db.models import CurrentUserField

from ckeditor.fields import RichTextField
from ..user.models import User
from ..legislation.models import Location, Topic


class Tip(models.Model):
    name = models.CharField(_('Title'), max_length=400, )
    content = RichTextField(_('Content'), max_length=4000, )
    avatar = models.ImageField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Help')
        verbose_name_plural = _(u'Help')
        ordering = ["name"]


class MassEmail(models.Model):
    locations = models.ManyToManyField(Location, verbose_name='Locations', blank=True, )
    topics = models.ManyToManyField(Topic, verbose_name='Topics', blank=True, )
    sent_at = models.DateTimeField(_("Sent at"), auto_now_add=True, )
    content = RichTextField(_('Content'), max_length=4000, )
    sender = CurrentUserField(_("Sender"), related_name='sender', )
    sent_to = models.ManyToManyField(User, verbose_name='Receivers', )

    def get_locations(self):
        return ", ".join([str(el) for el in self.locations.all()])

    get_locations.short_description = 'Locations'

    def get_topics(self):
        return ", ".join([str(el) for el in self.topics.all()])

    get_topics.short_description = 'Topics'

    def get_receivers(self):
        return ", ".join([str(el) for el in self.sent_to.all()])

    get_receivers.short_description = 'Receivers'

