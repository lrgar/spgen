#
# cpp.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

import os
import scope
import scope.lang.cpp as cpp

def generate_header_template(module_name, rules):
	return cpp.tfile [
		'#include <string>',
		'#include <vector>',
		'#include <istream>',

		cpp.tnamespace(module_name)[
			cpp.tnamespace('Parser')[
				cpp.tenum('TokenId', ['{0}Token'.format(rule) for rule in rules]),

				cpp.tclass('TokenInfo') [
					cpp.tattribute('TokenId', '_tokenId', visibility=cpp.PRIVATE),
					cpp.tattribute('std::string', '_string', visibility=cpp.PRIVATE),

					cpp.tmethod('TokenId', 'GetTokenId', const=True, visibility=cpp.PUBLIC)[
						'return _tokenId;'
					],

					cpp.tmethod('void', 'SetTokenId', ['TokenId tokenId'], visibility=cpp.PUBLIC)[
						'_tokenId = tokenId;'
					],

					cpp.tmethod('std::string', 'GetString', const=True, visibility=cpp.PUBLIC)[
						'return _string;'
					],

                    cpp.tmethod('void', 'SetString', ['std::string tokenString'], visibility=cpp.PUBLIC)[
						'_string = tokenString;'
					]
				],

				cpp.tclass('AbstractTokenListener')[
					cpp.tdtor('~AbstractTokenListener', virtual=True, visibility=cpp.PUBLIC)[
                        scope.nothing
                    ],

					scope.for_each(rules, function=
						lambda rule: cpp.tmethod('void', 'Visit{0}'.format(rule), ['const TokenInfo & info'],
                            virtual=True, visibility=cpp.PUBLIC)[
                            scope.nothing
                        ]

					),

					cpp.tmethod('void', 'BeforeToken', ['const TokenInfo & info'], virtual=True, visibility=cpp.PUBLIC)[
                        scope.nothing
                    ],

                    cpp.tmethod('void', 'AfterToken', ['const TokenInfo & info'], virtual=True, visibility=cpp.PUBLIC)[
                        scope.nothing
                    ],
				],

				cpp.tstruct(name = 'Token') [
					cpp.tattribute('TokenId', 'Id', visibility=cpp.PUBLIC),
					cpp.tattribute('std::string', 'Value', visibility=cpp.PUBLIC)
				],

				cpp.tclass('SimpleTokenReader', superclasses=[(cpp.PUBLIC, 'AbstractTokenListener')])[
					cpp.tattribute('std::vector<Token> &', '_output'),

					cpp.tctor('SimpleTokenReader', ['std::vector<Token> & output'], initialize=['_output(output)'], visibility=cpp.PUBLIC)[
                        scope.nothing
                    ],

					cpp.tmethod('void', 'AfterToken', ['const TokenInfo & info'], virtual=True, visibility=cpp.PUBLIC)[
						'Token token = { info.GetTokenId(), info.GetString() };',
						'_output.push_back(token);'
					],

					cpp.tctor('SimpleTokenReader', ['const SimpleTokenReader & other']),
					cpp.tmethod('SimpleTokenReader &', 'operator =', ['const SimpleTokenReader & other'])
				],

				cpp.tclass('LexerProcessor')[
					cpp.tctor('LexerProcessor', visibility=cpp.PUBLIC) [
                        scope.nothing
                    ],

					cpp.tmethod('void', 'Process', ['std::basic_istream<char> & input', 'AbstractTokenListener & listener'], visibility=cpp.PUBLIC)
				],
			]
		]
	]

def generate_source_template(module_name, header_file):
	return cpp.tfile [
		'#include "{0}"'.format(header_file),
		'#include <cctype>',
        'using namespace std;',

		cpp.tnamespace(module_name) [
			cpp.tnamespace('Parser') [
				cpp.tclass('LexerProcessorImpl')[
					cpp.tmethod('void', 'Process', ['basic_istream<char> & input', 'AbstractTokenListener & listener'], visibility=cpp.PUBLIC)[
						'char c;',
						'int state = 0;',
						'while (input >> c) {',
						scope.indent [
							''
						],
						'}'
					]
				],

				cpp.tmethod('void', 'LexerProcessor::Process', ['basic_istream<char> & input', 'AbstractTokenListener & listener']) [
					'LexerProcessorImpl impl;',
					'impl.Process(input, listener);'
				]
			]
		]
	]
