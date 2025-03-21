# Generated by Django 5.1.1 on 2024-09-24 16:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_user_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10, unique=True)),
                ('iccid', models.CharField(max_length=6, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='iccid',
            field=models.CharField(default='NONE', max_length=6),
        ),
        migrations.AlterField(
            model_name='user',
            name='phoneNumber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.phonenumber'),
        ),
    ]
