# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-05-08 17:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fights', '0017_auto_20170222_1735'),
    ]

    operations = [
        migrations.CreateModel(
            name='FightQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('win_loss_streak', models.IntegerField(blank=True, null=True)),
                ('min_age', models.PositiveIntegerField(blank=True, null=True)),
                ('max_age', models.PositiveIntegerField(blank=True, null=True)),
                ('min_experience', models.IntegerField(blank=True, null=True)),
                ('max_experience', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
