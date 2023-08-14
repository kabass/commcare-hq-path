# Generated by Django 1.11.6 on 2017-10-24 18:11

from django.core.management import call_command
from django.db import migrations

from corehq.privileges import LOGIN_AS


def _grandfather_login_as(apps, schema_editor):
    call_command(
        'cchq_prbac_grandfather_privs',
        LOGIN_AS,
        skip_edition='Community',
        noinput=True,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0014_paymentmethod__web_user__nonnullable'),
    ]

    operations = [
        migrations.RunPython(_grandfather_login_as),
    ]