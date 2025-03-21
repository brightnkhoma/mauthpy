# Generated by Django 5.1.1 on 2024-12-03 20:25

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_tower_user_average_transaction_user_balance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='time',
            field=models.CharField(default=datetime.datetime(2024, 12, 3, 20, 25, 51, 845784, tzinfo=datetime.timezone.utc), max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='phoneNumber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.phonenumber'),
        ),
    ]
