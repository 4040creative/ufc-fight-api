# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-15 00:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fights', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fight',
            name='win',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
