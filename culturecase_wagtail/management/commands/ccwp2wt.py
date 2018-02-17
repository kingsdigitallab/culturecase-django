'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

from kdl_wordpress2wagtail.management.commands.kdlwp2wt import (
    Command as KdlWp2Wt
)
# from kdl_page.models import HomePage
# from wagtail.wagtailcore.models import Page
# from culturecase_wagtail.models import RichPage, HomePage


class Command(KdlWp2Wt):
    help = 'Import wordpress xml dump into wagtail'
