# Generated by Django 1.10.7 on 2017-07-06 21:18

from django.db import migrations




class Migration(migrations.Migration):

    dependencies = [
        ('sql_accessors', '0049_remove_save_case'),
    ]

    operations = [
        migrations.RunSQL("DROP FUNCTION IF EXISTS get_extension_case_ids(text, text[])")
    ]