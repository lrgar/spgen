#
# template_serializer.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

import unittest
from template_serializer import *

class MockClass(TagBase):
	def __init__(self):
		super().__init__()
		self._name = ''

	def set_arguments(self, name = ''):
		self._name = name
		return self

	@property
	def name(self):
		return self._name

class TestTemplateSerializer(unittest.TestCase):
	def test_tag_handler_1(self):
		tag = TagHandler(MockClass)
		template = tag(name = 'element')
		expected = MockClass().set_arguments(name = 'element')
		self.assertEqual(Serializer().flatten(template), expected)

	def test_tag_handler_2(self):
		tag = TagHandler(MockClass)
		template = tag(name = 'parent') [
				tag(name = 'child-1'),
				tag(name = 'child-2')
				]
		expected = MockClass()
		expected.set_arguments(name = 'parent')
		expected.set_children([
				MockClass().set_arguments(name = 'child-1'),
				MockClass().set_arguments(name = 'child-2')
				])

		self.assertEqual(Serializer().flatten(template), expected)

	def test_tag_handler_3(self):
		tag = TagHandler(MockClass)
		template = tag [ tag, tag ]
		expected = MockClass()
		expected.set_children([
				MockClass(),
				MockClass()
				])

		self.assertEqual(Serializer().flatten(template), expected)

	def test_tag_for_each_1(self):
		tag = TagHandler(MockClass)
		template = tag(name = 'parent') [
				for_each(range(1, 4),
					function = lambda n: tag(name = 'child-{0}'.format(n)))
				]

		expected = MockClass()
		expected.set_arguments(name = 'parent')
		expected.set_children([
				MockClass().set_arguments(name = 'child-1'),
				MockClass().set_arguments(name = 'child-2'),
				MockClass().set_arguments(name = 'child-3')
				])

		self.assertEqual(Serializer().flatten(template), expected)

	def test_tag_for_each_2(self):
		tag = TagHandler(MockClass)
		template = tag(name = 'parent') [
				for_each(range(0, 2),
					function = lambda n: for_each(range(0, 3),
						function = lambda m: tag(name = 'child-{0}'.format(n * 3 + m + 1))
						)
					)
				]

		expected = MockClass()
		expected.set_arguments(name = 'parent')
		expected.set_children([
				MockClass().set_arguments(name = 'child-1'),
				MockClass().set_arguments(name = 'child-2'),
				MockClass().set_arguments(name = 'child-3'),
				MockClass().set_arguments(name = 'child-4'),
				MockClass().set_arguments(name = 'child-5'),
				MockClass().set_arguments(name = 'child-6')
				])

		self.assertEqual(Serializer().flatten(template), expected)

if __name__ == '__main__':
	unittest.main()
