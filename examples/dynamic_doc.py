from __future__ import absolute_import, print_function
from obj2xml import XML_Object, XML_Property, XML_ListProperty, XML_TextProperty


class ChildNode(XML_Object):
    text = XML_Property(['_text'], 'Some Default Text')


class MyExampleXML(XML_Object):
    # root
    version = XML_Property(['root', 'version'], 1.0)
    test_value = XML_Property(['root', 'test-value'], 'Default Value')

    a_text_value = XML_Property(['root', 'child', '_text'], 'Some Default Text')
    another_text_value = XML_TextProperty(['root', 'child'], 'This one automatically inserts the _text node for us')

    children = XML_ListProperty(['root', 'children', 'child'], ChildNode)

    def __init__(self, **kwargs):
        super(MyExampleXML, self).__init__(**kwargs)
        self.presentations = []

    def to_dict(self):
        d = super(MyExampleXML, self).to_dict()

        # add some values ourselves
        d['root']['presentations']['presentation'] = self.presentations

        return d


def run():
    obj = MyExampleXML()
    obj.version = 2.0
    obj.presentations = [
        {'index': 0, '_text': 'Hello'},
        {'index': 1, '_text': 'World!'}
    ]
    obj.children = [
        ChildNode(text='Over-ridden child text'),
        ChildNode()
    ]
    print(obj)

if __name__ == '__main__':
    run()
