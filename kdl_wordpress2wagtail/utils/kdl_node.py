'''
Created on 17 Feb 2018

@author: Geoffroy Noel
'''
KDL_NODE_ERROR_TAG_NOT_FOUND = 'KDL_NODE_ERROR_TAG_NOT_FOUND'


class KDLNode(object):
    '''
    Wrapper around minidom element node.
    Make it easier and more concise to get child nodes and their text content.

    e.g.
    <root>
        <y>
            <ns:x>XXX</ns:x>
        </y>
    <root>

    >>> y = KDLNode(root.getElementsByTagName('y'))
    >>> y.tag
    'y'
    >>> y['ns:x']
    'XXX'
    >>> x = y.kid('ns:x')
    >>> x.tag
    'x'
    >>> x.text()
    'XXX'

    '''

    def __init__(self, minidom_node):
        self.node = minidom_node

    @property
    def tag(self):
        return self.node.nodeName

    def __getitem__(self, tag):
        '''See .text(), but raises Exception is tag was not found.
        Please leave exception, it's useful for spotting bugs.
        [X] is used when a child element X should be there.
        Otherwise use text() with a default value.
        '''
        return self.text(tag)

    def text(self, tag=None, default=KDL_NODE_ERROR_TAG_NOT_FOUND):
        '''
        Returns the text of the first child element with tag <tag>.
        Returns <default> if no such element found.
        Raise exception if default == KDL_NODE_ERROR_TAG_NOT_FOUND and
        child not found.

        If tag == None, returns the texts under this element/node.
        '''
        if tag:
            node = self.child(tag)
        else:
            node = self.node
        if node:
            ret = get_element_text(node)
        else:
            ret = default
        if ret == KDL_NODE_ERROR_TAG_NOT_FOUND:
            raise Exception('Child not found: <{}> under <{}>'.format(
                tag,
                self.tag
            ))
        return ret

    @property
    def attributes(self):
        return dict(self.node.attributes.items())

    def kid(self, tag=None):
        ret = self.child(tag)
        if ret:
            ret = KDLNode(ret)
        return ret

    def kids(self, tag=None):
        ret = self.children(tag)
        if ret:
            ret = [KDLNode(n) for n in ret]
        return ret

    def child(self, tag=None):
        children = self.children(tag)
        if children:
            return children[0]
        return None

    def children(self, tag=None):
        if tag:
            nodes = self.node.getElementsByTagName(tag)
        else:
            nodes = self.childNodes
        return nodes

    def get_wp_categories(self, domain=None):
        '''
        Returns a dictionary with all the categories <slug>:<label> for a given
        domain name.

        <category domain="research-tags" nicename="education-2">
            <![CDATA[education]]>
        </category>

        >> get_wp_categories('research-tags')
        {
            'education-2': 'education',
        }

        '''
        return {
            n.attributes['nicename']: n.text()
            for n in self.kids('category')
            if not domain or n.attributes['domain'] == domain
        }

    def get_wp_metas(self):
        '''
        Returns a dictionary from the following children structure

        <wp:postmeta>
            <wp:meta_key>_menu_item_type</wp:meta_key>
            <wp:meta_value><![CDATA[post_type]]></wp:meta_value>
        </wp:postmeta>

        {
            '_menu_item_type': 'post_type',
        }
        '''
        return {n['wp:meta_key']: n['wp:meta_value']
                for n in self.kids('wp:postmeta')}


def get_element_text(element):
    '''Returns the text within a minidom element node'''
    rc = []
    for node in element.childNodes:
        if node.nodeType in [node.TEXT_NODE, node.CDATA_SECTION_NODE]:
            rc.append(node.data)

    return ''.join(rc)
