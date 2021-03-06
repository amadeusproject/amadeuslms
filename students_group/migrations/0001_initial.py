# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-18 20:11
from __future__ import unicode_literals

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subjects', '0012_auto_20170112_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentsGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name', unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('last_update', models.DateTimeField(auto_now=True, verbose_name='Last Update')),
                ('participants', models.ManyToManyField(blank=True, related_name='group_participants', to=settings.AUTH_USER_MODEL, verbose_name='Participants')),
                ('subject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_subject', to='subjects.Subject', verbose_name='Subject')),
            ],
            options={
                'verbose_name': 'Students Group',
                'verbose_name_plural': 'Students Groups',
            },
        ),
    ]
