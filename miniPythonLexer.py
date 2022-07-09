#!/usr/bin/env python3

import argparse
from ply import lex

# List of token names
tokens = [
    'NEW_LINE',
    'INT',
    'FLOAT',
    'STR',
    'ID',
    'POWER',
    'INT_DIVIDE',
    'LESS_EQUAL',
    'GREATER_EQUAL',
    'NOT_EQUAL',
    'EQUAL_EQUAL'
]

# List of literals
literals = [
    '+',
    '-',
    '*',
    '/',
    '%',
    '<',
    '>',
    '.',
    ',',
    ':',
    '=',
    '(',
    ')',
    '[',
    ']',
    '{',
    '}',
    '#'
]

# List of reserved names
reserved = {
    # BOOL
    'True' : 'TRUE',
    'False' : 'FALSE',
    # BOOL OPERATOR
    'and' : 'AND',
    'or' : 'OR',
    'not' : 'NOT',
    # IF
    'if' : 'IF',
    'elif' : 'ELIF',
    'else' : 'ELSE',
    # WHILE
    'while' : 'WHILE',
    # FUNCTION DEFINITION
    'def' : 'DEF',
    # CALLS
    'append' : 'APPEND',
    'extend' : 'EXTEND',
    'insert' : 'INSERT',
    'index' : 'INDEX',
    'pop' : 'POP',
    'copy' : 'COPY',
    'len' : 'LEN',
    'return' : 'RETURN',
    'print' : 'PRINT'
    }

# Add reserved names to list of tokens
tokens += list(reserved.values())

class MiniPythonLexer():
    # Ignored characters
    t_ignore = ' \t'

    # Regex rules without action code
    t_POWER = r'\*\*'
    t_INT_DIVIDE = r'//'
    t_LESS_EQUAL = r'\<='
    t_GREATER_EQUAL = r'\>='
    t_NOT_EQUAL = r'\!='
    t_EQUAL_EQUAL = r'\=='

    # Regex rules with action code
    def t_NEW_LINE(self, t):
        r'\n'
        t.lexer.lineno += len(t.value)
        return t

    def t_FALSE(self, t):
        r'False'
        t.value = False
        return t
    
    def t_TRUE(self, t):
        r'True'
        t.value = True
        return t

    def t_FLOAT(self, t):
        # Regex for floats: https://stackoverflow.com/questions/12643009/regular-expression-for-floating-point-numbers/12643073
        r'[+-]?([0-9]*)?[.][0-9]+'
        # End citation
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r'[+-]?(0|([1-9][0-9]*))'
        t.value = int(t.value)
        return t
    
    def t_STR(self, t):
        r'"[^"]*"'
        return t

    ''' Useful regex rules with action code: miniJavaLexer_solution.py from tutorial '''
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # Check for reserved words
        t.type = reserved.get(t.value, 'ID')
        return t

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
    
    def build(self, **kwargs):
        self.tokens = tokens
        self.literals = literals
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
    ''' End citation '''

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Take in the miniPython source code and perform lexical analysis.')
    parser.add_argument('FILE', help="Input file with miniPython source code")
    args = parser.parse_args()

    f = open(args.FILE, 'r')
    data = f.read()
    f.close()

    m = miniPythonLexer()
    m.build()
    m.test(data)