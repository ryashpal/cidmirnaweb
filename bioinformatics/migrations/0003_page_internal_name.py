# Generated by Django 2.1.2 on 2018-10-07 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bioinformatics', '0002_auto_20181008_0142'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='internal_name',
            field=models.CharField(default='', max_length=40, unique=True),
            preserve_default=False,
        ),
    ]
