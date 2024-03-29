# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-08-06 18:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mural', '0011_auto_20210731_1457'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='categorypost',
            index=models.Index(fields=['mural_ptr_id', 'space'], name='mural_categ_mural_p_d8b924_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['user', 'post'], name='mural_comme_user_id_d9334b_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['user', 'post', 'last_update'], name='mural_comme_user_id_fe6c5b_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['user', 'post', 'create_date'], name='mural_comme_user_id_82232d_idx'),
        ),
        migrations.AddIndex(
            model_name='subjectpost',
            index=models.Index(fields=['mural_ptr_id', 'space'], name='mural_subje_mural_p_1159af_idx'),
        ),
        migrations.AddIndex(
            model_name='subjectpost',
            index=models.Index(fields=['mural_ptr_id', 'resource', 'space'], name='mural_subje_mural_p_034193_idx'),
        ),
    ]
