#
# spgen_parser.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
# 

# TODO: support /* ... */ comments.

import sys, copy, string
from collections import OrderedDict

class ParserException(Exception):
	pass

class PropertyInfo:
	def __init__(self, name, value):
		self._name = name
		self._value = value

	def __repr__(self):
		return '{} {}'.format(self.__class__.__name__, str(self.__dict__))

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	@property
	def name(self):
		return self._name

	@property
	def value(self):
		return self._value

class TokenInfo:
	def __init__(self, name, grammar):
		self._name = name
		self._grammar = grammar

	def __repr__(self):
		return '{} {}'.format(self.__class__.__name__, str(self.__dict__))

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	@property
	def name(self):
		return self._name

	@property
	def grammar(self):
		return self._grammar

class FragmentInfo:
	def __init__(self, name, grammar):
		self._name = name
		self._grammar = grammar

	def __repr__(self):
		return '{} {}'.format(self.__class__.__name__, str(self.__dict__))

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	@property
	def name(self):
		return self._name

	@property
	def grammar(self):
		return self._grammar

class RuleTypes:
	TOKEN = 2
	FRAGMENT = 3

class SpecialInput:
	def __init__(self, value):
		self._value = value

	def __eq__(self, other):
		return self._value == other._value

SpecialInput.ANY = SpecialInput(1)
SpecialInput.DIGIT = SpecialInput(2)
SpecialInput.NON_DIGIT = SpecialInput(3)
SpecialInput.LETTER = SpecialInput(4)
SpecialInput.NON_LETTER = SpecialInput(5)
SpecialInput.WHITESPACE = SpecialInput(6)

def recognize_input_scape(str_):
	out = []

	index = 0
	while index < len(str_):
		if str_[index] == '\\':
			index = index + 1
			special = {
				'.'  : SpecialInput.ANY,
				'd'  : SpecialInput.DIGIT,
				'D'  : SpecialInput.NON_DIGIT,
				'w'  : SpecialInput.LETTER,
				'W'  : SpecialInput.NON_LETTER,
				's'  : SpecialInput.WHITESPACE,
				't'  : '\t',
				'n'  : '\n',
				'r'  : '\r',
				'\'' : '\'',
				'\\' : '\\' }

			if str_[index] not in special:
				raise ParserException('\'\\{0}\' token not recognized.'.format(str_[index]))
			else:
				out.append(special[str_[index]])
		else:
			out.append(str_[index])

		index = index + 1
	return out

class RuleInfo:
	def __init__(self, name, rule_type, grammar):
		self._name = name
		self._type = rule_type
		self._grammar = grammar

	def __repr__(self):
		return '{} {}'.format(self.__class__.__name__, str(self.__dict__))

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	@property
	def name(self):
		return self._name

	@property
	def type(self):
		return self._type

	@property
	def grammar(self):
		return self._grammar

class Context:
	def __init__(self):
		self._properties = {}
		self._rules = OrderedDict()

	def __repr__(self):
		return '{} {}'.format(self.__class__.__name__, str(self.__dict__))

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	@property
	def properties(self):
		return self._properties

	@property
	def rules(self):
		return self._rules

class SourceIterator:
	EOF = '<end-of-file>';

	def __init__(self, text):
		self._backup_stack = []
		self._text = text
		self._current_position = 0
		self._current_column = 1
		self._current_line = 1

	def backup(self):
		self._backup_stack.append((
				self._current_position,
				self._current_column,
				self._current_line
			))

	def restore(self):
		backup = self._backup_stack.pop()
		self._current_position = backup[0]
		self._current_column = backup[1]
		self._current_line = backup[2]

	def release(self):
		self._backup_stack.pop()

	def next(self):
		if self._current_position == len(self._text):
			raise StopIteration()

		if self._text[self._current_position] == '\n':
			self._current_line = self._current_line + 1
			self._current_column = 1
		else:
			self._current_column = self._current_column + 1

		self._current_position = self._current_position + 1
		return self

	@property
	def current_item(self):
		if self._current_position == len(self._text):
			return SourceIterator.EOF
		return self._text[self._current_position]

	@property
	def current_position(self):
		return self._current_position

	@property
	def current_column(self):
		return self._current_column

	@property
	def current_line(self):
		return self._current_line

class GrammarExpression:
	def __repr__(self):
		return '{} {}'.format(self.__class__.__name__, str(self.__dict__))

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

class GrammarConstant(GrammarExpression):
	def __init__(self, value):
		self._value = value

	@property
	def value(self):
		return self._value

class GrammarExpressionList(GrammarExpression):
	def __init__(self, list_):
		self._list = list_

	@property
	def list(self):
		return self._list

class GrammarReference(GrammarExpression):
	def __init__(self, identifier):
		self._identifier = identifier

	@property
	def identifier(self):
		return self._identifier

class GrammarOneOrMany(GrammarExpression):
	def __init__(self, expression):
		self._expression = expression

	@property
	def expression(self):
		return self._expression

class GrammarZeroOrMany(GrammarExpression):
	def __init__(self, expression):
		self._expression = expression

	@property
	def expression(self):
		return self._expression

class GrammarZeroOrOne(GrammarExpression):
	def __init__(self, expression):
		self._expression = expression

	@property
	def expression(self):
		return self._expression

class Parser:
	def process_file(self, file_path, context):
		with open(input_file_path, 'r') as input_file:
			contents = input_file.read()
			self.process_text(contents, context)

	def process_text(self, contents, context):
		self.free_context(SourceIterator(contents), context)
		return context

	def free_context(self, source_iterator, context):
		while True:
			success = self.try_eof(source_iterator)
			if success: break

			success = self.try_comment(source_iterator)
			if success: continue

			success, property_info = self.try_property(source_iterator)
			if success:
				context.properties[property_info.name] = property_info.value
				continue

			success, token_info = self.try_token(source_iterator)
			if success:
				context.rules[token_info.name] = RuleInfo(token_info.name, RuleTypes.TOKEN, token_info.grammar)
				continue

			success, fragment_info = self.try_fragment(source_iterator)
			if success:
				context.rules[fragment_info.name] = RuleInfo(fragment_info.name, RuleTypes.FRAGMENT, fragment_info.grammar)
				continue

			raise ParserException(
				'Unknown token at line: {0}, column {1}.'.format(
					source_iterator.current_line,
					source_iterator.current_column))

	def try_eof(self, source_iterator):
		source_iterator.backup()
		self.skip_whitespace(source_iterator)

		if source_iterator.current_item == SourceIterator.EOF:
			source_iterator.release()
			return True
		else:
			source_iterator.restore()
			return False

	def try_comment(self, source_iterator):
		source_iterator.backup()
		self.skip_whitespace(source_iterator)

		if source_iterator.current_item == '/':
			source_iterator.next()
			if source_iterator.current_item == '/':
				while source_iterator.current_item != SourceIterator.EOF and source_iterator.current_item != '\n':
					source_iterator.next()
				source_iterator.release()
				return True

		source_iterator.restore()
		return False

	def try_property(self, source_iterator):
		source_iterator.backup()

		if self.expect_token(source_iterator, 'property', alphanumeric_token = True):
			name = self.expect_identifier(source_iterator)
			if name is not None and self.expect_token(source_iterator, '=', alphanumeric_token = False):
				value = self.expect_string(source_iterator)
				if value is not None and self.expect_token(source_iterator, ';', alphanumeric_token = False):
					source_iterator.release()
					return True, PropertyInfo(name, value)

		source_iterator.restore()
		return False, None

	def try_token(self, source_iterator):
		source_iterator.backup()

		if self.expect_token(source_iterator, 'token', alphanumeric_token = True):
			name = self.expect_identifier(source_iterator)
			if name is not None and self.expect_token(source_iterator, ':', alphanumeric_token = False):
				grammar = self.expect_token_grammar(source_iterator)
				if grammar is not None and self.expect_token(source_iterator, ';', alphanumeric_token = False):
					source_iterator.release()
					return True, TokenInfo(name, grammar)

		source_iterator.restore()
		return False, None

	def try_fragment(self, source_iterator):
		source_iterator.backup()

		if self.expect_token(source_iterator, 'fragment', alphanumeric_token = True):
			name = self.expect_identifier(source_iterator)
			if name is not None and self.expect_token(source_iterator, ':', alphanumeric_token = False):
				grammar = self.expect_token_grammar(source_iterator)
				if grammar is not None and self.expect_token(source_iterator, ';', alphanumeric_token = False):
					source_iterator.release()
					return True, FragmentInfo(name, grammar)

		source_iterator.restore()
		return False, None

	def expect_token(self, source_iterator, token, alphanumeric_token):
		source_iterator.backup()
		self.skip_whitespace(source_iterator)

		token_index = 0
		while token_index < len(token) and source_iterator.current_item == token[token_index]:
			token_index = token_index + 1
			source_iterator.next()

		valid = token_index == len(token)

		if valid and alphanumeric_token:
			if self.is_alphanumeric(source_iterator.current_item):
				valid = False

		if valid:
			source_iterator.release()
			return True
		else:
			source_iterator.restore()
			return False

	def expect_identifier(self, source_iterator):
		source_iterator.backup()
		self.skip_whitespace(source_iterator)

		identifier = ''
		if self.is_alpha(source_iterator.current_item):
			identifier += source_iterator.current_item
			source_iterator.next()
			while self.is_alphanumeric(source_iterator.current_item):
				identifier += source_iterator.current_item
				source_iterator.next()

			source_iterator.release()
			return identifier

		source_iterator.restore()
		return None

	def expect_string(self, source_iterator):
		source_iterator.backup()
		self.skip_whitespace(source_iterator)

		identifier = ''
		if source_iterator.current_item == '\'':
			source_iterator.next()
			while source_iterator.current_item != SourceIterator.EOF and source_iterator.current_item != '\'':
				identifier += source_iterator.current_item
				source_iterator.next()

			if source_iterator.current_item == '\'':
				source_iterator.next()
				source_iterator.release()
				return identifier

		source_iterator.restore()
		return None

	def expect_token_grammar(self, source_iterator):
		return self.expect_token_grammar_list(source_iterator)

	def expect_token_grammar_list(self, source_iterator):
		source_iterator.backup()

		elements = [];
		while True:
			expression = self.expect_token_grammar_expression(source_iterator)
			if expression is None: break

			elements.append(expression)

		if len(elements) == 0:
			source_iterator.restore()
			return None
		elif len(elements) == 1:
			source_iterator.release()
			return elements[0]
		else:
			source_iterator.release()
			return GrammarExpressionList(elements)

	def expect_token_grammar_expression(self, source_iterator):
		source_iterator.backup()

		result = self.expect_token_grammar_unit(source_iterator)
		if result is None:
			source_iterator.restore()
			return None

		if self.expect_token(source_iterator, '*', alphanumeric_token = False):
			source_iterator.release()
			return GrammarZeroOrMany(result)

		if self.expect_token(source_iterator, '+', alphanumeric_token = False):
			source_iterator.release()
			return GrammarOneOrMany(result)

		if self.expect_token(source_iterator, '?', alphanumeric_token = False):
			source_iterator.release()
			return GrammarZeroOrOne(result)

		source_iterator.release()
		return result

	def expect_token_grammar_unit(self, source_iterator):
		source_iterator.backup()

		result = self.expect_identifier(source_iterator)
		if result is not None:
			source_iterator.release()
			return GrammarReference(result)

		result = self.expect_string(source_iterator)
		if result is not None:
			source_iterator.release()
			return GrammarConstant(result)

		if self.expect_token(source_iterator, '(', alphanumeric_token = False):
			result = self.expect_token_grammar_list(source_iterator)
			if result is not None:
				if self.expect_token(source_iterator, ')', alphanumeric_token = False):
					return result

		source_iterator.restore()
		return None

	def skip_whitespace(self, source_iterator):
		while source_iterator.current_item in string.whitespace:
			source_iterator.next()

	def is_alphanumeric(self, character):
		return self.is_alpha(character) or character in string.digits

	def is_alpha(self, character):
		return character in string.ascii_letters
