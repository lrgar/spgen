#
# cpp.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

import os
from generators.cpp_serializer import *

def generate_header_template(module_name, rules):
	return cpp_file [
		'#include <string>',
		'#include <vector>',
		'#include <istream>',

		cpp_namespace(name = module_name) [
			cpp_namespace(name = 'Parser') [
				cpp_enum(name = 'TokenId', values = ['{0}Token'.format(rule) for rule in rules]),

				cpp_class(name = 'TokenInfo') [
					cpp_attribute(name = '_tokenId', attr_type = 'TokenId', visibility = PRIVATE),
					cpp_attribute(name = '_string', attr_type = 'std::string', visibility = PRIVATE),

					cpp_method(
							visibility = PUBLIC,
							name = 'GetTokenId',
							return_type = 'TokenId',
							implemented = True,
							const = True
							) [
								'return _tokenId;'
							],

					cpp_method(
							visibility = PUBLIC,
							name = 'SetTokenId',
							implemented = True,
							arguments = [
								('tokenId', 'TokenId')
							]) [
								'_tokenId = tokenId;'
							],

					cpp_method(
							visibility = PUBLIC,
							name = 'GetString',
							return_type = 'std::string',
							implemented = True,
							const = True
							) [
								'return _string;'
							],

					cpp_method(
							visibility = PUBLIC,
							name = 'SetString',
							implemented = True,
							arguments = [
								('tokenString', 'std::string')
							]) [
								'_string = tokenString;'
							],
				],

				cpp_class(name = 'AbstractTokenListener') [
					cpp_destructor(
							visibility = PUBLIC,
							name = '~AbstractTokenListener',
							implemented = True,
							virtual = True),

					for_each(rules, function =
							lambda rule: cpp_method(
								visibility = PUBLIC,
								name = 'Visit{0}'.format(rule),
								virtual = True,
								return_type = 'void',
								implemented = True,
								arguments = [
									('info', 'const TokenInfo &')
								])
							),

					cpp_method(
							visibility = PUBLIC,
							name = 'BeforeToken',
							virtual = True,
							return_type = 'void',
							implemented = True,
							arguments = [
								('info', 'const TokenInfo &')
							]
						),

					cpp_method(
							visibility = PUBLIC,
							name = 'AfterToken',
							virtual = True,
							return_type = 'void',
							implemented = True,
							arguments = [
								('info', 'const TokenInfo &')
							]
						)
				],

				cpp_struct(name = 'Token') [
					cpp_attribute(name = 'Id', attr_type = 'TokenId', visibility = PUBLIC),
					cpp_attribute(name = 'Value', attr_type = 'std::string', visibility = PUBLIC)
				],

				cpp_class(name = 'SimpleTokenReader', inherits = [ ('AbstractTokenListener', PUBLIC) ]) [
					cpp_attribute(name = '_output', attr_type = 'std::vector<Token> &', visibility = PRIVATE),

					cpp_constructor(
							visibility = PUBLIC,
							name = 'SimpleTokenReader',
							implemented = True,
							arguments = [
								('output', 'std::vector<Token> &')
							],
							initializers = [
								('_output', 'output')
							]
						),

					cpp_constructor(
							visibility = PRIVATE,
							name = 'SimpleTokenReader',
							implemented = False,
							arguments = [
								('other', 'const SimpleTokenReader &')
							]),

					cpp_method(
							visibility = PUBLIC,
							name = 'AfterToken',
							virtual = True,
							return_type = 'void',
							implemented = True,
							arguments = [
								('info', 'const TokenInfo &')
							]) [
								'Token token = { info.GetTokenId(), info.GetString() };',
								'_output.push_back(token);'
							],

					cpp_method(
							visibility = PRIVATE,
							name = 'operator =',
							return_type = 'SimpleTokenReader &',
							implemented = False,
							arguments = [
								('other', 'const SimpleTokenReader &')
							])
				],

				cpp_class(name = 'LexerProcessor') [
					cpp_constructor(
							visibility = PUBLIC,
							name = 'LexerProcessor',
							implemented = True),

					cpp_method(
							visibility = PUBLIC,
							name = 'Process',
							return_type = 'void',
							implemented = False,
							arguments = [
								('input', 'std::basic_istream<char> &'),
								('listener', 'AbstractTokenListener &')
							])
				],
			]
		]
	]

def generate_source_template(module_name, rules, header_file):
	return cpp_file [
		'#include "{0}"'.format(header_file),

		cpp_namespace(name = module_name) [
			cpp_namespace(name = 'Parser') [
				cpp_method(
						visibility = PUBLIC,
						name = 'LexerProcessor::Process',
						virtual = True,
						return_type = 'void',
						implemented = True,
						arguments = [
								('input', 'std::basic_istream<char> &'),
								('listener', 'AbstractTokenListener &')
						]
					),
			]
		]
	]
