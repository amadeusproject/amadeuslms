# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-22 01:23
from __future__ import unicode_literals

from django.db import migrations, models
import material_delivery.models


class Migration(migrations.Migration):

    dependencies = [
        ('material_delivery', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentmaterial',
            options={'ordering': ['upload_date'], 'verbose_name': 'Student Material', 'verbose_name_plural': 'Student Materials'},
        ),
        migrations.AlterField(
            model_name='materialdelivery',
            name='data_end',
            field=models.DateTimeField(blank=True, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='materialdelivery',
            name='data_ini',
            field=models.DateTimeField(blank=True, verbose_name='Init Date'),
        ),
        migrations.AlterField(
            model_name='studentmaterial',
            name='file',
            field=models.FileField(blank=True, upload_to=material_delivery.models.get_upload_student_path, validators=[material_delivery.models.validate_file_extension], verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='supportmaterial',
            name='file',
            field=models.FileField(blank=True, upload_to=material_delivery.models.get_upload_support_path, validators=[material_delivery.models.validate_file_extension], verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='teacherevaluation',
            name='evaluation_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Evaluation Date'),
        ),
        migrations.AlterField(
            model_name='teacherevaluation',
            name='file',
            field=models.FileField(blank=True, upload_to=material_delivery.models.get_upload_teacher_path, validators=[material_delivery.models.validate_file_extension], verbose_name='File'),
        ),
    ]
