# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-01 20:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0010_auto_20170201_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='coordinators',
            field=models.ManyToManyField(blank=True, related_name='Coordenadores', to=settings.AUTH_USER_MODEL),
        ),
    ]
