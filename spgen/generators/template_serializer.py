#
# template_serializer.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

"""
Template serializer library.
Based in Brevé, http://breve.twisty-industries.com/
"""

import itertools

class TagBase:
	def __init__(self):
		self._children = []

	def __repr__(self):
		return '{0} {1}'.format(self.__class__.__name__, self.__dict__)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def set_arguments(self):
		return self

	def set_children(self, children):
		self._children = children
		return self

	def serialize(self, context):
		for child in self._children:
			child.serialize(context)

	@property
	def children(self):
		return self._children

class Tag:
	def __init__(self, class_):
		self._element = class_()
		self._children = []

	def __call__(self, ** args):
		self._element.set_arguments(** args)
		return self

	def __getitem__(self, children):
		if isinstance(children, tuple):
			self._children = list(children)
		else:
			self._children = [children]
		return self

	def serialize(self, context):
		return self.flatten().serialize(context)

	def _list(self):
		return [self]

	def flatten(self):
		source = itertools.chain(* list(t._list() for t in self._children))
		items = [e.flatten() for e in source]
		if len(items) > 0:
			self._element.set_children(items)
		return self._element

class TagHandler:
	def __init__(self, class_):
		self._class = class_

	def __call__(self, ** args):
		return Tag(self._class)(** args)

	def __getitem__(self, children):
		return Tag(self._class)[children]

	def flatten(self):
		return Tag(self._class).flatten()

	def _list(self):
		return Tag(self._class)._list()

class ForEachHandler:
	def __init__(self, enumerable, function):
		self._enumerable = enumerable
		self._function = function

	def _list(self):
		return itertools.chain(* list(self._function(e)._list() for e in self._enumerable))

class SerializerContext:
	def __init__(self):
		self._output = ''
		self._indentation = 0

	def write(self, str):
		self._output += ' ' * self._indentation + str + '\n'

	def new_line(self):
		self._output += '\n'

	def indent(self):
		self._indentation += 4

	def unindent(self):
		self._indentation -= 4

	@property
	def indentation(self):
		return self._indentation

	@property
	def output(self):
		return self._output

class Serializer:
	def serialize(self, template):
		context = SerializerContext()
		template.serialize(context)
		return context.output

def for_each(enumerable, function):
	return ForEachHandler(enumerable, function)