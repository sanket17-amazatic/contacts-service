# Generated by Django 2.2 on 2019-05-15 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='role_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('owner', 'Owner'), ('member', 'Member')], max_length=10),
        ),
    ]