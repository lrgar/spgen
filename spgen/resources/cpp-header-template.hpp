//
// language-parser.hpp
//
// Copyright (c) 2013 Luis Garcia.
// This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
//

#include <string>

namespace ModuleName {
	namespace Parser {
		class LexerProcessorContext {
		};

		class TokenInfo {
		};

		class AbstractTokenListener {
		public:
			virtual void VisitVar(LexerProcessorContext & context, const TokenInfo & info) {}
			virtual void VisitIdentifier(LexerProcessorContext & context, const TokenInfo & info) {}
			// ...
		};

		class LexerProcessor {
		public:
			inline void Process(AbstractTokenListener & tokenListener) {
				// TODO
			}
		};

		class LexerProcessorBuilder {
			std::string _filePath;
			std::string _text;
			int _mode;

			static const int _FILE_MODE = 0;
			static const int _TEXT_MODE = 1;
			static const int _UNDEFINED_MODE = 2;

		public:
			inline ProcessorBuilder() : _mode(_UNDEFINED_MODE) {}

			inline LexerProcessorBuilder & SetSourceFile(const std::string & filePath) {
				_filePath = filePath;
				_mode = _FILE_MODE;
			}

			inline LexerProcessorBuilder & SetSourceFile(std::string && filePath) {
				_filePath = filePath;
				_mode = _FILE_MODE;
			}

			inline LexerProcessorBuilder & SetSourceText(const std::string & text) {
				_text = text;
				_mode = _TEXT_MODE;
			}

			inline LexerProcessorBuilder & SetSourceText(std::string && text) {
				_text = text;
				_mode = _TEXT_MODE;
			}

			inline LexerProcessor * Build() const {
				// TODO
			}
		};
	} // namespace Parser
} // namespace ModuleName