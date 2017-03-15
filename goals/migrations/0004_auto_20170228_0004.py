# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-28 03:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('goals', '0003_auto_20170227_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyGoals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(verbose_name='My Value')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('last_update', models.DateTimeField(auto_now=True, verbose_name='Last Update')),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mine_goals', to='goals.Goals', verbose_name='Goal')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_goals', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.AlterModelOptions(
            name='goalitem',
            options={'ordering': ['order']},
        ),
    ]