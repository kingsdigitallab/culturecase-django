'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

from ._kdlcommand import KDLCommand
from kdl_wordpress2wagtail.utils.kdl_node import KDLNode
import re
from wagtail.wagtailcore.models import Page
from time import strptime
import pytz


class Command(KDLCommand):
    '''
    This is an abstract command to import Wordpress objects into
    Wagtail/Django.

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

    You can also override set_predefined_objects() to declare pre-existing
    or hard-coded django/wagtail objects that will serve as parents for the
    imported wordpress objects.
    '''
    help = 'Import wordpress xml dump into wagtail'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.summary = {
            'types': {}
        }
        from kdl_wordpress2wagtail.models import KDLWordpressReference
        self.registry = KDLWordpressReference

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--filter', help='Filter the object types, e.g.'
                            'item_page*;wp_term:145')

    def is_filtered_in(self, objectid):
        ret = True

        if self.options['filter']:
            afilter = self.options['filter'].replace(
                '*', '.*').replace(';', '|')
            if afilter:
                ret = re.match(r'^({})$'.format(afilter), objectid)

        return ret

    def action_add(self):
        raise Exception('Not implemented yet')
        self.action_import()

    def action_imported(self):
        self.parse_registry(action='imported')

    def action_delete(self):
        self.parse_registry(action='delete')

    def parse_registry(self, action='delete'):

        for reference in self.registry.objects.all():
            operation = '/'

            info = {
                'type': reference.wordpressid.split(':')[0],
                'wordpressid': reference.wordpressid,
                'wordpress_parentid': None,
                'obj': reference.django_object,
                'slug': getattr(reference.django_object, 'slug', '?'),
            }

            if action == 'delete':
                if reference.django_object:
                    operation = '/'
                    if not reference.protected:
                        reference.django_object.delete()
                        operation = 'D'
                else:
                    operation = '0'

                reference.delete()

            self.show_operation(info, operation)

            self.add_to_summary(info, operation)

        self.show_import_summary()

    def initialise_registry(self):
        '''
        Declare a pre-existing mapping between worpdress objects and
        django objects.

        You can OVERRIDE this method to declare your own django objects.
        For instance if all item_X should be imported under the same wagtail
        Page, then you can create that Page in this method (if it doesn't
        exist yet) and give it its wordpressid: {'item_X:0': wagtail_page}.

        self.objects is a cache/registry of all imported object
        {'WP_TYPE:WP_ID': DJANGO_OBJECT}

        It is mostly used to quickly find parent pages by their wordpress id.
        '''

        # Wordpress page root has id = 0 but not part of XML
        # and it corresponds to pre-existing wagtail sitemap root.
        self.registry.set('item_page:0', Page.objects.get(id=1), True)

    def action_import(self):
        try:
            xml_path = self.aargs.pop(0)
        except Exception:
            return self.print_error('missing argument: XML_PATH')

        self.initialise_registry()

        from xml.dom import minidom

        dom = minidom.parse(xml_path)
        channel = dom.getElementsByTagName('channel')[0]

        self._pre_import()

        for node in channel.childNodes:
            kdlnode = KDLNode(node)

            res = '/'

            info = self.get_info_from_kdlnode(kdlnode)

            if info['converter'] and self.is_filtered_in(info['wordpressid']):
                res = self.import_object(info)

                self.show_operation(info, res)

            self.add_to_summary(info, res)

        self._post_import()

        self.show_import_summary()

    def _pre_import(self):
        pass

    def _post_import(self):
        pass

    def get_info_from_kdlnode(self, kdlnode):
        ''' e.g.
        <item>
            <wp:post_id>2</wp:post_id>
            <wp:post_type>page</wp:post_type>
        =>
        {'id': '2', 'type': 'item_page', 'wordpressid': 'item_page:2'}
        '''
        ret = {
            # the id of the object, exactly as found in Wordpress XML
            'id': '-1',
            # a made up key identifying the object, e.g. 'item_page:17'
            'wordpressid': None,

            # a made up key identifying the parent object,
            # same format as wordpressid
            # e.g. 'item_page:5'
            'wordpress_parentid': None,

            # a type expanded from Wordpress node type,
            # e.g. <wp:item><wp:post_type>page</wp:post_type>[...]
            # => 'item_page'
            'type': kdlnode.tag.replace(':', '_'),
            # the XML node
            'kdlnode': kdlnode,
            # slug, if any
            'slug': '?',
            # the method that will convert the WP object to Django object
            'converter': None,
        }

        # Only populate this if we want the object to be placed under a
        # particular parent in Django.
        # It will be used to construct wordpress_parentid.
        parentid = None

        # subdivide the term nodes by taxonomy
        if ret['type'] == 'wp_term':
            ret['id'] = kdlnode['wp:term_id']
            ret['slug'] = kdlnode['wp:term_slug']
            parentid = kdlnode.text('wp:term_parent', None)
            ret['type'] += '_' + kdlnode['wp:term_taxonomy']

            # Wordpress is not consistent, wp:term_id is a unique number
            # but wp:term_parent is the slug of the parent.
            # That's different from wordpress items (e.g. page).
            self.term_ids_slug = getattr(self, 'term_ids_slug', {})
            self.term_ids_slug[ret['id']] = ret['slug']
            if parentid:
                parentid = self.term_ids_slug.get(
                    parentid,
                    'NOT FOUND'
                )

        # subdivide the item nodes by types
        if ret['type'] == 'item':
            ret['id'] = kdlnode['wp:post_id']
            ret['slug'] = kdlnode['wp:post_name']
            parentid = kdlnode['wp:post_parent']
            ret['type'] += '_' + kdlnode['wp:post_type']

        # resolve the parent
        if parentid:
            ret['wordpress_parentid'] = ret['type'] + ':' + parentid

        ret['wordpressid'] = ret['type'] + ':' + ret['id']

        converter_name = 'convert_' + ret['type']
        ret['converter'] = getattr(self, converter_name, None)

        return ret

    def import_object(self, info):
        '''
        Import a single Wordpress object into Django:
        - convert the WP object into Django data
        - create or update the django object in the database
        - attach to parent object if needed
        - add WP -> Django Object link to the registry
        - updates info['obj'] = django_object
        - returns an operation code (C|U|E|?)
        '''

        ret = '?'

        # node = info['kdlnode']

        model_info = info['converter'](info)
        if model_info is None:
            return '0'

        django_object = self.registry.get(info['wordpressid'])

        if not django_object:
            ret = 'C'
            # django object doesn't exist yet
            parent = None

            if info['wordpress_parentid']:
                parent = self.registry.get(info['wordpress_parentid'])

                # needs a parent
                if not parent:
                    print(
                        'WARNING: could not find parent {}'.format(
                            info['wordpress_parentid']
                        )
                    )
                    return 'E'

            # create new django object under parent
            AModel = model_info['model']
            # create new instance
            django_object = AModel(**model_info['data'])

            if parent:
                # add it under the parent
                parent.add_child(instance=django_object)
            else:
                django_object.save()

            # add to registry
            self.registry.set(info['wordpressid'], django_object)

            wordpressid_alias = info.get('wordpressid_alias')
            if wordpressid_alias:
                self.registry.set(wordpressid_alias, django_object)
        else:
            ret = 'U'

            # update the django object
            for k, v in model_info['data'].items():
                setattr(django_object, k, v)

            django_object.save()

        # caller need to know about this object
        info['obj'] = django_object

        return ret

    def show_operation(self, info, operation):
        # print the info
        obj_desc = 'None'
        if info.get('obj'):
            obj_desc = info['obj'].__class__.__name__ + \
                ':' + str(getattr(info['obj'], 'pk', ''))

        print(
            '{:25.25} -> {:20.20} {} "{:.15}"'.
            format(
                info['wordpressid'],
                obj_desc,
                operation,
                info['slug'],
            )
        )

    def add_to_summary(self, info, operation):
        # add operation to the summary
        if not self.summary['types'].get(info['type']):
            self.summary['types'][info['type']] = {}
        if not self.summary['types'][info['type']].get(operation):
            self.summary['types'][info['type']][operation] = 0
        self.summary['types'][info['type']][operation] += 1

    def convert_body(self, body):
        '''Wordpress <p> on the site is turned into line breaks in XML dump
        which, in turn, should be converted to <p> in wagtail.'''
        ret = re.sub(r'(?m)^([^<].*[^>])$', r'<p>\1</p>', body)

        return ret

    def _move_page(self, page, index=0):
        # GN: copied from wagtail Page.move(), shame their method is not
        # reusable without passing a request.
        page_to_move = page
        parent_page = page_to_move.get_parent()

        # Get position parameter
        position = index

        # Find page thats already in this position
        position_page = None
        if position is not None:
            try:
                position_page = parent_page.get_children()[int(position)]
            except IndexError:
                pass  # No page in this position

        # Move page

        # any invalid moves *should* be caught by the permission check above,
        # so don't bother to catch InvalidMoveToDescendant

        if position_page:
            # If the page has been moved to the right, insert it to the
            # right. If left, then left.
            old_position = [
                p.pk for p in parent_page.get_children()].index(
                page_to_move.pk)
            if int(position) < old_position:
                page_to_move.move(position_page, pos='left')
            elif int(position) > old_position:
                page_to_move.move(position_page, pos='right')
        else:
            # Move page to end
            page_to_move.move(parent_page, pos='last-child')

    def show_import_summary(self):
        '''Summarise import in a table,
        one item type per row,
        one column per result type'''

        info = self.summary

        # find all possile result types
        print('')
        print('Created, Updated, Deleted, Error, / nothing done, '
              '0 not found')
        print('')
        print('Summary')
        print('-------')
        print('')

        cols = set()
        for tag, results in info['types'].items():
            cols.update(set(results.keys()))

        cols = sorted([str(c) for c in cols])

        # print the heading row
        s = '{:30.30}'.format('TAG NAME')
        for col in cols:
            s += '|{:>8.8}'.format(col)
        print(s)
        print('-' * len(s))

        # print each row
        for tag in sorted(info['types'].keys()):
            results = info['types'][tag]
            s = '{:30.30}'.format(tag)
            for col in cols:
                s += '|{:8}'.format(results.get(col, 0))
            print(s)

        print('')

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

    def get_datetime_from_wp(self, datestr):
        '''Return a datetime object from a Wordpress date string
        Return None if not valid or 0000-00-00

        Two possible formats:

        a)
        <pubDate>Tue, 03 Dec 2013 08:50:50 +0000</pubDate>

        b)
        <wp:post_date>2018-01-05 16:22:58</wp:post_date>
        <wp:post_date_gmt>0000-00-00 00:00:00</wp:post_date_gmt>

        * pubDate / post_date_gmt is isually '0' if post has never been
           published
        * otherwise post_date and post_date_gmt should be the same
        * pubDate = post_date?

        '''
        ret = None

        from datetime import datetime
        try:
            ret = datetime(
                *(strptime(datestr, '%Y-%m-%d %H:%M:%S')[0:6]),
                tzinfo=pytz.utc
            )
        except ValueError:
            pass

        return ret

    def is_object_live(self, kdlnode):
        ret = kdlnode['wp:status'] == 'publish'
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

  delete
    delete wordpress objects from wagtail

  imported
    show all imported objects
        '''

        self.stdout.write(ret)

        return ret
