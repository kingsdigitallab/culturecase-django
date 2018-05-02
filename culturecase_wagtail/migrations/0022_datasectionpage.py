# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-11 17:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('culturecase_wagtail', '0021_menu_menuitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSectionPage',
            fields=[
                ('richpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='culturecase_wagtail.RichPage')),
            ],
            options={
                'abstract': False,
            },
            bases=('culturecase_wagtail.richpage',),
        ),
    ]
