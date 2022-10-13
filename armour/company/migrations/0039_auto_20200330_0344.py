# Generated by Django 2.2 on 2020-03-30 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legislation', '0105_auto_20200219_0138'),
        ('company', '0038_auto_20200326_0337'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='sector',
        ),
        migrations.AddField(
            model_name='company',
            name='sector',
            field=models.ManyToManyField(blank=True, related_name='companysectors', to='legislation.Sector', verbose_name='Sector'),
        ),
    ]
