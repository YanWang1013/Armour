# Generated by Django 2.2 on 2020-03-20 08:01

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_auto_20190924_0508'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country',
            field=django_countries.fields.CountryField(max_length=2, null=True, verbose_name='Country'),
        ),
    ]
