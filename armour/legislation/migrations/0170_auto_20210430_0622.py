# Generated by Django 3.1.8 on 2021-04-30 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legislation', '0169_auto_20210419_2024'),
    ]

    operations = [
        migrations.RenameField(
            model_name='legislationdocument',
            old_name='legislation',
            new_name='register',
        ),
    ]
