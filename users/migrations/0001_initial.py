# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-20 18:17
from __future__ import unicode_literals

import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(help_text='Your email address that will be used to access the platform', max_length=254, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[\\w.@+-]+$', 32), 'Type a valid username. This fields should only contain letters, numbers and the characteres: @/./+/-/_ .', 'invalid')], verbose_name='Mail')),
                ('username', models.CharField(max_length=100, verbose_name='Name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last Name')),
                ('social_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Social Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('image', models.ImageField(blank=True, null=True, upload_to='users/', verbose_name='Photo')),
                ('type_profile', models.IntegerField(blank=True, choices=[(1, 'Professor'), (2, 'Student'), (3, 'Coordinator')], null=True, verbose_name='Type')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('show_email', models.IntegerField(choices=[(1, 'Allow everyone to see my address'), (2, 'Only classmates can see my address'), (3, 'Nobody can see my address')], null=True, verbose_name='Show email?')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Administrator')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
