'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

from ._kdlcommand import KDLCommand
from kdl_wordpress2wagtail.utils.kdl_node import KDLNode
import re
from wagtail.wagtailcore.models import Page
from kdl_wordpress2wagtail.models import KDLWordpressReference


class Command(KDLCommand):
    '''
    This is an abstract command.
    Please subclass it in your own app and define methods such as:

    def convert_TYPE(info):

    See convert_item_page_EXAMPLE() below for an example.

    where TYPE is a wordpress type, such as 'item_page', 'wp_term', ...

    The convert methods take data from an object described in your Wordpress
    XML dump and must return data that would allow to create a Django or
    Wagtail model from it.

    The full list of tag names can be found by running this script on
    your Wordpress XML dump and looking at the first column in the summary
    table.

    Content of info can be found in get_info_from_kdlnode()
    '''
    help = 'Import wordpress xml dump into wagtail'

    def action_info(self):
        raise Exception('Not implemented yet')
        self.action_import()

    def action_add(self):
        raise Exception('Not implemented yet')
        self.action_import()

    def action_delete(self):
        # raise Exception('Not implemented yet')
        self.action_import()

    def action_import(self):
        try:
            xml_path = self.aargs.pop(0)
        except Exception:
            return self.print_error('missing argument: XML_PATH')

        # self.objcts is a cache of all imported object
        # {'WP_TYPE:WP_ID': DJANGO_OBJECT}
        self.objects = {
            # Wordpress page root has id = 0 but not part of XML
            # and it corresponds to pre-existing wagtail sitemap root
            'item_page:0': Page.objects.get(id=1),
        }
        self.home_pageid = None

        from xml.dom import minidom

        dom = minidom.parse(xml_path)
        channel = dom.getElementsByTagName('channel')[0]

        summary = {
            'types': {}
        }

        for node in channel.childNodes:
            kdlnode = KDLNode(node)

            res = '/'

            info = self.get_info_from_kdlnode(kdlnode)

            if info['converter']:
                # pre-imported django object corresponding to that wordpress
                # object
                info['obj'] = KDLWordpressReference.get_django_object(
                    info['wordpressid']
                )

                if self.action == 'delete':
                    if info['obj']:
                        info['obj'].delete()
                        res = 'D'
                    else:
                        res = '0'
                else:
                    res = 'A'
                    if info['obj']:
                        res = 'U'

                    self.import_object(info)

                    if res == 'A':
                        if info['obj']:
                            # new object, save link between with wordpress id
                            # for the next imports
                            KDLWordpressReference(
                                wordpressid=info['wordpressid'],
                                django_object=info['obj']
                            ).save()
                        else:
                            # could not add...
                            res = 'E'

                print(
                    '{:20.20} -> {:20.20} {} "{:.15}"'.
                    format(
                        info['wordpressid'],
                        info['obj'].__class__.__name__ + ':' +
                        str(getattr(info['obj'], 'pk', '')),
                        res,
                        info['slug'],
                    )
                )

                # add page to cache
                if info['obj']:
                    self.objects[info['wordpressid']] = info['obj']

                    # First item_page becomes our home page.
                    # Wagtail's different from wordpress:
                    # Home page is parent of all other pages.
                    if info['wordpress_parentid'] == 'item_page:0':
                        self.home_pageid = info['id']

            # collect summary info
            if not summary['types'].get(info['type']):
                summary['types'][info['type']] = {}
            if not summary['types'][info['type']].get(res):
                summary['types'][info['type']][res] = 0
            summary['types'][info['type']][res] += 1

        self.show_import_summary(summary)

    def get_info_from_kdlnode(self, kdlnode):
        ''' e.g.
        <item>
            <wp:post_id>2</wp:post_id>
            <wp:post_type>page</wp:post_type>
        =>
        {'id': '2', 'type': 'item_page', 'wordpressid': 'item_page:2'}
        '''
        ret = {
            'id': '-1',
            'wordpressid': None,
            'wordpress_parentid': None,
            'type': kdlnode.tag.replace(':', '_'),
            'kdlnode': kdlnode,
            'slug': '?',
            'converter': None,
        }

        if ret['type'] == 'item':
            ret['type'] += '_' + kdlnode['wp:post_type']
            ret['id'] = kdlnode['wp:post_id']
            ret['slug'] = kdlnode['wp:post_name']
            ret['parentid'] = kdlnode['wp:post_parent']

        if ret.get('parentid'):
            if ret['type'] == 'item_page':
                # this is a trick: Wordpress Home page is at same level as
                # other top level pages, in Wagtail Home page should be above
                # other pages.
                if ret['parentid'] == '0':
                    if self.home_pageid:
                        ret['parentid'] = self.home_pageid

            ret['wordpress_parentid'] = ret['type'] + ':' + ret['parentid']

            ret['parent'] = self.objects.get(ret['wordpress_parentid'])

        ret['wordpressid'] = ret['type'] + ':' + ret['id']

        converter_name = 'convert_' + ret['type']
        ret['converter'] = getattr(self, converter_name, None)

        return ret

    def import_object(self, info):
        # search for the page
        page = info['obj']
        # node = info['kdlnode']

        model_info = info['converter'](info)

        if not page:
            # page doesn't exist yet
            if info['parentid']:
                # needs a parent
                if not info['parent']:
                    print(
                        'WARNING: could not find parent {}'.format(
                            info['parentid']))

                else:
                    # create new page under parent
                    page_type = model_info['model']
                    # create new instance
                    page = page_type(**model_info['data'])
                    # add it under the pa
                    info['parent'].add_child(instance=page)
                    # caller need to know about this new object
                    info['obj'] = page
        else:
            # update the page
            for k, v in model_info['data'].items():
                setattr(info['obj'], k, v)
            page.save()

    def convert_body(self, body):
        '''Wordpress <p> on the site is turned into line breaks in XML dump
        which, in turn, should be converted to <p> in wagtail.'''
        ret = re.sub(r'(?m)^[^<](.*)[^>]$', r'<p>\1</p>', body)

        return ret

    def show_help(self):
        ret = '''
Importing rules

  For each supported Wordpress entity (page, tag, etc.), create the equivalent
  entity in wagtail. If the entity had already been imported before, only
  update the content (so no duplicates), and preserve its location.

actions:

  import XML_PATH
    import the wordpress objects into wagtail

  delete XML_PATH
    delete wordpress objects from wagtail
        '''

        self.stdout.write(ret)

        return ret

    def show_import_summary(self, info):
        '''Summarise import in a table,
        one item type per row,
        one column per result type'''
        # find all possile result types
        print('\nSummary')
        print('-------\n')

        cols = set()
        for tag, results in info['types'].items():
            cols.update(set(results.keys()))

        cols = sorted([str(c) for c in cols])

        # print the heading row
        s = '{:20.20}'.format('TAG NAME')
        for col in cols:
            s += '|{:>8.8}'.format(col)
        print(s)
        print('-' * len(s))

        # print each row
        for tag in sorted(info['types'].keys()):
            results = info['types'][tag]
            s = '{:20.20}'.format(tag)
            for col in cols:
                s += '|{:8}'.format(results.get(col, 0))
            print(s)

#     def convert_item_page_EXAMPLE(self, info):
#         node = info['kdlnode']
#
#         ret = {
#             'model': RichPage,
#             # Mapping between django model fields and wordpress node content
#             'data': {
#                 'title': node['title'],
#                 'slug': node['wp:post_name'],
#                 'body': self.convert_body(node['content:encoded']),
#             }
#         }
#
#         # use home page
#         if info['wordpress_parentid'] == 'item_page:0':
#             ret['model'] = HomePage
#
#         return ret
