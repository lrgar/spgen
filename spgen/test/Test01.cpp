#include "gen\Test01Parser.h"

#include <sstream>
#include <vector>

using namespace std;
using namespace Test01::Parser;

int main() {
    istringstream input("abc == def != !qwe = 324 der1");

    vector<Token> output;
    SimpleTokenReader tokenReader(output);

    LexerProcessor processor;
    processor.Process(input, tokenReader);

    return 0;
}