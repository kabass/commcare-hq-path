# Generated by Django 1.11.14 on 2018-08-03 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('export', '0004_datafile_delete_after'),
    ]

    operations = [
        migrations.DeleteModel(name='DataFile'),
    ]