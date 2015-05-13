from __future__ import absolute_import, print_function
from obj2xml import XML_Object, XML_Property, XML_TextProperty


class MyExampleXML(XML_Object):
    # root
    version = XML_Property(['root', 'version'], 1.0)
    test_value = XML_Property(['root', 'test-value'], 'Default Value')
    no_default_value = XML_Property(['root', 'no-default'])

    text_node = XML_TextProperty(['root', 'text-node-1'])
    manual_text_node = XML_Property(['root', 'text-node-2', '_text'])


def run_parse_object():
    # make an object that will store our values
    class Object(object):
        pass

    obj = Object()
    obj.version = 2.0
    obj.test_value = 'Over-ridden value'
    # leave no_default_value as empty
    obj.a_text_value = 'Child1'
    obj.another_text_value = 'Child2'
    # leave obj.a_text_value as its default
    #obj.another_text_value = 'Some over-ridden text'
    obj.ignored = 'This isnt an xml property and will be ignored'

    # parse our object
    doc = MyExampleXML.from_object(obj)
    print(doc)


def run_inherited():
    obj = MyExampleXML()
    obj.test_value = 'Another value'
    obj.no_default_value = 'This value was hidden before'
    obj.a_text_value = 'Over-rode the default text'
    obj.text_node = 'This is some text'
    obj.manual_text_node = 'This is some more text'

    print(obj)


def run():
    run_parse_object()
    run_inherited()

if __name__ == '__main__':
    run()
