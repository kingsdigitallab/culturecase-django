'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

import re
from kdl_wordpress2wagtail.management.commands.kdlwp2wt import (
    Command as KdlWp2Wt, SITE_ROOT)
from culturecase_wagtail.models import (
    StaticPage, HomePage, ResearchSummary, ResearchTag, ResearchCategoriesTree,
    ResearchCategory, ResearchSummariesTree, CategorisedSummariesPage,
    FAQsPage, QuestionAndAnswer
)
from django.utils.text import slugify

ALIAS_HOME_PAGE = 'alias:home_page'
ALIAS_RESEARCH_SUMMARIES_ROOT = 'alias:research_summaries_root'
ALIAS_RESEARCH_CATEGORIES_ROOT = 'alias:research_categories_root'
ALIAS_FAQS = 'item_avada_faq:0'


class Command(KdlWp2Wt):
    help = 'Import wordpress xml dump into wagtail'

    def initialise_registry(self):
        super(Command, self).initialise_registry()

        # create the parent page for the research_category taxonomy
        category_home = self.registry.get(ALIAS_RESEARCH_CATEGORIES_ROOT)
        if category_home is None:
            root = self.registry.get(SITE_ROOT)
            category_home = ResearchCategoriesTree(
                title='Reseach Categories',
                # DONT change this slug, it matches legacy site
                slug='research-category'
            )

            root.add_child(instance=category_home)

            self.registry.set(
                ALIAS_RESEARCH_CATEGORIES_ROOT,
                category_home,
            )

    def post_convert_item_page(self, info):
        # Move research category home under home page
        # We don't know the home page in advance, that's why we can
        # only do it here, when we are processing the HomePage.
        if isinstance(info['obj'], HomePage):
            self._set_page_location(
                self.registry.get(ALIAS_RESEARCH_CATEGORIES_ROOT),
                parentid=info['obj'].pk
            )

    def convert_item_page(self, info):
        node = info['kdlnode']

        slug = node['wp:post_name']

        if not slug:
            print('WARNING: item without a post_name / slug')
            slug = slugify(node['title'])

        # Prepare the structure that allows teh import to update/create
        # a django object.

        ret = {
            'model': StaticPage,
            # Mapping between django model fields and wordpress node content
            'data': {
                'title': node['title'],
                'slug': slug,
                'body': self.convert_body(node['content:encoded']),
                # 'sample-page' = HomePage in CC Wordpress XML, we cheat
                'show_kcl_logo': (slug in ['about', 'sample-page']),
                # Note that in WP, post_date_gmt is '0' if never been live
                # get_datetime_from_wp should return None for it
                'go_live_at': self.get_datetime_from_wp(
                    node['wp:post_date_gmt']
                ),
                'live': self.is_object_live(node)
            }
        }

        if slug == 'contents':
            ret['model'] = CategorisedSummariesPage

        if slug == 'faqs':
            ret['model'] = FAQsPage
            info['wordpressid_alias'] = ALIAS_FAQS

        # <wp:status>publish|draft</wp:status>

        # First item_page becomes our home page.
        # Wagtail's different from wordpress:
        # Home page is parent of all other pages.
        if info['wordpress_parentid'] == SITE_ROOT:
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

        target_type = metas['_menu_item_object'].replace('-', '_')

        # menu links to a reseaarch category
        if target_type == 'research_category':
            target_type = 'wp_term_' + target_type

        # menu link to a page
        if target_type == 'page':
            target_type = 'item_' + target_type

        targetid = target_type + ':' + metas['_menu_item_object_id']

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

            self._set_page_location(
                target,
                sort_order=node['wp:menu_order']
            )

        return ret

    def convert_item_research(self, info):
        ret = self.convert_item_page(info)

        node = info['kdlnode']
        metas = node.get_wp_metas()

        ret['model'] = ResearchSummary

        ret['data'].update({
            'article_title': metas['title'],
            'article_authors': metas['authors'],
            'article_year': self._clean_entry(metas, 'date', 'year'),
            'article_source': metas['source'],
            'article_url': self._clean_entry(metas, 'url', 'url'),
            'article_oaurl': self._clean_entry(metas, 'oaurl', 'url'),
            'article_email': self._clean_entry(metas, 'author-email', 'email')
        })

        # get the research parent Page
        research_parent = self.registry.get(ALIAS_RESEARCH_SUMMARIES_ROOT)
        if not research_parent:
            # create it, under the Home Page
            home_page = self.registry.get(ALIAS_HOME_PAGE)
            research_parent = ResearchSummariesTree(
                slug='research', title='Research'
            )
            home_page.add_child(instance=research_parent)
            # register research parent
            self.registry.set(ALIAS_RESEARCH_SUMMARIES_ROOT, research_parent)

        # all item_research should go directly under research parent
        info['wordpress_parentid'] = ALIAS_RESEARCH_SUMMARIES_ROOT

        return ret

    def convert_item_avada_faq(self, info):
        ret = self.convert_item_page(info)

        # turn this into a Q&A
        ret['model'] = QuestionAndAnswer

        return ret

    def post_convert_item_avada_faq(self, info):
        # retain the sort order
        node = info['kdlnode']
        self._set_page_location(
            info['obj'],
            node['wp:menu_order'],
        )

    def post_convert_item_research(self, info):
        page = info.get('obj', None)
        if not page:
            return

        self.assign_terms_to_page(
            info,
            'research-tags',
            'wp_term_research_tags',
            page,
            'tags',
        )

        self.assign_terms_to_page(
            info,
            'research-category',
            'wp_term_research_category',
            page,
            'categories',
        )

    def assign_terms_to_page(
            self, info, wp_category_domain, wordpress_type, page,
            term_field_name):
        '''
        Assign all the wordpress terms found in info to the given page.
        Only process terms from wp_category_domain (e.g. research-tags).
        wordpress_type is the type in the regsitry that matches that domain
        (e.g. wp_term_research_tags).

        (a term can be a tag or a category)

        <category domain="research-tags" nicename="children">
            <![CDATA[children]]>
        </category>

        <category domain="research-category" nicename="education">
            <![CDATA[Educational impacts of arts and culture]]>
        </category>

        <term_field_name> is the name of the model field in <page> where
        the terms will be assigned.
        '''
        node = info['kdlnode']

        tags = node.get_wp_categories(wp_category_domain)
        if tags:
            # TODO: remove all other tags
            # TODO: only save if made a change
            for tag_slug in tags:
                tag = self.registry.get(
                    '{}:{}'.format(wordpress_type, tag_slug)
                )
                getattr(page, term_field_name).add(tag)
            # that call is necessary
            page.save()

    def convert_wp_term_research_tags(self, info):
        '''
            <wp:term>
                <wp:term_id>44</wp:term_id>
                <wp:term_taxonomy>research-tags</wp:term_taxonomy>
                <wp:term_slug>education-2</wp:term_slug>
                <wp:term_parent></wp:term_parent>
                <wp:term_name><![CDATA[education]]></wp:term_name>
            </wp:term>
        '''
        node = info['kdlnode']

        ret = {
            'model': ResearchTag,
            'data': {
                'slug': info['slug'],
                'name': node['wp:term_name'],
            }
        }

        # let's use the slug as wordpressid, because that's what's used
        # in items to refer to tags
        info['wordpressid'] = info['type'] + ':' + info['slug']

        return ret

    def convert_wp_term_research_category(self, info):
        '''
            <wp:term>
                <wp:term_id>90</wp:term_id>
                <wp:term_taxonomy>research-category</wp:term_taxonomy>
                <wp:term_slug>intrinsic-impacts</wp:term_slug>
                <wp:term_parent>impacts</wp:term_parent>
                <wp:term_name><![CDATA[Intrinsic impacts of arts and culture]]>
                </wp:term_name>
                <wp:term_description><![CDATA[<b>The intrinsic []...</
            </
        '''
        node = info['kdlnode']

        ret = {
            'model': ResearchCategory,
            'data': {
                'slug': info['slug'],
                'title': node['wp:term_name'],
                'body': self.convert_body(node['wp:term_description']),
            }
        }

        if node['wp:term_parent']:
            info['wordpress_parentid'] = info['type'] + \
                ':' + node['wp:term_parent']
        else:
            info['wordpress_parentid'] = ALIAS_RESEARCH_CATEGORIES_ROOT

        # let's use the slug as wordpressid, because that's what's used
        # in items to refer to tags
        info['wordpressid_alias'] = info['type'] + ':' + info['slug']

        return ret

    def convert_body(self, body):
        ret = super(Command, self).convert_body(body)
        ret = re.sub(r'\[rev_slider home-slider-1\]', '', ret)
        return ret
