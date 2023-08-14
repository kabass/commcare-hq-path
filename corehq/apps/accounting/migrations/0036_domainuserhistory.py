# Generated by Django 1.11.14 on 2018-07-14 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0035_merge_20180711_2039'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainUserHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=256)),
                ('record_date', models.DateField()),
                ('num_users', models.IntegerField(default=0, null=True)),
            ],
        ),
    ]