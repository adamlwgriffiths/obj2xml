=======
Obj2XML
=======

Convert objects to XML quickly and easily.


Features
========

* Easily convert objects using an XML template.
* Supports node lists and sub-documents.
* Objects don't need to know about XML paths, flat objects can become deep XML documents.
* Dynamically inject XML at creation time.


Examples
========

Simple document::

from obj2xml import XML_Object, XML_Property, XML_TextProperty


    class MyExampleXML(XML_Object):
        version = XML_Property(['root', 'version'], 1.0)
        test_value = XML_Property(['root', 'test-value'], 'Default Value')
        no_default_value = XML_Property(['root', 'no-default'])

        text_node = XML_TextProperty(['root', 'text-node-1'])
        manual_text_node = XML_Property(['root', 'text-node-2', '_text'])

    obj = MyExampleXML()
    obj.test_value = 'Another value'
    obj.no_default_value = 'This value was hidden before'
    obj.a_text_value = 'Over-rode the default text'
    obj.text_node = 'This is some text'
    obj.manual_text_node = 'This is some more text'

    print(obj)

    <?xml version="1.0" ?>
    <root no-default="This value was hidden before" test-value="Another value" version="1.0">
      <text-node-2>This is some more text</text-node-2>
      <text-node-1>This is some text</text-node-1>
    </root>


For further examples, look in the `examples` directory.


Dependencies
============

* `pydict2xml <https://github.com/delfick/python-dict2xml>`_


Authors
=======

* `Adam Griffiths <https://github.com/adamlwgriffiths>`_

