#!/usr/bin/env python3

class ParseError(Exception): pass

class SymbolTable(object):
    def __init__(self):
        self.functions = dict()
        self.scope_stack = [dict()]

    def get_scope(self):
        return len(self.scope_stack)

    def push_scope(self):
        self.scope_stack.append(dict())

    def pop_scope(self):
        assert len(self.scope_stack) > 1
        self.scope_stack.pop()

    def declare_function(self, function_name, function_node, line_number):
        if function_name in self.functions:
            raise ParseError("Redeclaring function named \"" + function_name + "\"", line_number)
        self.functions[function_name] = function_node

    def lookup_function(self, function_name, line_number):
        if function_name not in self.functions:
            raise ParseError("Referencing undefined function \"" + function_name + "\"")
        return self.functions[function_name]

    def declare_variable(self, name, var_type, line_number):
        if name in self.scope_stack[-1]:
            raise ParseError("Redeclaring variable named \"" + name + "\"", line_number)
        self.scope_stack[-1][name] = var_type

    def lookup_variable(self, name, line_number):
        # You should traverse through the entire scope stack
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        raise ParseError("Referencing undefined variable \"" + name + "\"", line_number)
    
    def check_variable(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return True
        return False