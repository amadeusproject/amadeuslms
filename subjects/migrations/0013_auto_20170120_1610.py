# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-20 19:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0012_auto_20170112_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='subjects.Tag', verbose_name='tags'),
        ),
    ]
