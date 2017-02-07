# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-01 04:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0004_auto_20170201_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='end_view_date',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Initial View Date'),
        ),
        migrations.AlterField(
            model_name='link',
            name='initial_view_date',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Initial View Date'),
        ),
    ]