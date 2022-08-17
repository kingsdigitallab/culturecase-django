# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-28 19:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('culturecase_wagtail', '0010_auto_20180227_2046'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchCategoryHomePage',
            fields=[
                ('richpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='culturecase_wagtail.RichPage')),
            ],
            options={
                'abstract': False,
            },
            bases=('culturecase_wagtail.richpage',),
        ),
        migrations.CreateModel(
            name='ResearchCategoryPage',
            fields=[
                ('richpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='culturecase_wagtail.RichPage')),
            ],
            options={
                'abstract': False,
            },
            bases=('culturecase_wagtail.richpage',),
        ),
    ]
