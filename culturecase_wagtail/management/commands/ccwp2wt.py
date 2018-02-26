'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

from kdl_wordpress2wagtail.management.commands.kdlwp2wt import (
    Command as KdlWp2Wt
)
from culturecase_wagtail.models import RichPage, HomePage, ResearchPage
from django.utils.text import slugify

ALIAS_HOME_PAGE = 'alias:home_page'
ALIAS_RESEARCH_PARENT = 'alias:research_parent'


class Command(KdlWp2Wt):
    help = 'Import wordpress xml dump into wagtail'

    def _pre_import(self):
        self._sort_orders = {}

    def _post_import(self):
        self._reorder_objects()

    def _reorder_objects(self):
        print('\nReorder objects\n')
        for parentid, children in self._sort_orders.items():
            sort_order = 0
            for wp_order in sorted(children.keys(), key=lambda c: int(c)):
                print(
                    wp_order,
                    children[wp_order].pk,
                    sort_order,
                    children[wp_order]
                )
                self._move_page(children[wp_order], sort_order)
                sort_order += 1

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
                'show_kcl_logo': (slug in ['about']),
                # Note that in WP, post_date_gmt is '0' if never been live
                # get_datetime_from_wp should return None for it
                'go_live_at': self.get_datetime_from_wp(
                    node['wp:post_date_gmt']
                ),
                'live': self.is_object_live(node)
            }
        }

        # <wp:status>publish|draft</wp:status>

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
                ret['data']['show_kcl_logo'] = True

        return ret

    def convert_item_nav_menu_item(self, info):
        ''' a wordpress object for a menu entry that references another object
        e.g. item_page
        We don't create a wagtail object for it, we just mark
        the referenced object as show_in_menus and reset it's sort order
        '''
        ret = None

        node = info['kdlnode']

        # get the wordpress object it refers to
        metas = node.get_wp_metas()
        targetid = 'item_' + metas['_menu_item_object'] + \
            ':' + metas['_menu_item_object_id']

        info['slug'] = node['title']

        # retrieve the corresponding wagtail object
        target = self.registry.get(targetid)
        if target:
            self.registry.set(info['wordpressid'], target, protected=True)

            ret = {
                'model': type(target),
                'data': {
                    'show_in_menus': True,
                    'short_title': node['title'],
                }
            }

            parentpk = target.get_parent().pk
            if parentpk not in self._sort_orders:
                self._sort_orders[parentpk] = {}
            self._sort_orders[parentpk][node['wp:menu_order']] = target

            # self._move_page(target, node['wp:menu_order'])

        return ret

    def convert_item_research(self, info):
        ret = self.convert_item_page(info)

        ret['model'] = ResearchPage

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

    def convert_body(self, body):
        ret = super(Command, self).convert_body(body)
        import re
        ret = re.sub(r'\[rev_slider home-slider-1\]', '', ret)
        return ret
