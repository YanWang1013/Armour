from django.apps import AppConfig


class GeneralConfig(AppConfig):
    """
    Clark: replace with full path to fit to Django 3.2
    """
    default_auto_field = 'django.db.models.BigAutoField'
    # name = 'general'
    name = 'armour.general'
