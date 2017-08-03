from unittest import TestCase
import json

from util.collections import CaseInsensitiveCounter


class CaseInsensitiveCounterTest(TestCase):
    def setUp(self):
        self.counter = CaseInsensitiveCounter()

    def test_stores_value(self):
        self.counter['a'] = 4
        self.assertEqual(self.counter['a'], 4)

    def test_default_0(self):
        self.assertEqual(self.counter['unassigned'], 0)

    def test_is_json_serializable(self):
        self.counter['a'] = 9
        self.assertEqual(json.dumps(self.counter), '{"a": 9}')

    def test_is_case_insensitive(self):
        self.counter['a'] = 7
        self.assertEqual(self.counter['A'], 7)

    def test_keeps_original_keys(self):
        self.counter['a'] = 1
        self.counter['B'] = 2
        self.counter['WhatEver'] = 4
        self.assertIn('a', self.counter)
        self.assertIn('B', self.counter)
        self.assertIn('WhatEver', self.counter)

    def test_does_not_iterate_implicit_keys(self):
        self.counter['x'] = 0
        self.assertIn('x', self.counter)
        self.assertNotIn('y', self.counter)

    def test_items(self):
        self.counter['bla'] = 1
        self.counter['Blub'] = 2
        self.assertIn(('bla', 1), self.counter.items())
        self.assertIn(('Blub', 2), self.counter.items())

    def test_deletes_items(self):
        self.counter['a'] = 11
        del self.counter['a']
        self.assertNotIn('a', self.counter)
        self.assertEqual(self.counter['a'], 0)

    def test_no_exception_on_delete(self):
        del self.counter['a']
        self.assertTrue(True)

    def test_equality_with_regular_dict(self):
        self.counter['a'] = 3
        self.counter['B'] = 1
        other = {'A': 3, 'b': 1}
        self.assertEqual(self.counter, other)
        self.assertEqual(other, self.counter)
