# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-18 21:00
from __future__ import unicode_literals

from django.db import migrations

from django.contrib.postgres.operations import UnaccentExtension

class Migration(migrations.Migration):

    dependencies = [
        ('students_group', '0001_initial'),
    ]

    operations = [
    	UnaccentExtension()
    ]
