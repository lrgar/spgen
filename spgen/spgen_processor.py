#
# spgen_processor.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
# 

from spgen_parser import *
from collections import deque

class LexerInput:
	_BAG = {}

	def __init__(self, value):
		self._value = value

	def __repr__(self):
		return self._value

	def __lt__(self, other):
		if len(self._value) != len(other._value):
			return len(self._value) < len(other._value)
		return self._value < other._value

	def any():
		return LexerInput._generate('any-value')

	def any_digit():
		return LexerInput._generate('any-digit')

	def any_letter():
		return LexerInput._generate('any-letter')

	def char(char):
		return LexerInput._generate('\'' + char + '\'')

	def default():
		return LexerInput._generate('default')

	def _generate(name):
		if name not in LexerInput._BAG:
			LexerInput._BAG[name] = LexerInput(name)
		return LexerInput._BAG[name]

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
		starting_state = self.create_state(states)

		for key, rule in context.rules.items():
			if rule.type == RuleTypes.TOKEN:
				last_state = self.iterate(starting_state, states, rule.grammar)
				last_state.rule = rule.name

		nfa_graph = NFAGraph()
		nfa_graph.states = states
		return nfa_graph

	def iterate(self, current_state, states, grammar):
		if isinstance(grammar, GrammarConstant):
			for char in grammar.value:
				next_state = self.create_state(states)
				current_state.consume(LexerInput.char(char), next_state)
				current_state = next_state

		elif isinstance(grammar, GrammarExpressionList):
			for expr in grammar.list:
				current_state = self.iterate(current_state, states, expr)

		elif isinstance(grammar, GrammarZeroOrOne):
			out_state = self.iterate(current_state, states, grammar.expression)
			current_state.consume(LexerInput.default(), out_state)
			current_state = out_state

		elif isinstance(grammar, GrammarZeroOrMany):
			end_state = self.create_state(states)
			out_state = self.iterate(current_state, states, grammar.expression)
			out_state.consume(LexerInput.default(), current_state)
			current_state.consume(LexerInput.default(), end_state)
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
			for s in [t for i, t in queue[index].moves if i == LexerInput.default()]:
				if s not in visited:
					queue.append(s)
			index = index + 1

		return queue

	def input_closure(self, nfa_states, input_):
		closure = [t for s in nfa_states for i, t in s.moves if i == input_]
		return self.default_closure(closure)

	def get_inputs(self, nfa_states):
		return sorted(set([i for s in nfa_states for i, t in s.moves if i != LexerInput.default()]))

	def create_state(self, states):
		state = DFAState()
		state.index = len(states)
		states.append(state)
		return state

class LexerGraphGenerator:
	def generate(self, context, lexer_info):
		nfa_generator = NFAGraphGenerator()
		nfa_graph = nfa_generator.generate(context)

