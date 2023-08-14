# Generated by Django 1.11.20 on 2019-03-26 08:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0017_locationrelation_last_modified'),
        ('app_manager', '0002_latestenabledbuildprofiles'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppReleaseByLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=255)),
                ('app_id', models.CharField(max_length=255)),
                ('build_id', models.CharField(max_length=255)),
                ('version', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('activated_on', models.DateTimeField(blank=True, null=True)),
                ('deactivated_on', models.DateTimeField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               to='locations.SQLLocation', to_field='location_id')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='appreleasebylocation',
            unique_together=set([('domain', 'build_id', 'location', 'version')]),
        ),
    ]