# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-25 18:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0008_thread_thread_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='picture',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
