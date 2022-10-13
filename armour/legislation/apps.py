from django.apps import AppConfig


class LegislationConfig(AppConfig):
    """
        Clark: replace with full path to fit to Django 3.2
    """
    default_auto_field = 'django.db.models.BigAutoField'
    # name = 'legislation'
    name = 'armour.legislation'
