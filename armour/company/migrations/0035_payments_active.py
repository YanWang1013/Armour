# Generated by Django 2.2 on 2019-10-17 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0034_auto_20190926_0505'),
    ]

    operations = [
        migrations.AddField(
            model_name='payments',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
