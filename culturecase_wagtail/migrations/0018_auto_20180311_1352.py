# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-11 13:52
from __future__ import unicode_literals

from django.db import migrations


def load_initial_wordpress_content(apps, schema_editor):
    from django.core.management.commands import loaddata
    from django.core import management
    management.call_command(
        'loaddata',
        'culturecase_wagtail/data/culturecase.wordpress.2018-03-06.json',
        verbosity=0
    )


class Migration(migrations.Migration):

    dependencies = [
        ('culturecase_wagtail', '0017_homepageslide_text_color'),
    ]

    operations = [
        migrations.RunPython(load_initial_wordpress_content),
    ]
