# Generated by Django 2.0.1 on 2018-03-23 12:30

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('exchange_payments', '0009_auto_20180314_1801'),
    ]

    operations = [
        migrations.CreateModel(
            name='Credentials',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('provider', models.CharField(choices=[('coinpayments', 'CoinPayments'), ('tcoin', 'Tcoin'), ('bitgo', 'BitGo')], max_length=20)),
                ('code', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]