# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-28 22:56
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.contenttypes.models import ContentType


def load_initial_wordpress_content(apps, schema_editor):
    from django.core.management.commands import loaddata
    from django.core import management

    if 0:
        # Not a good idea to do it here.
        # Because at this stage the model can be more complete or different
        # than in the database and the indexing will crash..
        for i in [0, 1]:
            management.call_command(
                'ccwp2wt',
                'import',
                'culturecase_wagtail/fixtures/culturecase.wordpress.2018-03-28.xml',
            )

        management.call_command(
            'update_index',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('culturecase_wagtail', '0018_auto_20180311_1352'),
    ]

    operations = [
        migrations.RunPython(load_initial_wordpress_content),
    ]