# Generated by Django 2.2 on 2020-04-28 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legislation', '0131_legistationnonconformanceresponse_topicpos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='legistationnonconformanceresponse',
            name='topicpos',
        ),
        migrations.AddField(
            model_name='legistationposition',
            name='topicpos',
            field=models.PositiveIntegerField(default=1, editable=False),
        ),
    ]
