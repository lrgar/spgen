#
# cpp.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

"""C++ compiler code generator."""

import os
from generators.cpp_serializer import *

class Properties:
	OUTPUT_CPP_HEADER = 'outputCppHeader'
	OUTPUT_CPP_SOURCE = 'outputCppSource'
	OUTPUT_CPP_NAMESPACE = 'outputCppNamespace'
	OUTPUT_DIRECTORY = 'outputDirectory'
	DEFAULT_MODULE_NAME = 'defaultModuleName'

module_name = 'C++ code generator'

def generate_header_file(output_header_file, lexer_transition_table, rules, properties):
	template = cpp_file [
		cpp_include(file = '<string>'),

		cpp_namespace(name = properties[Properties.DEFAULT_MODULE_NAME]) [
			cpp_namespace(name = 'Parser') [
				cpp_class(name = 'LexerProcessorContext'),
				cpp_class(name = 'TokenInfo'),
				cpp_class(name = 'AbstractTokenListener') [
					for_each(rules, function =
						lambda rule: cpp_method(
							visibility = PUBLIC,
							name = 'Visit{0}'.format(rule),
							virtual = True,
							return_type = 'void',
							implemented = True,
							arguments = [
								('context', 'LexerProcessorContext &'),
								('info', 'const TokenInfo &')
							])
						)
				]
			]
		]
	]

	serializer = Serializer()
	output = serializer.serialize(template)

	with open(output_header_file, 'w') as f:
		f.write(output)

def generate_code(info):
	if Properties.OUTPUT_CPP_SOURCE not in info.properties:
		info.properties[Properties.OUTPUT_CPP_SOURCE] = '{0}Parser.cpp'.format(info.properties[Properties.DEFAULT_MODULE_NAME])

	if Properties.OUTPUT_CPP_HEADER not in info.properties:
		info.properties[Properties.OUTPUT_CPP_HEADER] = '{0}Parser.h'.format(info.properties[Properties.DEFAULT_MODULE_NAME])

	if Properties.OUTPUT_CPP_NAMESPACE not in info.properties:
		info.properties[Properties.OUTPUT_CPP_NAMESPACE] = '{0}.Parser'.format(info.properties[Properties.DEFAULT_MODULE_NAME])

	print('Properties:')
	for name, value in sorted(info.properties.items()):
		print('    {0}: {1}'.format(name, value))

	output_header_file = os.path.normpath(os.path.join(
		os.getcwd(),
		info.properties[Properties.OUTPUT_DIRECTORY],
		info.properties[Properties.OUTPUT_CPP_HEADER]))

	generate_header_file(
		output_header_file,
		info.lexer_transition_table,
		info.rules,
		info.properties)
