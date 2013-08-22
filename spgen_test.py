#
# cgen_test.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
# 

# Requires Python3

import unittest
from cgen import *

class TestParser(unittest.TestCase):
	def test_eof_detection_1(self):
		result = Parser().try_eof(SourceIterator(''))
		self.assertEqual(result, True)

	def test_eof_detection_2(self):
		result = Parser().try_eof(SourceIterator('    \n\r   \t  '))
		self.assertEqual(result, True)

	def test_eof_detection_3(self):
		result = Parser().try_eof(SourceIterator('   as'))
		self.assertEqual(result, False)

	def test_comment_detection_1(self):
		result = Parser().try_comment(SourceIterator('    // adasd\n'))
		self.assertEqual(result, True)

	def test_comment_detection_2(self):
		result = Parser().try_comment(SourceIterator('    //adasd'))
		self.assertEqual(result, True)

	def test_comment_detection_3(self):
		result = Parser().try_comment(SourceIterator('//'))
		self.assertEqual(result, True)

	def test_comment_detection_4(self):
		result = Parser().try_comment(SourceIterator('/'))
		self.assertEqual(result, False)

	def test_comment_detection_5(self):
		result = Parser().try_comment(SourceIterator(' asdasd // asw \n'))
		self.assertEqual(result, False)

	def test_expect_token_1(self):
		result = Parser().expect_token(SourceIterator(' = '), '=', alphanumeric_token = False)
		self.assertEqual(result, True)

	def test_expect_token_2(self):
		result = Parser().expect_token(SourceIterator('asd'), 'asd', alphanumeric_token = True)
		self.assertEqual(result, True)

	def test_expect_token_3(self):
		result = Parser().expect_token(SourceIterator('   asd  '), 'asd', alphanumeric_token = True)
		self.assertEqual(result, True)

	def test_expect_token_4(self):
		result = Parser().expect_token(SourceIterator('asdr'), 'asd', alphanumeric_token = True)
		self.assertEqual(result, False)

	def test_expect_token_5(self):
		result = Parser().expect_token(SourceIterator('   asrd'), 'asd', alphanumeric_token = True)
		self.assertEqual(result, False)

	def test_expect_token_6(self):
		result = Parser().expect_token(SourceIterator('|=  '), '=', alphanumeric_token = False)
		self.assertEqual(result, False)

	def test_expect_token_7(self):
		result = Parser().expect_token(SourceIterator('asdr'), 'asd', alphanumeric_token = False)
		self.assertEqual(result, True)

	def test_expect_identifier_1(self):
		result = Parser().expect_identifier(SourceIterator(' Aasd32ds asd'))
		self.assertEqual(result, 'Aasd32ds')

	def test_expect_identifier_2(self):
		result = Parser().expect_identifier(SourceIterator(' 32'))
		self.assertEqual(result, None)

	def test_expect_identifier_3(self):
		result = Parser().expect_identifier(SourceIterator('!=asd'))
		self.assertEqual(result, None)

	def test_expect_identifier_4(self):
		result = Parser().expect_identifier(SourceIterator(' '))
		self.assertEqual(result, None)

	def test_expect_identifier_5(self):
		result = Parser().expect_identifier(SourceIterator(' A'))
		self.assertEqual(result, 'A')

	def test_expect_string_1(self):
		result = Parser().expect_string(SourceIterator(' Aasd32ds asd'))
		self.assertEqual(result, None)

	def test_expect_string_2(self):
		result = Parser().expect_string(SourceIterator('*asd \'fail\''))
		self.assertEqual(result, None)

	def test_expect_string_3(self):
		result = Parser().expect_string(SourceIterator(' \'asd\''))
		self.assertEqual(result, 'asd')

	def test_expect_string_4(self):
		result = Parser().expect_string(SourceIterator(''))
		self.assertEqual(result, None)

	def test_property_detection_1(self):
		result, property_info = Parser().try_property(SourceIterator('property abc = \'value\';'))
		self.assertEqual(result, True)
		self.assertEqual(property_info, PropertyInfo('abc', 'value'))

	def test_property_detection_2(self):
		result, property_info = Parser().try_property(SourceIterator('property abcds23 = \'\';'))
		self.assertEqual(result, True)
		self.assertEqual(property_info, PropertyInfo('abcds23', ''))

	def test_property_detection_3(self):
		result, property_info = Parser().try_property(SourceIterator('prop abcds23 = \'\';'))
		self.assertEqual(result, False)

	def test_property_detection_4(self):
		result, property_info = Parser().try_property(SourceIterator('property abcds23 = ;'))
		self.assertEqual(result, False)

	def test_property_detection_5(self):
		result, property_info = Parser().try_property(SourceIterator('property abcds23 = \'asd\''))
		self.assertEqual(result, False)

	def test_property_detection_6(self):
		result, property_info = Parser().try_property(SourceIterator('property abcds23 = asd;'))
		self.assertEqual(result, False)

	def test_property_detection_7(self):
		result, property_info = Parser().try_property(SourceIterator('property = asd;'))
		self.assertEqual(result, False)

	def test_property_detection_8(self):
		result, property_info = Parser().try_property(SourceIterator('abcds23 = asd;'))
		self.assertEqual(result, False)

	def test_property_detection_9(self):
		result, property_info = Parser().try_property(SourceIterator('=;'))
		self.assertEqual(result, False)

	def test_property_detection_10(self):
		result, property_info = Parser().try_property(SourceIterator(''))
		self.assertEqual(result, False)

	def test_token_detection_1(self):
		result, token_info = Parser().try_token(SourceIterator('token var : \'var\';'))
		self.assertEqual(result, True)
		self.assertEqual(token_info, TokenInfo('var', GrammarConstant('var')))

	def test_token_detection_2(self):
		result, token_info = Parser().try_token(SourceIterator('token rule : anotherRule zeroOrMany* ;'))
		self.assertEqual(result, True)
		self.assertEqual(token_info, TokenInfo('rule',
			GrammarExpressionList([
				GrammarReference('anotherRule'),
				GrammarZeroOrMany(GrammarReference('zeroOrMany'))
			])))

	def test_token_detection_3(self):
		result, token_info = Parser().try_token(SourceIterator('token var : a (;'))
		self.assertEqual(result, False)

	def test_token_detection_4(self):
		result, token_info = Parser().try_token(SourceIterator('token var : *;'))
		self.assertEqual(result, False)

	def test_token_detection_5(self):
		result, token_info = Parser().try_token(SourceIterator('token 4 : a (;'))
		self.assertEqual(result, False)

	def test_token_detection_6(self):
		result, token_info = Parser().try_token(SourceIterator('token : a (;'))
		self.assertEqual(result, False)

	def test_token_detection_7(self):
		result, token_info = Parser().try_token(SourceIterator('tvar : a (;'))
		self.assertEqual(result, False)

	def test_token_detection_8(self):
		result, token_info = Parser().try_token(SourceIterator('token var : ;'))
		self.assertEqual(result, False)

	def test_token_detection_9(self):
		result, token_info = Parser().try_token(SourceIterator('token var ;'))
		self.assertEqual(result, False)

	def test_token_detection_10(self):
		result, token_info = Parser().try_token(SourceIterator(';'))
		self.assertEqual(result, False)

	def test_token_detection_11(self):
		result, token_info = Parser().try_token(SourceIterator(''))
		self.assertEqual(result, False)

class TestTokenRuleGrammarParser(unittest.TestCase):
	def test_expect_token_grammar_constant_1(self):
		result = Parser().expect_token_grammar(SourceIterator('\'var\''))
		self.assertEqual(result, GrammarConstant('var'))

	def test_expect_token_grammar_reference_1(self):
		result = Parser().expect_token_grammar(SourceIterator('tokenId'))
		self.assertEqual(result, GrammarReference('tokenId'))

	def test_expect_token_grammar_list_1(self):
		result = Parser().expect_token_grammar(SourceIterator('\'var\' name'))
		expected = GrammarExpressionList([GrammarConstant('var'), GrammarReference('name')])
		self.assertEqual(result, expected)

	def test_expect_token_grammar_list_2(self):
		result = Parser().expect_token_grammar(SourceIterator('\'first\' \'second\''))
		expected = GrammarExpressionList([GrammarConstant('first'), GrammarConstant('second')])
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_1(self):
		result = Parser().expect_token_grammar(SourceIterator('\'a\'*'))
		expected = GrammarZeroOrMany(GrammarConstant('a'))
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_2(self):
		result = Parser().expect_token_grammar(SourceIterator('\'a\'+'))
		expected = GrammarOneOrMany(GrammarConstant('a'))
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_3(self):
		result = Parser().expect_token_grammar(SourceIterator('\'a\'?'))
		expected = GrammarZeroOrOne(GrammarConstant('a'))
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_4(self):
		result = Parser().expect_token_grammar(SourceIterator('\'a\'?bcd*'))
		expected = GrammarExpressionList([GrammarZeroOrOne(GrammarConstant('a')), GrammarZeroOrMany(GrammarReference('bcd'))])
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_5(self):
		result = Parser().expect_token_grammar(SourceIterator('\'a\'? b c d*'))
		expected = GrammarExpressionList([
			GrammarZeroOrOne(GrammarConstant('a')),
			GrammarReference('b'),
			GrammarReference('c'),
			GrammarZeroOrMany(GrammarReference('d'))
			])
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_6(self):
		result = Parser().expect_token_grammar(SourceIterator('\'a\'? (b) c (d)*'))
		expected = GrammarExpressionList([
			GrammarZeroOrOne(GrammarConstant('a')),
			GrammarReference('b'),
			GrammarReference('c'),
			GrammarZeroOrMany(GrammarReference('d'))
			])
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_7(self):
		result = Parser().expect_token_grammar(SourceIterator('\'a\'? (b c)+ d*'))
		expected = GrammarExpressionList([
			GrammarZeroOrOne(GrammarConstant('a')),
			GrammarOneOrMany(GrammarExpressionList([GrammarReference('b'), GrammarReference('c')])),
			GrammarZeroOrMany(GrammarReference('d'))
			])
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_8(self):
		result = Parser().expect_token_grammar(SourceIterator('(a*)*'))
		expected = GrammarZeroOrMany(GrammarZeroOrMany(GrammarReference('a')))
		self.assertEqual(result, expected)

	def test_expect_token_grammar_expression_9(self):
		result = Parser().expect_token_grammar(SourceIterator('(a'))
		self.assertEqual(result, None)

	def test_expect_token_grammar_expression_10(self):
		result = Parser().expect_token_grammar(SourceIterator('(a*'))
		self.assertEqual(result, None)

	def test_expect_token_grammar_expression_11(self):
		result = Parser().expect_token_grammar(SourceIterator('a*\''))
		self.assertEqual(result, GrammarZeroOrMany(GrammarReference('a')))

	def test_expect_token_grammar_expression_12(self):
		result = Parser().expect_token_grammar(SourceIterator(''))
		self.assertEqual(result, None)

	def test_expect_token_grammar_expression_13(self):
		result = Parser().expect_token_grammar(SourceIterator('()*'))
		self.assertEqual(result, None)

if __name__ == '__main__':
	unittest.main()
