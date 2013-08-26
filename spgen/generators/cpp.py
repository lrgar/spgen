#
# spgen.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

"""C++ compiler code generator."""

import os

class Properties:
	OUTPUT_CPP_HEADER = 'outputCppHeader'
	OUTPUT_CPP_SOURCE = 'outputCppSource'
	OUTPUT_CPP_NAMESPACE = 'outputCppNamespace'
	OUTPUT_DIRECTORY = 'outputDirectory'
	DEFAULT_MODULE_NAME = 'defaultModuleName'

module_name = 'C++ code generator'

def generate_header_file(output_header_file, lexer_transition_table, rules, properties):
	with open(output_header_file, 'w') as output:
		output.write('#include <string>\n')
		output.write('\n')
		output.write('namespace {0} {{\n'.format(properties[Properties.DEFAULT_MODULE_NAME]))
		output.write('namespace Parser {\n')
		output.write('\n')
		output.write('  class LexerProcessorContext {};\n')
		output.write('\n')
		output.write('  class TokenInfo {};\n')
		output.write('\n')
		output.write('  class AbstractTokenListener {\n')
		output.write('  public:\n')

		for rule_name, info in rules.items():		
			output.write('    virtual void Visit{0}(LexerProcessorContext & context, const TokenInfo & info) {{}}\n'.format(rule_name))
		output.write('  };\n')

		output.write('\n')
		output.write('} // namespace Parser\n')
		output.write('}} // namespace {0}\n'.format(properties[Properties.DEFAULT_MODULE_NAME]))

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