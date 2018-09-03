# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 18:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0006_auto_20170102_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='professor',
            field=models.ManyToManyField(blank=True, related_name='professors', to=settings.AUTH_USER_MODEL),
        ),
    ]
