import abc
from unittest import TestCase
from pynetsym import metautil

__author__ = 'enrico'


class A(object):
    def foo(self):
        pass

    def bar(self):
        pass


class C(object):
    def a(self):
        pass

    def b(self):
        pass


class D(A, C):
    pass


class TestExtract_interface(TestCase):
    def test_extract_all_methods(self):
        @metautil.abstract_interface_from(D)
        class E(object):
            __metaclass__ = abc.ABCMeta
            pass
        self.assert_(set(dir(D)).issubset(dir(E)))

    def test_no_metaclass(self):
            class E(object):
                pass
            self.assertRaises(TypeError,
                    metautil.abstract_interface_from(D), E)

    def test_methods(self):
        @metautil.abstract_interface_from(D)
        class E(object):
            __metaclass__ = abc.ABCMeta
            pass
        self.assertRaises(TypeError, E)
