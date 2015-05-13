from __future__ import absolute_import, print_function
import collections
from dict2xml import dict2xml
from xml.etree.cElementTree import tostring
import xml.dom.minidom


def Tree():
    """Allows for dynamic creation of sub dictionaries when
    accessed.
    """
    return collections.defaultdict(Tree)


class XML_Property(object):
    """Descriptor class for XML properties."""
    def __init__(self, path, default=None):
        self.path = path
        self.default = default

    def __get__(self, instance, owner):
        value = getattr(instance, str(self.path), None)
        if not value:
            value = self.default
        return value

    def __set__(self, instance, value):
        setattr(instance, str(self.path), value)

    def __delete__(self, instance):
        delattr(instance, str(self.path))


class XML_PathProperty(XML_Property):
    """Automatically adds a prefix and postfix to a path.

    Useful when a lot of properties are in the same location.
    """
    prefix = []
    postfix = []

    def __init__(self, path, default=None):
        path = self.prefix + path + self.postfix
        super(XML_PathProperty, self).__init__(path, default)


class XML_TextProperty(XML_PathProperty):
    """Automatically adds ['_text'] to the end of the path"""
    postfix = ['_text']


class XML_ListProperty(XML_PathProperty):
    def __init__(self, path, cls, default=None):
        self.cls = cls
        path = self.prefix + path + self.postfix
        super(XML_PathProperty, self).__init__(path, default)

    def __set__(self, instance, value):
        if isinstance(value, list):
            setattr(instance, str(self.path), value)
        else:
            val = self.__get__(instance, instance.__class__)
            if not val:
                val = []
                setattr(instance, str(self.path), val)
            val.append(value)

    def __delete__(self, instance):
        delattr(instance, str(self.path))


class DescriptorMixin(object):
    """Mixin to enable runtime-added descriptors.
    Descriptors need to be registered during object creation.
    This provides a work around to let us dynamically add descriptors.
    Without this, any descriptors added outside the class declaration
    will be ignored.
    """
    def __getattribute__(self, name):
        attr = super(DescriptorMixin, self).__getattribute__(name)
        if hasattr(attr, "__get__") and not callable(attr):
            return attr.__get__(self, self.__class__)
        else:
            return attr

    def __setattr__(self, name, value):
        try:
            attr = super(DescriptorMixin, self).__getattribute__(name)
            return attr.__set__(self, value)
        except AttributeError:
            return super(DescriptorMixin, self).__setattr__(name, value)


class XML_Object(DescriptorMixin):
    """Generates a deep xml hierarchy from a simple flat class.

    Uses XML_Property to define values to put into the XML.
    Use unicode(obj) or str(obj) to get the string XML representation.
    """
    @classmethod
    def from_object(cls, obj, ignore_underscore=True):
        values = {}
        for k in dir(obj):
            if ignore_underscore:
                if k.startswith('_'):
                    continue
            v = getattr(obj, k)
            if callable(v):
                continue
            values[k] = v

        return cls(**values)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        """This function takes any property descriptors set on this class
        and adds them to a dict at their specified path.
        """
        tree = Tree()
        for name in dir(self):
            # we must get descriptors directly, or we'll get the value
            # they can reside inside the object, OR in the class
            # fall back to class if not present.
            try:
                prop = self.__dict__[name]
            except:
                try:
                    prop = self.__class__.__dict__[name]
                except:
                    continue

            # check if it's one of our properties
            # it must have a __get__ method and not be callable
            if not isinstance(prop, XML_Property):
                continue

            # value must be non null
            # we still need 0 values to come through
            if getattr(self, name) is None:
                continue

            # navigate to the path
            # at each path location, add a dict if one isn't present
            # but don't create a branch for the leaf
            # we can use the Tree to automatically create nodes for us
            branch = tree
            path = prop.path

            for p in path[:-1]:
                branch = branch[p]
            path = path[-1]

            # assign our value to the leaf
            value = getattr(self, name)

            # convert lists to child docs
            if isinstance(value, list):
                value = [v.to_dict() if hasattr(v, 'to_dict') else v for v in value]

            branch[path] = value

        return tree

    def to_xml(self):
        return dict2xml(self.to_dict())

    def __str__(self):
        data = self.to_xml()
        s = tostring(data, encoding='UTF-8')
        # pretty print the xml
        # http://stackoverflow.com/a/1206856/1591957
        x = xml.dom.minidom.parseString(s)
        return x.toprettyxml(indent='  ')
