# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-11 13:52
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.contenttypes.models import ContentType


def load_initial_wordpress_content(apps, schema_editor):
    from django.core import management

    # GN - 2022 - commented out, this is a very bad idea to load fixture
    # from a migration, because Django will complain about the latest model
    # not matching the old schema saved in the fixture.
    # In this case culturecase_wagtail_richpage.show_kcl_logo will be removed
    # in migration 0024, but the model already reflect that change.
    if 0:
        # remove all existing content types to avoid duplicate keys
        for ct in ContentType.objects.all():
            ct.delete()

        management.call_command(
            'loaddata',
            'culturecase.wordpress.2018-03-06b.json',
            verbosity=0
        )


class Migration(migrations.Migration):

    dependencies = [
        ('culturecase_wagtail', '0017_homepageslide_text_color'),
        ('sessions', '0001_initial'),
        ('kdl_wordpress2wagtail', '0005_auto_20180227_2210'),
        ('wagtaildocs', '0007_merge'),
        ('wagtailusers', '0006_userprofile_prefered_language'),
        ('wagtailadmin', '0001_create_admin_access_permissions'),
        ('wagtailembeds', '0003_capitalizeverbose'),
        ('wagtailsearch', '0003_remove_editors_pick'),
    ]

    operations = [
        migrations.RunPython(load_initial_wordpress_content),
    ]
