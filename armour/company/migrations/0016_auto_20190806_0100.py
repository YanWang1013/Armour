# Generated by Django 2.2 on 2019-08-06 01:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0015_payments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payments',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paymentscc', to='company.Company'),
        ),
    ]
