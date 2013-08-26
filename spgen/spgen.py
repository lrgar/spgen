#
# spgen.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

"""Compiler generator script for C++."""

import spgen_parser as parser
import spgen_processor as processor
import generators
import getopt
import sys
import importlib
import os

version = '0.1.0-alpha'

class CommandArgumentsError(Exception):
	pass

class GeneratorTaskInfo:
	def __init__(self, lexer_transition_table, properties, rules):
		self._lexer_transition_table = lexer_transition_table
		self._properties = properties
		self._rules = rules

	@property
	def lexer_transition_table(self):
		return self._lexer_transition_table

	@property
	def properties(self):
		return self._properties

	@property
	def rules(self):
		return self._rules


def generate_code(output_language, transition_table, properties, rules):
	module_name = 'generators.{0}'.format(output_language)
	generator = importlib.import_module(module_name)

	generator_info = GeneratorTaskInfo(transition_table, properties, rules)

	generator.generate_code(generator_info)

def main(args):
	try:
		grammar_file, output_language = read_arguments(args)

		context = parser.Context()
		context.properties['outputLanguage'] = output_language

		root, ext = os.path.splitext(os.path.basename(grammar_file))
		context.properties['defaultModuleName'] = root
		context.properties['grammarFilePath'] = os.path.abspath(grammar_file)
		context.properties['grammarFileName'] = os.path.basename(grammar_file)
		context.properties['outputDirectory'] = os.path.dirname(os.path.abspath(grammar_file))

		parser.Parser().process_file(grammar_file, context)
		nfa_graph = processor.NFAGraphGenerator().generate(context)
		dfa_graph = processor.DFAGraphGenerator().generate(nfa_graph)
		transition_table = processor.TransitionTableGenerator().generate(dfa_graph)

		generate_code(output_language, transition_table, context.properties, context.rules)
	except parser.ParserError as err:
		print('Parse error: {0}'.format(err.args[0]))
		sys.exit(2)

	except CommandArgumentsError as err:
		print('Error: {0}'.format(err.args[0]))
		print('')
		usage()
		sys.exit(2)

def read_arguments(args):
	grammar_file = ''
	output_language = ''

	try:
		opts, args = getopt.getopt(args, 'g:l:', [ 'grammar=lang=' ])
		for opt, arg in opts:
			if opt in ('-g', '--grammar'):
				grammar_file = arg
			elif opt in ('-l', '--lang'):
				output_language = arg
	except getopt.GetoptError as err:
		raise CommandArgumentsError(err.msg)

	if grammar_file == '' or output_language == '':
		raise CommandArgumentsError('You must specify an input grammar file and the output language.')

	return grammar_file, output_language

def usage():
	print('Usage: python spgen.py -g <input-file> -l <language>')
	print('Version: ' + version)
	print('Copyright (c) 2013 Luis Garcia')
	print('')
	print('See README for more info.')

if __name__ == '__main__':
	main(sys.argv[1:])
