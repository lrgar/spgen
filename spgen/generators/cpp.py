#
# cpp.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

"""C++ compiler code generator."""

import os
from generators.cpp_serializer import *
import generators.cpp_templates
import spgen_parser

class Properties:
	OUTPUT_CPP_HEADER = 'outputCppHeader'
	OUTPUT_CPP_SOURCE = 'outputCppSource'
	OUTPUT_CPP_NAMESPACE = 'outputCppNamespace'
	OUTPUT_DIRECTORY = 'outputDirectory'
	DEFAULT_MODULE_NAME = 'defaultModuleName'

module_name = 'C++ code generator'

def generate_header_file(output_header_file, lexer_transition_table, rules, properties):
	template = generators.cpp_templates.generate_header_template(
		module_name = properties[Properties.DEFAULT_MODULE_NAME],
		rules = [r for r, v in rules.items() if v.type == spgen_parser.RuleTypes.TOKEN]
		)

	serializer = Serializer()
	output = serializer.serialize(template)

	with open(output_header_file, 'w') as f:
		f.write(output)

def generate_source_file(output_source_file, header_file, lexer_transition_table, rules, properties):
	template = generators.cpp_templates.generate_source_template(
		module_name = properties[Properties.DEFAULT_MODULE_NAME],
		header_file = header_file
	)

	serializer = Serializer()
	output = serializer.serialize(template)

	with open(output_source_file, 'w') as f:
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

	output_source_file = os.path.normpath(os.path.join(
		os.getcwd(),
		info.properties[Properties.OUTPUT_DIRECTORY],
		info.properties[Properties.OUTPUT_CPP_SOURCE]))

	generate_header_file(
		output_header_file,
		info.lexer_transition_table,
		info.rules,
		info.properties)

	generate_source_file(
		output_source_file,
		info.properties[Properties.OUTPUT_CPP_HEADER],
		info.lexer_transition_table,
		info.rules,
		info.properties)
