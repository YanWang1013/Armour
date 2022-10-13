# Generated by Django 2.2 on 2020-02-07 05:00

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legislation', '0097_auto_20200206_0418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keypoint',
            name='point',
            field=ckeditor.fields.RichTextField(max_length=10000, verbose_name='Key Point'),
        ),
        migrations.AlterField(
            model_name='legislationtopic',
            name='description',
            field=ckeditor.fields.RichTextField(max_length=10000, null=True, verbose_name='Full description'),
        ),
        migrations.AlterField(
            model_name='legislationtopiccomply',
            name='title',
            field=ckeditor.fields.RichTextField(max_length=10000, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='requirments',
            name='description',
            field=ckeditor.fields.RichTextField(max_length=10000, null=True, verbose_name='Full description'),
        ),
    ]
