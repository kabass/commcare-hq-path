# Generated by Django 1.10.7 on 2017-05-19 12:42

import django.db.models.deletion
from django.db import migrations, models

import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0001_initial'),
        ('data_interfaces', '0008_update_case_rulesubmission'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreateScheduleInstanceActionDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipients', jsonfield.fields.JSONField(default=list)),
                ('alert_schedule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='scheduling.AlertSchedule')),
                ('timed_schedule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='scheduling.TimedSchedule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='caseruleaction',
            name='create_schedule_instance_definition',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data_interfaces.CreateScheduleInstanceActionDefinition'),
        ),
    ]