# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-21 22:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('netstore', '0008_auto_20171021_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2017, 10, 24, 22, 25, 58, 687901, tzinfo=utc), help_text=b'format: YYYY-MM-DD HH:MM'),
        ),
    ]