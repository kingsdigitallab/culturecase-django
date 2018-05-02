'''
Created on 13 April 2018

@author: Geoffroy Noel
'''

import re
from kdl_wordpress2wagtail.management.commands._kdlcommand import KDLCommand
from wagtail.wagtailcore.models import Page
from culturecase_wagtail.models import Menu, MenuItem, StaticPage,\
    DataSectionPage
from django.core.exceptions import ValidationError


class Command(KDLCommand):
    '''
    see get_operation_from_migration()

    Wagtail data migration can't easily be run in a django data migration
    because the models are method-less and adding a child page
    doesnt work there.

    This is a work-around. We call the command from a data migration, it
    will be executed with normal django models.

    Usage:

    1. create a new empty data migration for your app
    ./manage.py makemigration APPNAME --empty
    2. open the new migration file and change the operations array
        (see get_operation_from_migration())
    3. create a new method below with name action_MIGRATION_NAME()

    '''
    help = 'Runs a wagtail data migration'

    def action_0023_add_menus(self):
        if 1:
            page_data = create_page(
                DataSectionPage,
                'CultureCase Data',
                'data',
                'CultureCase Data Landing Page',
            )
            create_page(
                StaticPage,
                'About CultureCase Data',
                'about-data',
                'Info about the CultureCase Data section',
                page_data
            )

        create_menu('primary', ['how-to-use', 'faqs', 'about', 'links'])
        create_menu('research', ['contents', 'insights', 'impacts'])
        create_menu('data', ['about-data'])


def create_page(PageType, title, slug, body, parent=None):
    ret = None
    if not parent:
        # The home page is the parent.
        # Find the site first.
        parent = Page.objects.filter(slug='research').order_by('id').first()
        parent = parent.get_parent()
    if not parent:
        raise Exception('Error parent page not found')

    page = PageType(title=title, slug=slug, body=body)

    try:
        parent.add_child(instance=page)
    except ValidationError as e:
        if 'slug' in e.error_dict:
            print('Page "%s" already exists' % slug)
        else:
            raise

    return ret


def create_menu(menu_slug, page_slugs):
    # create the menus

    menu_items = []
    for page_slug in page_slugs:
        page = Page.objects.filter(slug=page_slug).order_by('id').first()
        if page is None:
            raise Exception('Page slug not found: "%s"' % page_slug)
        menu_items.append(MenuItem(page=page))

    menu, _ = Menu.objects.get_or_create(slug=menu_slug)
    menu.menu_items = menu_items
    menu.save()


MIGRATION_NAME = None


def get_operation_from_migration(migrations, debug=False):
    '''
    Helper to conveniently run wagtail data changes from a django data
    migration.

    Usage: call it like this from your Migration class:

        operations = [
            get_operation_from_migration(migrations, debug=True),
        ]

    '''

    global MIGRATION_NAME
    import inspect

    stack = inspect.stack()
    for frame in stack:
        frame, filename, line_number, function_name, lines, index = frame
        names = re.findall(r'(\d{4}_.*)\.py$', filename)
        if names:
            MIGRATION_NAME = names[0]
            break

    if not MIGRATION_NAME:
        raise Exception('Migration name not found in stack')

    method = run_wagtail_data_migration
    if debug:
        method = run_wagtail_data_migration_debug

    ret = migrations.RunPython(method)
    return ret


def run_wagtail_data_migration_debug(apps, schema_editor):
    ret = run_wagtail_data_migration(apps, schema_editor, debug=True)
    return ret


def run_wagtail_data_migration(apps, schema_editor, debug=False):
    global MIGRATION_NAME
    from django.core import management

    migration_name = MIGRATION_NAME

    args = ['ccmigrate', migration_name]
    if debug:
        args.append('--dry-run')

    management.call_command(*args)

    if debug:
        raise Exception('ROLLBACK')
