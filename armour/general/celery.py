from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

import environ
envc = environ.Env()

os.environ.setdefault('DJANGO_SETTINGS_MODULE',envc('DJANGO_SETTINGS_MODULE', default='config.settings.local') )

app = Celery('armour')

app.config_from_object('django.conf:settings',)

app.autodiscover_tasks(settings.INSTALLED_APPS)
