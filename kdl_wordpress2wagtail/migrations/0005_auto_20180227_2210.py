# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-27 22:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kdl_wordpress2wagtail', '0004_auto_20180218_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kdlwordpressreference',
            name='wordpressid',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
