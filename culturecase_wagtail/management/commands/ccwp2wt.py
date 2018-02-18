'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

from kdl_wordpress2wagtail.management.commands.kdlwp2wt import (
    Command as KdlWp2Wt
)
from culturecase_wagtail.models import RichPage, HomePage
# from kdl_page.models import HomePage
# from wagtail.wagtailcore.models import Page


class Command(KdlWp2Wt):
    help = 'Import wordpress xml dump into wagtail'

    def convert_item_page(self, info):
        node = info['kdlnode']

        ret = {
            'model': RichPage,
            # Mapping between django model fields and wordpress node content
            'data': {
                'title': node['title'],
                'slug': node['wp:post_name'],
                'body': self.convert_body(node['content:encoded']),
            }
        }

        # select the model
        if info['wordpress_parentid'] == 'item_page:0':
            ret['model'] = HomePage

        return ret
