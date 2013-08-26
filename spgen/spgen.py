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

version = '0.1.0-alpha'

class CommandArgumentsError(Exception):
	pass

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

def main(args):
	try:
		grammar_file, output_language = read_arguments(args)

		context = parser.Context()
		context.properties['outputLanguage'] = output_language
		parser.Parser().process_file(grammar_file, context)
		nfa_graph = processor.NFAGraphGenerator().generate(context)
		dfa_graph = processor.DFAGraphGenerator().generate(nfa_graph)
		transition_table = processor.TransitionTableGenerator().generate(dfa_graph)

	except parser.ParserError as err:
		print('Parse error: {0}'.format(err.args[0]))
		sys.exit(2)

	except CommandArgumentsError as err:
		print('Error: {0}'.format(err.args[0]))
		print('')
		usage()
		sys.exit(2)

if __name__ == '__main__':
	main(sys.argv[1:])
