# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-11-08 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_video_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='video_times',
            field=models.IntegerField(default=0, verbose_name='视频时间'),
        ),
    ]