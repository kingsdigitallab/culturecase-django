# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-25 23:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('culturecase_wagtail', '0004_auto_20180225_1905'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchPage',
            fields=[
                ('richpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='culturecase_wagtail.RichPage')),
            ],
            options={
                'abstract': False,
            },
            bases=('culturecase_wagtail.richpage',),
        ),
        migrations.AlterField(
            model_name='richpage',
            name='short_title',
            field=models.CharField(blank=True, default=None, help_text='A word or two that can be included in the main menu', max_length=32, null=True, verbose_name='Short title'),
        ),
    ]
