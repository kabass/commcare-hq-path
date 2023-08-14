# Generated by Django 1.10.7 on 2017-07-03 21:23

from django.conf import settings
from django.db import migrations

from corehq.sql_db.operations import RawSQLMigration

migrator = RawSQLMigration(('corehq', 'sql_proxy_accessors', 'sql_templates'), {
    'PL_PROXY_CLUSTER_NAME': settings.PL_PROXY_CLUSTER_NAME
})


class Migration(migrations.Migration):

    dependencies = [
        ('sql_proxy_accessors', '0035_livequery_sql'),
    ]

    operations = [
        migrations.RunSQL("""DROP FUNCTION IF EXISTS save_case_and_related_models(
                TEXT,
                form_processor_commcarecasesql,
                form_processor_casetransaction[],
                form_processor_commcarecaseindexsql[],
                form_processor_caseattachmentsql[],
                INTEGER[],
                INTEGER[])"""
                 )
    ]