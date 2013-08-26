#
# spgen_processor.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
# 

from spgen_parser import *
from collections import deque
import string

def _is_digit(char):
	return char in string.digits

def _is_letter(char):
	return char in string.ascii_letters

def _is_whitespace(char):
	return char in string.whitespace

class LexerError(Exception):
	pass

class LexerInput:
	_BAG = {}

	def __init__(self, value):
		self._value = value

	def __repr__(self):
		return '{0}({1})'.format(self.__class__.__name__, self._value)

	def __lt__(self, other):
		return self._value < other._value

	def input(value):
		if isinstance(value, SpecialInput):
			special = {
				SpecialInput.ANY        : LexerInput.ANY,
				SpecialInput.DIGIT      : LexerInput.DIGIT,
				SpecialInput.NON_DIGIT  : LexerInput.NON_DIGIT,
				SpecialInput.LETTER     : LexerInput.LETTER,
				SpecialInput.NON_LETTER : LexerInput.NON_LETTER,
				SpecialInput.WHITESPACE : LexerInput.WHITESPACE }

			return special[value]
		else:
			return LexerInput.char(value)

	def char(char):
		return LexerInput._generate('Z' + char)

	def _generate(name):
		if name not in LexerInput._BAG:
			LexerInput._BAG[name] = LexerInput(name)
		return LexerInput._BAG[name]

	def _is_char(self):
		return self._value[0] == 'Z'

	def _get_char(self):
		return self._value[1]

	def match(a, b):
		# Note that this algorithm depends of the ordering of value of special tokens.

		if b < a: return LexerInput.match(b, a)

		if a != LexerInput.DEFAULT and a == b:
			return True

		if a == LexerInput.ANY:
			return True

		if a == LexerInput.DIGIT:
			if b._is_char():
				return _is_digit(b._get_char())
			elif b == LexerInput.NON_LETTER:
				return True
			return False

		if a == LexerInput.NON_DIGIT:
			if b._is_char():
				return not _is_digit(b._get_char())
			return True

		if a == LexerInput.LETTER:
			if b._is_char():
				return _is_letter(b._get_char())
			return False

		if a == LexerInput.NON_LETTER:
			if b._is_char():
				return not _is_letter(b._get_char())
			return True

		if a == LexerInput.WHITESPACE:
			if b._is_char():
				return _is_whitespace(b._get_char())

		if a._is_char() and b._is_char():
			return a == b

		# For comparing DEFAULT
		raise NotImplementedError('Input comparison not implemented between {0} and {1}.'.format(str(a), str(b)))

LexerInput.DEFAULT = LexerInput._generate('A00default')
LexerInput.ANY = LexerInput._generate('A01any')
LexerInput.DIGIT = LexerInput._generate('A02digit')
LexerInput.NON_DIGIT = LexerInput._generate('A03non-digit')
LexerInput.LETTER = LexerInput._generate('A04letter')
LexerInput.NON_LETTER = LexerInput._generate('A05non-letter')
LexerInput.WHITESPACE = LexerInput._generate('A06whitespace')

class NFAGraph:
	def __init__(self):
		self._states = []
	
	def __repr__(self):
		if len(self._states) == 0:
			return '{0} {{ 0 states }} '.format(self.__class__.__name__)
		else:
			output = ', '.join([
				'state {0} [emit \'{1}\']'.format(s.index, s.rule)
				for s in self._states if s.rule is not None
				])

			if len(output) > 0: output = ': {0}'.format(output)

			moves = [(s.index, r[1].index, r[0]) for s in self._states for r in s.moves]
			sorted(moves)

			if len(moves) > 0:
				output += '; ' + ', '.join(['({0}, {1}, {2})'.format(u, v, m) for u, v, m in moves])

			return '{0} {{ {1} states{2} }}'.format(self.__class__.__name__, len(self._states), output)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	@property
	def states(self):
	    return self._states

	@states.setter
	def states(self, value):
	    self._states = value

class NFAState:
	def __init__(self):
		self._index = None
		self._rule = None
		self._moves = []

	def __repr__(self):
		return '{0} {1}'.format(self.__class__.__name__, str(self.__dict__))

	def __eq__(self, other):
		if self._index != other._index:
			return False

		if self._rule != other._rule:
			return False

		if set([(a, s.index) for a, s in self.moves]) != set([(a, s.index) for a, s in other.moves]):
			return False

		return True

	def __hash__(self):
		return self._index

	@property
	def index(self):
		return self._index

	@index.setter
	def index(self, value):
		self._index = value

	@property
	def rule(self):
		return self._rule

	@rule.setter
	def rule(self, value):
		self._rule = value

	@property
	def moves(self):
	    return self._moves

	@moves.setter
	def moves(self, value):
	    self._moves = value

	def consume(self, acceptor, state):
		self._moves.append((acceptor, state))

class DFAGraph:
	def __init__(self):
		self._states = []
	
	def __repr__(self):
		if len(self._states) == 0:
			return '{0} {{ 0 states }} '.format(self.__class__.__name__)
		else:
			output = ', '.join([
				'state {0} [emit \'{1}\']'.format(s.index, '\', \''.join(s.rules))
				for s in self._states if len(s.rules) > 0
				])

			if len(output) > 0: output = ': {0}'.format(output)

			moves = [(s.index, r[1].index, r[0]) for s in self._states for r in s.moves]
			sorted(moves)

			if len(moves) > 0:
				output += '; ' + ', '.join(['({0}, {1}, {2})'.format(u, v, m) for u, v, m in moves])

			return '{0} {{ {1} states{2} }}'.format(self.__class__.__name__, len(self._states), output)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	@property
	def states(self):
		return self._states

	@states.setter
	def states(self, value):
		self._states = value

class DFAState:
	def __init__(self):
		self._index = None
		self._rules = []
		self._moves = []

	def __repr__(self):
		return '{0} {1}'.format(self.__class__.__name__, str(self.__dict__))

	def __eq__(self, other):
		if self._index != other._index:
			return False

		if set(self._rules) != set(other._rules):
			return False

		if set([(a, s.index) for a, s in self.moves]) != set([(a, s.index) for a, s in other.moves]):
			return False

		return True

	def __hash__(self):
		return self._index

	@property
	def index(self):
		return self._index

	@index.setter
	def index(self, value):
		self._index = value

	@property
	def rules(self):
		return self._rules

	@rules.setter
	def rules(self, value):
		self._rules = value

	@property
	def moves(self):
		return self._moves

	@moves.setter
	def moves(self, value):
		self._moves = value

	def consume(self, acceptor, state):
		self._moves.append((acceptor, state))

class NFAGraphGenerator:
	def generate(self, context):
		states = []
		start_state = self.create_state(states)

		for key, rule in context.rules.items():
			if rule.type == RuleTypes.TOKEN:
				rule_start_state = self.create_state(states)
				start_state.consume(LexerInput.DEFAULT, rule_start_state)
				last_state = self.iterate(rule_start_state, states, rule.grammar)
				last_state.rule = rule.name

		nfa_graph = NFAGraph()
		nfa_graph.states = states
		return nfa_graph

	def iterate(self, current_state, states, grammar):
		if isinstance(grammar, GrammarConstant):
			for char in grammar.value:
				next_state = self.create_state(states)
				current_state.consume(LexerInput.input(char), next_state)
				current_state = next_state

		elif isinstance(grammar, GrammarExpressionList):
			for expr in grammar.list:
				current_state = self.iterate(current_state, states, expr)

		elif isinstance(grammar, GrammarZeroOrOne):
			out_state = self.iterate(current_state, states, grammar.expression)
			current_state.consume(LexerInput.DEFAULT, out_state)
			current_state = out_state

		elif isinstance(grammar, GrammarZeroOrMany):
			end_state = self.create_state(states)
			out_state = self.iterate(current_state, states, grammar.expression)
			out_state.consume(LexerInput.DEFAULT, current_state)
			current_state.consume(LexerInput.DEFAULT, end_state)
			current_state = end_state

		elif isinstance(grammar, GrammarOneOrMany):
			current_state = self.iterate(current_state, states,
				GrammarExpressionList([
					grammar.expression,
					GrammarZeroOrMany(grammar.expression)
				]))

		else:
			raise NotImplementedError()

		return current_state

	def create_state(self, states):
		state = NFAState()
		state.index = len(states)
		states.append(state)
		return state

class DFAGraphGenerator:
	def generate(self, nfa_graph):
		states = []
		visited = {}
		nodes = []

		node = frozenset(self.default_closure([nfa_graph.states[0]]))
		nodes.append(node)
		visited[node] = self.create_state(states)
		visited[node].rules = [r.rule for r in node if r.rule != None]

		index = 0
		while index < len(nodes):
			for i in self.get_inputs(nodes[index]):
				node = frozenset(self.input_closure(nodes[index], i))
				if node not in visited:
					nodes.append(node)
					visited[node] = self.create_state(states)
					visited[node].rules = [r.rule for r in node if r.rule != None]

				visited[nodes[index]].consume(i, visited[node])
			index = index + 1

		dfa_graph = DFAGraph()
		dfa_graph.states = states
		return dfa_graph

	def default_closure(self, nfa_states):
		visited = set(nfa_states)

		queue = list(nfa_states)
		index = 0
		while index < len(queue):
			for s in [t for i, t in queue[index].moves if i == LexerInput.DEFAULT]:
				if s not in visited:
					queue.append(s)
			index = index + 1

		return queue

	def input_closure(self, nfa_states, input_):
		closure = [t for s in nfa_states for i, t in s.moves if i != LexerInput.DEFAULT and LexerInput.match(i, input_)]
		return self.default_closure(closure)

	def get_inputs(self, nfa_states):
		return sorted(set([i for s in nfa_states for i, t in s.moves if i != LexerInput.DEFAULT]))

	def create_state(self, states):
		state = DFAState()
		state.index = len(states)
		states.append(state)
		return state

class TransitionTableState:
	def __init__(self):
		self._fallbacks = []
		self._rules = []

	def __repr__(self):
		return '{0} {1}'.format(self.__class__.__name__, str(self.__dict__))

	@property
	def rules(self):
	    return self._rules

	@rules.setter
	def rules(self, value):
	    self._rules = value
	
	def on(self, char):
		for a, s in self._fallbacks:
			if LexerInput.match(a, LexerInput.char(char)):
				return s
		return None

	def fallback(self, acceptor, state):
		self._fallbacks.append((acceptor, state))

class TransitionTable:
	def __init__(self):
		self._states = []

	def __repr__(self):
		return '{0} {1}'.format(self.__class__.__name__, str(self.__dict__))

	@property
	def states(self):
		return self._states

class TransitionTableGenerator:
	def generate(self, dfa_graph):
		table = TransitionTable()

		table_states = {}	
		for u in dfa_graph.states:
			table_states[u.index] = TransitionTableState()
			table_states[u.index].rules = u.rules
			table.states.append(table_states[u.index])

		for u in dfa_graph.states:
			for a, v in u.moves:
				table_states[u.index].fallback(a, table_states[v.index])

		return table

class TransitionTableTraverser:
	def traverse(self, transition_table, text):
		start_state = transition_table.states[0]
		current_state = start_state

		output = []

		token_offset = 0
		index = 0

		last_valid_state = None
		last_valid_index = -1

		while token_offset < len(text):
			if index == len(text):
				if len(current_state.rules) > 0:
					last_valid_state = current_state
					last_valid_index = index

				if last_valid_state is not None and last_valid_index != token_offset:
					for r in last_valid_state.rules:
						output.append((token_offset, last_valid_index - token_offset, r))
					current_state = start_state
					token_offset = last_valid_index
					index = last_valid_index
					last_valid_state = None
					last_valid_index = -1
				else:
					raise LexerError('Failed to match \'{0}\' character'.format(text[index]))

			else:
				if len(current_state.rules) > 0:
					last_valid_state = current_state
					last_valid_index = index

				next_state = current_state.on(text[index])
				if next_state is None:
					if last_valid_state is not None and last_valid_index != token_offset:
						for r in last_valid_state.rules:
							output.append((token_offset, last_valid_index - token_offset, r))
						current_state = start_state
						token_offset = last_valid_index
						index = last_valid_index
						last_valid_state = None
						last_valid_index = -1
					else:
						raise LexerError('Failed to match \'{0}\' character'.format(text[index]))
				else:
					current_state = next_state
					index = index + 1

		return output
