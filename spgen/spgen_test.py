#
# spgen_test.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
# 

import unittest
from spgen_parser import *
from spgen_processor import *

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

	def test_fragment_detection_1(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('fragment var : \'var\';'))
		self.assertEqual(result, True)
		self.assertEqual(fragment_info, FragmentInfo('var', GrammarConstant('var')))

	def test_fragment_detection_2(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('fragment rule : anotherRule zeroOrMany* ;'))
		self.assertEqual(result, True)
		self.assertEqual(fragment_info, FragmentInfo('rule',
			GrammarExpressionList([
				GrammarReference('anotherRule'),
				GrammarZeroOrMany(GrammarReference('zeroOrMany'))
			])))

	def test_fragment_detection_3(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('fragment var : a (;'))
		self.assertEqual(result, False)

	def test_fragment_detection_4(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('fragment var : *;'))
		self.assertEqual(result, False)

	def test_fragment_detection_5(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('fragment 4 : a (;'))
		self.assertEqual(result, False)

	def test_fragment_detection_6(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('fragment : a (;'))
		self.assertEqual(result, False)

	def test_fragment_detection_7(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('tvar : a (;'))
		self.assertEqual(result, False)

	def test_fragment_detection_8(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('fragment var : ;'))
		self.assertEqual(result, False)

	def test_fragment_detection_9(self):
		result, fragment_info = Parser().try_fragment(SourceIterator('fragment var ;'))
		self.assertEqual(result, False)

	def test_fragment_detection_10(self):
		result, fragment_info = Parser().try_fragment(SourceIterator(';'))
		self.assertEqual(result, False)

	def test_fragment_detection_11(self):
		result, fragment_info = Parser().try_fragment(SourceIterator(''))
		self.assertEqual(result, False)

	def test_free_context_1(self):
		text = """ // A comment
		           property propName     = 'propValue';
		           token tokenName       : 'constant'* andReference;
		           fragment fragmentName : 'anotherConstant' ; """
		
		context = Context()
		Parser().free_context(SourceIterator(text), context)
		
		expected = Context()
		expected.properties['propName'] = 'propValue'
		expected.rules['tokenName'] = RuleInfo(
			'tokenName', RuleTypes.TOKEN,
				GrammarExpressionList([
					GrammarZeroOrMany(GrammarConstant('constant')),
					GrammarReference('andReference')]))
		expected.rules['fragmentName'] = RuleInfo(
			'fragmentName', RuleTypes.FRAGMENT, GrammarConstant('anotherConstant'))

		self.assertEqual(context, expected)

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

def create_nfa_graph(moves, accepting_states):
	states = {}

	for u, v, i in moves:
		if u not in states:
			states[u] = NFAState()
			states[u].index = u
		if v not in states:
			states[v] = NFAState()
			states[v].index = v
		states[u].consume(i, states[v])

	for u, r in accepting_states:
		if u not in states:
			states[u] = NFAState()
			states[u].index = u
		states[u].rule = r

	graph = NFAGraph()
	graph.states = list(states.values())
	return graph

class TestLexerGenerator(unittest.TestCase):
	def test_nfa_generation_1(self):
		context = Context()
		context.rules['var'] = RuleInfo('var', RuleTypes.TOKEN, GrammarConstant('var'))
		result = NFAGraphGenerator().generate(context)

		expected = create_nfa_graph(
					moves = [
						(0, 1, LexerInput.char('v')),
						(1, 2, LexerInput.char('a')),
						(2, 3, LexerInput.char('r'))],
					accepting_states = [
						(3, 'var')])

		self.assertEqual(result, expected)

	def test_nfa_generation_2(self):
		context = Context()
		context.rules['t'] = RuleInfo('t', RuleTypes.TOKEN, GrammarZeroOrOne(GrammarConstant('var')))
		result = NFAGraphGenerator().generate(context)

		expected = create_nfa_graph(
					moves = [
						(0, 1, LexerInput.char('v')),
						(1, 2, LexerInput.char('a')),
						(2, 3, LexerInput.char('r')),
						(0, 3, LexerInput.default())],
					accepting_states = [
						(3, 't')])
		
		self.assertEqual(result, expected)

if __name__ == '__main__':
	unittest.main()
