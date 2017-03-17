# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-17 01:15
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20170309_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drive',
            name='repeated_week_days',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, size=None),
        ),
        migrations.AlterField(
            model_name='hitch',
            name='repeated_week_days',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, size=None),
        ),
    ]
