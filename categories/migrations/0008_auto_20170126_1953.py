# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-26 22:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0007_auto_20170118_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='coordinators',
            field=models.ManyToManyField(blank=True, related_name='coordinators', to=settings.AUTH_USER_MODEL),
        ),
    ]
