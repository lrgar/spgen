#
# cpp_serializer.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

from generators.template_serializer import *

PUBLIC = 'public'
PRIVATE = 'private'
PROTECTED = 'protected'

class CppFile(TagBase):
	pass

class CppInclude(TagBase):
	def __init__(self):
		super().__init__()
		self._file = ''

	def set_arguments(self, file):
		self._file = file
		return self

	def serialize(self, context):
		context.write('#include {0}'.format(self._file))

	@property
	def file(self):
		return self._file

class CppNamespace(TagBase):
	def __init__(self):
		super().__init__()
		self._name = ''

	def serialize(self, context):
		context.write('namespace {0} {{'.format(self._name))
		context.indent()
		for child in self.children:
			context.serialize(child)
		context.unindent()
		context.write('}} // namespace {0}'.format(self._name))

	def set_arguments(self, name):
		self._name = name
		return self

	@property
	def name(self):
		return self._name

class CppClass(TagBase):
	def __init__(self, unit_name = 'class'):
		super().__init__()
		self._unit_name = unit_name

	def serialize(self, context):
		context.write('{0} {1} {{'.format(self._unit_name, self._name))

		private_children = [child for child in self.children if child.visibility == PRIVATE]
		if len(private_children) > 0:
			context.write('private:')
			context.indent()
			for child in private_children:
				context.serialize(child)
			context.unindent()

		public_children = [child for child in self.children if child.visibility == PUBLIC]
		if len(public_children) > 0:
			context.write('public:')
			context.indent()
			for child in public_children:
				context.serialize(child)
			context.unindent()

		protected_children = [child for child in self.children if child.visibility == PROTECTED]
		if len(protected_children) > 0:
			context.write('protected:')
			context.indent()
			for child in protected_children:
				context.serialize(child)
			context.unindent()

		context.write('}}; // class {0}'.format(self._name))
		context.new_line()

	def set_arguments(self, name, visibility = PUBLIC):
		self._name = name
		self._visibility = visibility
		return self

	@property
	def name(self):
		return self._name

	@property
	def visibility(self):
		return self._visibility


class CppStruct(CppClass):
	def __init__(self):
		super().__init__('struct')

class CppMethod(TagBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, name, return_type = 'void', arguments = [], virtual = False, visibility = PUBLIC, implemented = False, const = False):
		self._name = name
		self._visibility = visibility
		self._virtual = virtual
		self._return_type = return_type
		self._arguments = arguments
		self._implemented = implemented
		self._const = const
		return self

	def serialize(self, context):
		temp = ''
		args = ', '.join('{0} {1}'.format(t, n) for n, t in self._arguments)
		if self._virtual:
			temp = 'virtual {0} {1}({2})'.format(self._return_type, self._name, args)
		else:
			temp = '{0} {1}({2})'.format(self._return_type, self._name, args)

		if self._const:
			temp += ' const'

		if self._implemented:
			if len(self.children) == 0:
				context.write(temp + ' {}')
			else:
				context.write(temp + ' {')
				context.indent()
				for child in self.children:
					context.serialize(child)
				context.unindent()
				context.write('}')
				context.new_line()
		else:
			context.write(temp + ';')

	@property
	def name(self):
		return self._name

	@property
	def visibility(self):
		return self._visibility

	@property
	def virtual(self):
		return self._virtual

	@property
	def return_type(self):
		return self._return_type

	@property
	def arguments(self):
		return self._arguments

class CppAttribute(TagBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, name, attr_type, visibility = PUBLIC):
		self._name = name
		self._visibility = visibility
		self._attr_type = attr_type
		return self

	def serialize(self, context):
		context.write('{0} {1};'.format(self._attr_type, self._name))

	@property
	def name(self):
		return self._name

	@property
	def visibility(self):
		return self._visibility

	@property
	def attr_type(self):
		return self._attr_type

class CppEnum(TagBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, name, values, visibility = PUBLIC):
		self._name = name
		self._visibility = visibility
		self._values = values
		return self

	def serialize(self, context):
		context.write('enum {0} {{'.format(self._name))
		context.indent()
		for value in self._values[:-1]:
			context.write('{0},'.format(value))
		context.write('{0}'.format(self._values[-1]))
		context.unindent()
		context.write('}}; // enum {0}'.format(self._name))
		context.new_line()

	@property
	def name(self):
		return self._name

	@property
	def visibility(self):
		return self._visibility

	@property
	def values(self):
		return self._values


class CppConstructor(TagBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, name, arguments, visibility = PUBLIC, implemented = False, initializers = []):
		self._name = name
		self._visibility = visibility
		self._arguments = arguments
		self._implemented = implemented
		self._initializers = initializers
		return self

	def serialize(self, context):
		temp = '{0}('.format(self._name) + ', '.join('{0} {1}'.format(t, n) for n, t in self._arguments) + ')'
		if len(self._initializers) > 0:
			temp += ' : ' + ', '.join('{0}({1})'.format(n, i) for n, i in self._initializers)

		if self._implemented:
			if len(self.children) == 0:
				context.write(temp + ' {}')
			else:
				context.write(temp + ' {')
				context.indent()
				for child in self.children:
					context.serialize(child)
				context.unindent()
				context.write('}')
				context.new_line()
		else:
			context.write(temp + ';')

	@property
	def name(self):
		return self._name

	@property
	def visibility(self):
		return self._visibility

	@property
	def virtual(self):
		return self._virtual

	@property
	def return_type(self):
		return self._return_type

	@property
	def arguments(self):
		return self._arguments

cpp_file = TagHandler(CppFile)
cpp_include = TagHandler(CppInclude)
cpp_namespace = TagHandler(CppNamespace)
cpp_class = TagHandler(CppClass)
cpp_struct = TagHandler(CppStruct)
cpp_method = TagHandler(CppMethod)
cpp_attribute = TagHandler(CppAttribute)
cpp_enum = TagHandler(CppEnum)
cpp_constructor = TagHandler(CppConstructor)
