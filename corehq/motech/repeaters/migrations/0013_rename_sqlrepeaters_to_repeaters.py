# Generated by Django 3.2.16 on 2023-01-23 12:04

import corehq.motech.dhis2.repeaters
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motech', '0011_connectionsettings_is_deleted'),
        ('repeaters', '00012_create_default_names_for_repeaters'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameModel(
                    old_name='SQLRepeater',
                    new_name='Repeater',
                ),
            ]
        ),
        migrations.DeleteModel(
            name='SQLAppStructureRepeater',
        ),
        migrations.DeleteModel(
            name='SQLBaseCOWINRepeater',
        ),
        migrations.DeleteModel(
            name='SQLBaseExpressionRepeater',
        ),
        migrations.DeleteModel(
            name='SQLBeneficiaryRegistrationRepeater',
        ),
        migrations.DeleteModel(
            name='SQLBeneficiaryVaccinationRepeater',
        ),
        migrations.DeleteModel(
            name='SQLCaseExpressionRepeater',
        ),
        migrations.DeleteModel(
            name='SQLCaseRepeater',
        ),
        migrations.DeleteModel(
            name='SQLCreateCaseRepeater',
        ),
        migrations.DeleteModel(
            name='SQLDataRegistryCaseUpdateRepeater',
        ),
        migrations.DeleteModel(
            name='SQLDhis2EntityRepeater',
        ),
        migrations.DeleteModel(
            name='SQLDhis2Repeater',
        ),
        migrations.DeleteModel(
            name='SQLFHIRRepeater',
        ),
        migrations.DeleteModel(
            name='SQLFormRepeater',
        ),
        migrations.DeleteModel(
            name='SQLLocationRepeater',
        ),
        migrations.DeleteModel(
            name='SQLOpenmrsRepeater',
        ),
        migrations.DeleteModel(
            name='SQLReferCaseRepeater',
        ),
        migrations.DeleteModel(
            name='SQLShortFormRepeater',
        ),
        migrations.DeleteModel(
            name='SQLUpdateCaseRepeater',
        ),
        migrations.DeleteModel(
            name='SQLUserRepeater',
        ),
        migrations.CreateModel(
            name='AppStructureRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.repeater',),
        ),
        migrations.CreateModel(
            name='BaseExpressionRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.repeater',),
        ),
        migrations.CreateModel(
            name='CaseRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.repeater',),
        ),
        migrations.CreateModel(
            name='FormRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.repeater',),
        ),
        migrations.CreateModel(
            name='LocationRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.repeater',),
        ),
        migrations.CreateModel(
            name='ShortFormRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.repeater',),
        ),
        migrations.CreateModel(
            name='UserRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.repeater',),
        ),
        migrations.CreateModel(
            name='BaseCOWINRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.caserepeater',),
        ),
        migrations.CreateModel(
            name='CaseExpressionRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.baseexpressionrepeater',),
        ),
        migrations.CreateModel(
            name='CreateCaseRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.caserepeater',),
        ),
        migrations.CreateModel(
            name='Dhis2EntityRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.caserepeater', corehq.motech.dhis2.repeaters.Dhis2Instance),
        ),
        migrations.CreateModel(
            name='Dhis2Repeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.formrepeater', corehq.motech.dhis2.repeaters.Dhis2Instance),
        ),
        migrations.CreateModel(
            name='FHIRRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.caserepeater',),
        ),
        migrations.CreateModel(
            name='OpenmrsRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.caserepeater',),
        ),
        migrations.CreateModel(
            name='UpdateCaseRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.caserepeater',),
        ),
        migrations.CreateModel(
            name='BeneficiaryRegistrationRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.basecowinrepeater',),
        ),
        migrations.CreateModel(
            name='BeneficiaryVaccinationRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.basecowinrepeater',),
        ),
        migrations.CreateModel(
            name='DataRegistryCaseUpdateRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.createcaserepeater',),
        ),
        migrations.CreateModel(
            name='ReferCaseRepeater',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('repeaters.createcaserepeater',),
        ),
    ]