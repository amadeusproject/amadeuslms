# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-08-30 11:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0016_auto_20170831_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='description_brief',
            field=models.TextField(blank=True, verbose_name='simpler description'),
        ),
    ]
