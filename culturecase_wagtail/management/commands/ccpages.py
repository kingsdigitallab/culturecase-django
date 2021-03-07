'''
Created on 15 Feb 2018

@author: jeff
'''
from culturecase_wagtail.models import RichPage
from kdl_wordpress2wagtail.management.commands._kdlcommand import KDLCommand
import re
import os
from bs4 import BeautifulSoup

class Command(KDLCommand):
    help = 'Asset management'

    def add_arguments(self, parser):
        parser.add_argument('action', nargs=1, type=str)
        parser.add_argument('aargs', nargs='*', type=str)

    def action_fixbody(self):
        ids = self.options.get('aargs', [])
        options = {}
        if ids:
            options = {'id__in': ids}

        for p in RichPage.objects.filter    (**options).order_by('id'):
            p = p.specific
            print(p.id, p.title, p.last_published_at)
            body = p.body
            if body:
                body2 = str(BeautifulSoup(body, 'html.parser'))
                if body2 != body:
                    # print(repr(body))
                    print('^ different')
                    p.body = body2
                    p.save()
                    # print(repr(body2))

