# Generated by Django 2.0.1 on 2018-03-23 12:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exchange_payments', '0010_credentials'),
    ]

    operations = [
        migrations.AddField(
            model_name='credentials',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='credentials', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='credentials',
            unique_together={('provider', 'user')},
        ),
    ]
