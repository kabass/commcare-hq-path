# Generated by Django 1.11.16 on 2018-11-27 23:02

from django.db import migrations

from corehq.sql_db.operations import RawSQLMigration
from corehq.sql_db.migrations import partitioned

migrator = RawSQLMigration(('corehq', 'blobs', 'sql_templates'), {})


@partitioned
class Migration(migrations.Migration):

    dependencies = [
        ('form_processor', '0076_form_attachment_fk'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE form_processor_xformattachmentsql
                ALTER COLUMN properties DROP NOT NULL;
            """,
            """
            ALTER TABLE form_processor_xformattachmentsql
                ALTER COLUMN properties SET NOT NULL;
            """,
        ),
    ]