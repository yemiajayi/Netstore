# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-18 17:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('netstore', '0004_auto_20171017_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2017, 10, 21, 17, 12, 51, 91918, tzinfo=utc), help_text=b'format: YYYY-MM-DD HH:MM'),
        ),
    ]
