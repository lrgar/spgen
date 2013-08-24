#
# spgen_processor.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
# 

from spgen_parser import *

class LexerInput:
	_BAG = {}

	def __init__(self, value):
		self._value = value

	def __repr__(self):
		return self._value

	def any():
		return LexerInput._generate('any')

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
		return self.__dict__ == other.__dict__

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

class NFAGraphGenerator:
	def generate(self, context):
		starting_state = NFAState()
		states = [starting_state]

		for key, rule in context.rules.items():
			if rule.type == RuleTypes.TOKEN:
				last_state = self.iterate(starting_state, states, rule.grammar)
				last_state.rule = rule.name

		index = 0
		for state in states:
			state.index = index
			index = index + 1

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

		return current_state

	def create_state(self, states):
		state = NFAState()
		states.append(state)
		return state

class LexerGraphGenerator:
	def generate(self, context, lexer_info):
		nfa_generator = NFAGraphGenerator()
		nfa_graph = nfa_generator.generate(context)

class Processor:
	def process(self, context):
		pass
