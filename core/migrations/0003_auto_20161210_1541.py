# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-10 18:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20161124_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mimetype',
            name='icon',
            field=models.CharField(max_length=50, verbose_name='Icon'),
        ),
    ]
