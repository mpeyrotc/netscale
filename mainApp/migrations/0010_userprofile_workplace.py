# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-02 22:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0009_auto_20170625_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='workplace',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]
