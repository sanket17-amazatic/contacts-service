# Generated by Django 2.2 on 2019-05-15 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20190514_0435'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_active',
            new_name='is_otp_verified',
        ),
    ]