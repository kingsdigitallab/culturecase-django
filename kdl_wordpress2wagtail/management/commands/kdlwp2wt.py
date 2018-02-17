'''
Created on 15 Feb 2018

@author: Geoffroy Noel
'''

from ._kdlcommand import KDLCommand
from kdl_wordpress2wagtail.utils.kdl_node import KDLNode
import re
from wagtail.wagtailcore.models import Page
from culturecase_wagtail.models import RichPage, HomePage


class Command(KDLCommand):
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

        self.items = {}
        self.roots = {}

        from xml.dom import minidom

        dom = minidom.parse(xml_path)
        channel = dom.getElementsByTagName('channel')[0]

        self.items['page:0'] = Page.objects.get(id=1)

        info = {
            'nodes': {}
        }

        for child in channel.childNodes:
            child = KDLNode(child)

            res = None

            node_key = child.tag.replace(':', '_')

            handler = getattr(
                self,
                'import_' + node_key,
                None
            )
            if handler:
                res = handler(child)
                if res and hasattr(res, 'extend'):
                    node_key, res = res[0], res[1]

            # collect summary info
            if not info['nodes'].get(node_key):
                info['nodes'][node_key] = {}
            if not info['nodes'][node_key].get(repr(res)):
                info['nodes'][node_key][repr(res)] = 0
            info['nodes'][node_key][repr(res)] += 1

        self.show_import_summary(info)

        print('done')

    def import_item(self, item):
        ret = None
        node_key = 'item_' + item['wp:post_type']
        handler = getattr(self, 'import_' + node_key, None)
        if handler:
            ret = handler(item)
        return [node_key, ret]

    def import_item_page(self, item):
        # search for the page
        legacyid = item['wp:post_type'] + ':' + item['wp:post_id']
        page = RichPage.objects.filter(
            legacyid=legacyid
        ).first()

        page_key = 'NOT FOUND'

        operation = '0'

        if not page and self.action != 'delete':
            # page not found

            # search for parent
            parent = None

            # this is a trick: Wordpress Home page is at same level as other
            # top level pages, in Wagtail Home page should be above other pages
            if item['wp:post_parent'] == '0':
                parent = self.roots.get(item['wp:post_type'])

            # search for the parent
            if not parent:
                parentid = item['wp:post_type'] + ':' + item['wp:post_parent']
                parent = self.items.get(parentid)

            if not parent:
                print('WARNING: could not find parent {}'.format(parentid))
            else:
                # create dummy page under parent
                operation = 'C'
                page_type = RichPage
                if parent.pk == 1:
                    page_type = HomePage

                page = page_type(
                    legacyid=legacyid,
                    title=item['title'],
                    slug=item['wp:post_name']
                )
                parent.add_child(instance=page)

        if page:
            page_key = page.__class__.__name__ + ':' + str(page.pk)

            if self.action == 'delete':
                operation = 'D'
                page.delete()
            else:
                operation = 'U'
                if item['wp:post_parent'] == '0' and\
                        not self.roots.get(item['wp:post_type']):
                    # we force the Wordpress Home Page to be above all
                    # other pages in wagtail
                    self.roots[item['wp:post_type']] = page

                # update the page
                page.title = item['title']
                page.slug = item['wp:post_name']
                page.body = self.convert_body(item['content:encoded'])
                page.save()

                # add page to dictionary
                self.items[page.legacyid] = page

        print(
            '{:20.20} -> {:20.20} {} "{:.15}"'.
            format(
                item['wp:post_type'] + ':' + item['wp:post_id'],
                page_key,
                operation,
                item['wp:post_name'],
            )
        )

        return (page is not None)

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
        for tag, results in info['nodes'].items():
            cols.update(set(results.keys()))

        cols = sorted([str(c) for c in cols])

        # print the heading row
        s = '{:20.20}'.format('TAG NAME')
        for col in cols:
            s += '|{:>8.8}'.format(col)
        print(s)

        # print each row
        for tag in sorted(info['nodes'].keys()):
            results = info['nodes'][tag]
            s = '{:20.20}'.format(tag)
            for col in cols:
                s += '|{:8}'.format(results.get(col, 0))
            print(s)
