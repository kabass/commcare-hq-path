# Generated by Django 1.11.16 on 2019-01-30 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0040_auto_20181002_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaccount',
            name='restrict_signup_message',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]