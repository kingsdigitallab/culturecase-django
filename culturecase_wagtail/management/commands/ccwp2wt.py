'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

from kdl_wordpress2wagtail.management.commands.kdlwp2wt import (
    Command as KdlWp2Wt
)
from culturecase_wagtail.models import RichPage, HomePage
from kdl_wordpress2wagtail.models import KDLWordpressReference
from django.utils.text import slugify
# from kdl_page.models import HomePage
# from wagtail.wagtailcore.models import Page


ALIAS_HOME_PAGE = 'alias:home_page'
ALIAS_RESEARCH_PARENT = 'alias:research_parent'


class Command(KdlWp2Wt):
    help = 'Import wordpress xml dump into wagtail'

    def set_predefined_objects2(self):
        super(Command, self).set_predefined_objects()

        # All item_research will be created as wagtail Page under a new
        # top level Page called 'research'.
        wordpressid = 'item_research:0'

        research_parent = KDLWordpressReference.get_django_object(
            wordpressid
        )

        if not research_parent:
            # create the page
            research_parent = RichPage(slug='research', title='Research')
            # add it under wagtail home page
            home_page = KDLWordpressReference.get_django_object(
                'home_page:home_page'
            )
            home_page.add_child(instance=research_parent)
            # add it to the registry, so it can be removed automatically
            # if needed
            KDLWordpressReference(
                wordpressid=wordpressid,
                django_object=research_parent
            ).save()

        self.objects['item_research:0'] = research_parent

    def convert_item_page(self, info):
        node = info['kdlnode']

        slug = node['wp:post_name']

        if not slug:
            print('WARNING: item without a post_name / slug')
            slug = slugify(node['title'])

        # Prepare the structure that allows teh import to update/create
        # a django object.
        ret = {
            'model': RichPage,
            # Mapping between django model fields and wordpress node content
            'data': {
                'title': node['title'],
                'slug': slug,
                'body': self.convert_body(node['content:encoded']),
            }
        }

        # First item_page becomes our home page.
        # Wagtail's different from wordpress:
        # Home page is parent of all other pages.
        if info['wordpress_parentid'] == 'item_page:0':
            home_page = self.registry.get(ALIAS_HOME_PAGE)
            if home_page:
                # Note on second import, the Home page will come here as well
                # which would mean parent of itself.
                # However 'wordpress_parentid' is ignored if the object exists.
                info['wordpress_parentid'] = ALIAS_HOME_PAGE
            else:
                info['wordpressid_alias'] = ALIAS_HOME_PAGE
                ret['model'] = HomePage

        return ret

    def convert_item_research(self, info):
        ret = self.convert_item_page(info)

        # get the research parent Page
        research_parent = self.registry.get(ALIAS_RESEARCH_PARENT)
        if not research_parent:
            # create it, under the Home Page
            home_page = self.registry.get(ALIAS_HOME_PAGE)
            research_parent = RichPage(slug='research', title='Research')
            home_page.add_child(instance=research_parent)
            # register research parent
            self.registry.set(ALIAS_RESEARCH_PARENT, research_parent)

        # all item_research should go directly under research parent
        info['wordpress_parentid'] = ALIAS_RESEARCH_PARENT

        return ret
