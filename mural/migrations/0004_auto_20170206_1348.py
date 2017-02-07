# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-06 16:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mural', '0003_auto_20170204_1625'),
    ]

    operations = [
        migrations.CreateModel(
            name='MuralFavorites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='mural',
            name='action',
            field=models.CharField(choices=[('comment', 'Comment'), ('help', 'Ask for Help')], default='comment', max_length=100, verbose_name='Action'),
        ),
        migrations.AddField(
            model_name='muralfavorites',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorites_post', to='mural.Mural', verbose_name='Post'),
        ),
        migrations.AddField(
            model_name='muralfavorites',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorites_user', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]