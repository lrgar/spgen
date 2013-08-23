#
# spgen.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
# 

# Requires Python3

"""Compiler generator script for C++."""

from spgen_parser import *

def main(args):
	parser = Parser()
	context = Context()
	#context = parser.process_file('')
	pass

if __name__ == '__main__':
	main(sys.argv[1:])
