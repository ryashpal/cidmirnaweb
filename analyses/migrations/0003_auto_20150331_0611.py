# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('analyses', '0002_filename'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('command_line', models.TextField()),
                ('machine', models.TextField()),
                ('process_id', models.IntegerField(null=True, blank=True)),
                ('exit_code', models.IntegerField(null=True, blank=True)),
                ('start_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('analysis', models.ForeignKey(to='analyses.Analysis', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='analysis',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 31, 6, 11, 56, 227735, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filename',
            name='input',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='analysis',
            name='sent',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
