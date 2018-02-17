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
        return self.text(tag)

    def text(self, tag=None, default=KDL_NODE_ERROR_TAG_NOT_FOUND):
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


def get_element_text(element):
    '''Returns the text within a minidom element node'''
    rc = []
    for node in element.childNodes:
        if node.nodeType in [node.TEXT_NODE, node.CDATA_SECTION_NODE]:
            rc.append(node.data)

    return ''.join(rc)
