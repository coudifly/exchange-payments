# Generated by Django 2.0 on 2018-01-04 18:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('exchange_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyGateway',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('gateway', models.CharField(choices=[('coinpayments', 'CoinPayments')], max_length=50)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gateway', to='exchange_core.Currencies')),
            ],
            options={
                'verbose_name': 'Currency Gateway',
                'verbose_name_plural': 'Currencies Gateway',
            },
        ),
    ]