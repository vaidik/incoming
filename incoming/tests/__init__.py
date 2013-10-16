'''
    tests
    ~~~~~

    Tests for incoming.
'''

import sys
import unittest

from ..incoming import iteritems


class TestCase(unittest.TestCase):

    def assertDictEqual(self, *args, **kwargs):
        if sys.version_info >= (2, 7):
            super(TestCase, self).assertDictEqual(*args, **kwargs)

        item1 = args[0]
        item2 = args[1]

        # First compare keys
        self.assertItemsEqual(item1.keys(), item2.keys())

        for key, val in iteritems(item1):
            assert item2[key] == val

    def assertItemsEqual(self, *args, **kwargs):
        if sys.version_info == (2, 7):
            super(TestCase, self).assertItemsEqual(*args, **kwargs)

        items1 = list(args[0])
        items2 = list(args[1])
        items1.sort()
        items2.sort()

        for i in range(len(items1)):
            assert items1[i] == items2[i]
