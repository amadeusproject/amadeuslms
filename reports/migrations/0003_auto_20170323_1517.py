# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-23 18:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_reportxls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportxls',
            name='xls_data',
            field=models.TextField(null=True),
        ),
    ]
