#!/usr/bin/env python3

import argparse
from ply import yacc
from miniPythonLexer import MiniPythonLexer
from miniPythonLexer import tokens
import miniPythonAST as ast

class MiniPythonParser:
    debug_messages = False

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('left', '<', 'LESS_EQUAL', '>', 'GREATER_EQUAL', 'NOT_EQUAL', 'EQUAL_EQUAL'),
        ('left','+', '-'),
        ('left', '*', '/',  'INT_DIVIDE', '%'),
        ('left', 'POWER'),
        ('right', 'UPLUS', 'UMINUS'),
    )

    start = 'program'

    def p_program(self, p):
        '''
        program : code_lines
                | optional_new_lines code_lines
        '''
        self.debug("DEBUG", "program")
        if len(p) == 2:
            p[0] = ast.Program(p[1], p.lineno(1))
        else:
            p[0] = ast.Program(p[2], p.lineno(2))

    def p_code_lines(self, p):
        '''
        code_lines : code_line
                   | code_line new_lines
                   | code_line new_lines code_lines
                   | code_line optional_new_lines code_lines
        '''
        if len(p) < 4:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_code_line(self, p):
        '''
        code_line : function_def
                  | statement
                  | expr
        '''
        self.debug("DEBUG", "code_line")
        p[0] = ast.CodeLine(p[1], p.lineno(1))

    def p_block(self, p):
        '''
        block : ':' new_lines optional_new_lines code_lines '#' new_lines
              | ':' new_lines optional_new_lines code_lines '#'
        '''
        self.debug("DEBUG", "block")
        p[0] = p[4]

    def p_optional_new_lines(self, p):
        '''
        optional_new_lines : new_lines
                           | empty
        '''
        self.debug("DEBUG", "optional_new_lines")
        p[0] = None

    def p_new_lines(self, p):
        '''
        new_lines : NEW_LINE
                  | NEW_LINE new_lines
        '''
        self.debug("DEBUG", "new_lines")
        p[0] = None

    def p_statement(self, p):
        '''
        statement : assignment_statement
                  | if_statement 
                  | while_statement
                  | return_statement
                  | print_statement
        '''
        self.debug("DEBUG", "statement")
        p[0] = p[1]

    def p_assignment_statement(self, p):
        '''
        assignment_statement : ID '=' expr
        '''
        self.debug("DEBUG", "assignment_statement")
        p[0] = ast.AssignmentStatement(p[1], p[3], p.lineno(1))

    def p_params(self, p):
        '''
        params : expr
               | expr ',' params
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_params_or_empty(self, p):
        '''
        params_or_empty : params
                        | empty
        '''
        p[0] = ast.ParamsList(p[1], p.lineno(1))

    def p_function_def(self, p):
        '''
        function_def : DEF ID '(' params_or_empty ')' block
        '''
        self.debug("DEBUG", "function_def")
        p[0] = ast.FunctionDef(p[2], p[6], p[4], p.lineno(1))

    def p_if_statement(self, p):
        '''
        if_statement : IF expr block
                     | IF expr block elif_statements
                     | IF expr block ELSE block
                     | IF expr block elif_statements ELSE block
        '''
        self.debug("DEBUG", "if_statement")
        if len(p) == 4:
            p[0] = ast.IfStatement(p[2], p[3], None, None, p.lineno(1))
        elif len(p) == 5:
            p[0] = ast.IfStatement(p[2], p[3], p[4], None, p.lineno(1))
        elif len(p) == 6:
            p[0] = ast.IfStatement(p[2], p[3], None, p[5], p.lineno(1))
        else:
            p[0] = ast.IfStatement(p[2], p[3], p[4], p[6], p.lineno(1))

    def p_elif_statements(self, p):
        '''
        elif_statements : ELIF expr block
                        | ELIF expr block elif_statements
        '''
        self.debug("DEBUG", "else_statement")
        if len(p) == 4:
            p[0] = ast.ElifStatement(p[2], p[3], None, p.lineno(1))
        else:
            p[0] = ast.ElifStatement(p[2], p[3], p[4], p.lineno(1))

    def p_while_statement(self, p):
        '''
        while_statement : WHILE expr block
        '''
        p[0] = ast.WhileStatement(p[2], p[3], p.lineno(1))

    def p_return_statement(self, p):
        '''
        return_statement : RETURN expr
                         | RETURN
        '''
        self.debug("DEBUG", "return_statement")
        if len(p) == 3:
            p[0] = ast.ReturnStatement(p[2], p.lineno(1))
        else:
            p[0] = ast.ReturnStatement(None, p.lineno(1))

    def p_print_statement(self, p):
        '''
        print_statement : PRINT '(' expr ')'
                        | PRINT '(' ')'
        '''
        self.debug("DEBUG", "print_statement")
        if len(p) == 4:
            p[0] = ast.PrintStatement(None, p.lineno(1))
        else:
            p[0] = ast.PrintStatement(p[3], p.lineno(1))

    def p_expr_id(self, p):
        '''
        expr : ID
        '''
        self.debug("DEBUG", "expr_id", p[1])
        p[0] = ast.ID(p[1], p.lineno(1))

    def p_expr_literal(self, p):
        '''
        expr : TRUE
             | FALSE
             | INT
             | FLOAT
             | STR
        '''
        self.debug("DEBUG", "expr_literal", p[1])
        p[0] = ast.Literal(p[1], p.lineno(1))

    def p_expr_list(self, p):
        '''
        expr : list
        '''
        self.debug("DEBUG", "expr_list")
        p[0] = p[1]

    def p_expr_tuple(self, p):
        '''
        expr : tuple
        '''
        self.debug("DEBUG", "expr_tuple")
        p[0] = p[1]

    def p_expr_sequence_call(self, p):
        '''
        expr : sequence_call
        '''
        self.debug("DEBUG", "expr_sequence_call")
        p[0] = p[1]

    def p_expr_function_call(self, p):
        '''
        expr : function_call
        '''
        self.debug("DEBUG", "expr_function_call")
        p[0] = p[1]

    def p_expr_unary_op(self, p):
        '''
        expr : NOT expr
             | '+' expr %prec UPLUS
             | '-' expr %prec UMINUS
        '''
        self.debug("DEBUG", "expr_unary_op", p[1])
        p[0] = ast.UnaryOperation(p[1], p[2], p.lineno(1))

    def p_expr_binary_op(self, p):
        '''
        expr : expr AND expr
             | expr OR expr
             | expr EQUAL_EQUAL expr
             | expr NOT_EQUAL expr
             | expr '+' expr
             | expr '-' expr
             | expr '*' expr
             | expr '/' expr
             | expr '%' expr
             | expr POWER expr
             | expr INT_DIVIDE expr
             | expr '>' expr
             | expr '<' expr
             | expr GREATER_EQUAL expr
             | expr LESS_EQUAL expr
        '''
        self.debug("DEBUG", "expr_binary_op")
        p[0] = ast.BinaryOperation(p[2], p[1], p[3], p.lineno(2))

    def p_expr_group(self, p):
        '''
        expr : '(' expr ')'
        '''
        self.debug("DEBUG", "expr_group")
        p[0] = p[2]

    def p_elements(self, p):
        '''
        elements : expr ',' elements
                 | expr ','
                 | expr
        '''
        self.debug("DEBUG", "elements")
        if len(p) == 2 or len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_elements_or_empty(self, p):
        '''
        elements_or_empty : elements
                          | empty
        '''
        self.debug("DEBUG", "elements_or_empty")
        p[0] = ast.ElementsList(p[1], p.lineno(1))
    
    def p_tuple(self, p):
        '''
        tuple : '(' elements_or_empty ')'
              | '(' ')'
        '''
        self.debug("DEBUG", "tuple")
        if len(p) == 3:
            p[0] = ast.Tuple(None, p.lineno(1))
        else:
            p[0] = ast.Tuple(p[2], p.lineno(1))

    def p_list(self, p):
        '''
        list : '[' elements_or_empty ']'
             | '[' ']'
        '''
        self.debug("DEBUG", "list")
        if len(p) == 3:
            p[0] = ast.List(None, p.lineno(1))
        else:
            p[0] = ast.List(p[2], p.lineno(1))

    def p_sequence_call(self, p):
        '''
        sequence_call : sequence_index
                      | sequence_slice
                      | sequence_function_call
                      | sequence_method
        '''
        self.debug("DEBUG", "sequence_call")
        p[0] = p[1]
    
    def p_sequence_index(self, p):
        '''
        sequence_index : expr '[' expr ']'
        '''
        self.debug("DEBUG", "sequence_index")
        p[0] = ast.SequenceIndex(p[1], p[3], p.lineno(2))

    def p_sequence_slice(self, p):
        '''
        sequence_slice : expr '[' ':' ']'
                       | expr '[' expr ':' ']'
                       | expr '[' ':' expr ']'
                       | expr '[' expr ':' expr ']'
                       | expr '[' ':' ':' ']'
                       | expr '[' expr ':' ':' ']'
                       | expr '[' ':' expr ':' ']'
                       | expr '[' ':' ':' expr ']'
                       | expr '[' expr ':' expr ':' ']'
                       | expr '[' expr ':' ':' expr ']'
                       | expr '[' ':' expr ':' expr ']'
                       | expr '[' expr ':' expr ':' expr ']'
        '''
        self.debug("DEBUG", "sequence_slice")
        if len(p) == 5:
            p[0] = ast.SequenceSlice(p[1], None, None, None, p.lineno(2))
        elif len(p) == 6:
            if p[3] == ':' and p[4] == ':':
                p[0] = ast.SequenceSlice(p[1], None, None, None, p.lineno(2))
            elif p[3] == ':':
                p[0] = ast.SequenceSlice(p[1], None, p[4], None, p.lineno(2))
            else:
                p[0] = ast.SequenceSlice(p[1], p[3], None, None, p.lineno(2))
        elif len(p) == 7:
            if p[3] == ':' and p[4] == ':':
                p[0] = ast.SequenceSlice(p[1], None, None, p[5], p.lineno(2))
            elif p[3] == ':' and p[5] == ':':
                p[0] = ast.SequenceSlice(p[1], None, p[4], None, p.lineno(2))
            else:
                p[0] = ast.SequenceSlice(p[1], p[3], None, None, p.lineno(2))
        elif len(p) == 8:
            if p[3] == ':':
                p[0] = ast.SequenceSlice(p[1], None, p[4], p[6], p.lineno(2))
            elif p[4] == ':' and p[5] == ":":
                p[0] = ast.SequenceSlice(p[1], p[3], None, p[6], p.lineno(2))
            else:
                p[0] = ast.SequenceSlice(p[1], p[3], p[5], None, p.lineno(2))
        else:
            p[0] = ast.SequenceSlice(p[1], p[3], p[5], p[7], p.lineno(2))

    def p_sequence_function_call(self, p):
        '''
        sequence_function_call : LEN '(' expr ')'
        '''
        self.debug("DEBUG", "sequence_function_call", p[1])
        p[0] = ast.SequenceFunctionCall(p[1], p[3], p.lineno(1))

    def p_sequence_method(self, p):
        '''
        sequence_method : expr '.' APPEND '(' expr ')'
                        | expr '.' EXTEND '(' expr ')'
                        | expr '.' INSERT '(' expr ',' expr ')'
                        | expr '.' INDEX '(' expr ')'
                        | expr '.' POP '(' ')'
                        | expr '.' POP '(' expr ')'
                        | expr '.' COPY '(' ')'
        '''
        self.debug("DEBUG", "sequence_method", p[3])
        if len(p) == 6:
            p[0] = ast.SequenceMethod(p[1], p[3], None, None, p.lineno(3))
        elif len(p) == 7:
            p[0] = ast.SequenceMethod(p[1], p[3], p[5], None, p.lineno(3))
        else:
            p[0] = ast.SequenceMethod(p[1], p[3], p[5], p[7], p.lineno(3))

    def p_args(self, p):
        '''
        args : expr
             | expr ',' args
        '''
        self.debug("DEBUG", "args")
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]
    
    def p_args_or_empty(self, p):
        '''
        args_or_empty : args
                      | empty
        '''
        self.debug("DEBUG", "args_or_empty")
        p[0] = ast.ArgsList(p[1], p.lineno(1))

    def p_function_call(self, p):
        '''
        function_call : ID '(' args_or_empty ')'
        '''
        self.debug("DEBUG", "function_call")
        p[0] = ast.FunctionCall(p[1], p[3], p.lineno(1))
    
    def p_empty(self, p):
        '''
        empty :
        '''
        self.debug("DEBUG", "empty")
        p[0] = None

    ''' Useful code from: miniJavaParser.py from tutorial '''
    # Error handling rule
    def p_error(self, p):
        print("Syntax error at token", p)

    # Build the parser
    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = MiniPythonLexer()
        self.lexer.build()
        self.parser = yacc.yacc(debug=False, module=self, **kwargs)
    ''' End citation '''

    def parse(self, data):
        return self.parser.parse(data)

    def test(self, data):
        result = self.parser.parse(data, debug=False)
        visitor = ast.NodeVisitor()
        visitor.visit(result)

    def debug(self, *args):
        if self.debug_messages:
            print(*args)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Take in the miniPython source code and parses it')
    argparser.add_argument('FILE', help='Input file with miniPython source code')
    args = argparser.parse_args()

    f = open(args.FILE, 'r')
    data = f.read()
    f.close()

    m = MiniPythonParser()
    m.build()
    m.test(data)
