# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-22 00:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('netstore', '0010_auto_20171022_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2017, 10, 25, 0, 34, 39, 720821, tzinfo=utc), help_text=b'format: YYYY-MM-DD HH:MM'),
        ),
    ]