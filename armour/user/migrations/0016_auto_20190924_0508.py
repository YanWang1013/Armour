# Generated by Django 2.2 on 2019-09-24 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_user_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
    ]
