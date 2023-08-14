# Generated by Django 2.2.24 on 2021-08-24 17:30

from django.db import migrations

from corehq.apps.users.models import UserHistory
from corehq.util.django_migrations import skip_on_fresh_install


def noop(*args, **kwargs):
    pass


@skip_on_fresh_install
def _reset_records(*args, **kwargs):
    UserHistory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_auto_20210826_1155'),
    ]

    operations = [
        migrations.RunPython(_reset_records, reverse_code=noop),
    ]