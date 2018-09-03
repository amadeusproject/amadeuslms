# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-21 03:51
from __future__ import unicode_literals

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name', unique=True, verbose_name='Slug')),
                ('description', models.CharField(max_length=300, verbose_name='description')),
                ('visible', models.BooleanField(verbose_name='visible')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('modified_date', models.DateTimeField(auto_now_add=True, verbose_name='Modified Date')),
                ('category_father', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_parent', to='categories.Category')),
                ('coordinators', models.ManyToManyField(related_name='coordinators', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'verbose_name': 'Category',
            },
        ),
    ]
