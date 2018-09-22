# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filename',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.TextField(blank=True)),
                ('analysis', models.ForeignKey(to='analyses.Analysis', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
