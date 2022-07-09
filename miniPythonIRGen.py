#!/usr/bin/env python3

import miniPythonAST as ast
import os
import re
from threeAddressCode import TAC

class IRGen(object):
    def __init__(self):
        self.TAC_lst = []
        self.register_count = 0
        self.label_count = 0
        self.else_labels_stack = []

    def generate(self, node):
        method = 'gen_' + node.__class__.__name__
        return getattr(self, method)(node)

    # HELPERS

    def is_reg(self, value):
        if type(value) is not str:
            return False
        pattern = re.compile(r"^_t(0|([1-9][0-9]*))$")
        return pattern.match(value)

    def is_str_literal(self, value):
        if type(value) is not str:
            return False
        pattern = re.compile(r'^"[^"]*"$')
        return pattern.match(value)

    def add_TAC(self, result, operator=None, left_operand=None, right_operand=None):
        tac = TAC(result, operator, left_operand, right_operand)
        self.TAC_lst.append(tac)
    
    def get_register(self):
        return "_t%d" % self.inc_register()

    def get_label(self):
        return "_L%d" % self.inc_label()

    def push_else_label(self, label):
        self.else_labels_stack.append(label)

    def pop_else_label(self):
        self.else_labels_stack.pop()

    ''' Helper functions from tinyJavaIRGen.py '''

    def inc_register(self):
        """
        Can reset the register_count to reuse them
        """
        self.register_count += 1
        return self.register_count

    def inc_label(self):
        """
        Increase the label count and return its value for use
        """
        self.label_count += 1
        return self.label_count

    ''' End Citation '''

    def print_ir(self):
        """
        Loop through the generated IR code and print them out to stdout
        """
        for tac in self.TAC_lst:
            print(tac)

    def output_ir(self, file_name):
        """
        Loop through the generated IR code and output them out to a file
        """
        name = os.path.basename(os.path.splitext(os.path.normpath(file_name))[0])
        os.makedirs("output", exist_ok=True)
        file = open("output/{}_ir.out".format(name), "w")
        for tac in self.TAC_lst:
            file.write(str(tac) + "\n")
        file.close()

    def gen_Program(self, node):
        for codeline in node.code_lines:
            self.generate(codeline)
        
    def gen_FunctionDef(self, node):
        params = []
        node_params = self.generate(node.params)
        if node_params is not None:
            params = node_params.copy()

        self.add_TAC(None, "fdef", node.name, tuple(params))

        for codeline in node.body:
            self.generate(codeline)

        self.add_TAC(None, "end-label")

    def gen_CodeLine(self, node):
        self.generate(node.code_line)

    def gen_AssignmentStatement(self, node):
        expr = self.generate(node.expr)
        self.add_TAC(node.name, None, expr)

    def gen_IfStatement(self, node):
        cond = self.generate(node.cond)
        self.add_TAC(None, "if", cond)
        
        for codeline in node.if_body:
            self.generate(codeline)
        self.add_TAC(None, "end-label")

        if node.elif_bodies is not None:
            self.gen_ElifStatement(node.elif_bodies)

        if node.else_body is not None:
            self.add_TAC(None, "else")
            for codeline in node.else_body:
                self.generate(codeline)
            self.add_TAC(None, "end-label")

    def gen_ElifStatement(self, node):
        cond = self.generate(node.cond)
        self.add_TAC(None, "else-if", cond)

        for codeline in node.elif_body:
            self.generate(codeline)
        self.add_TAC(None, "end-label")

        if node.other_elifs is not None:
            self.gen_ElifStatement(node.other_elifs)

    def gen_WhileStatement(self, node):
        cond = self.generate(node.cond)

        self.add_TAC(None, "while", cond)

        for codeline in node.body:
            self.generate(codeline)
        
        self.add_TAC(None, "end-label")

    def gen_ReturnStatement(self, node):
        expr = self.generate(node.expr)
        self.add_TAC(None, "return", expr)

    def gen_PrintStatement(self, node):
        expr = self.generate(node.expr)
        self.add_TAC(None, "print", expr)

    def gen_ID(self, node):
        return node.name

    def gen_Literal(self, node):
        return node.value

    def gen_UnaryOperation(self, node):
        expr = self.generate(node.expr)
        if type(expr) is not str:
                if node.op == "+":
                    return expr
                elif node.op == "-":
                    return -1 * expr
                elif node.op == "not":
                    return not expr
        reg = self.get_register()
        self.add_TAC(reg, node.op, expr)
        return reg

    def gen_BinaryOperation(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)

        if ((type(left) != str and type(right) != str) or (self.is_str_literal(left) and self.is_str_literal(right))):
            if node.op == "and":
                return left and right
            if node.op == "or":
                return left or right
            if node.op == "==":
                return left == right
            if node.op == "!=":
                return left != right
            if node.op == "+":
                if type(left) == str and type(right) == str:
                    return left[:-1] + right[1:]
                return left + right
            if node.op == "-":
                return left - right
            if node.op == "/":
                return left / right
            if node.op == "%":
                return left % right
            if node.op == "**":
                return left ** right
            if node.op == "//":
                return left // right
            if node.op == ">":
                return left > right
            if node.op == "<":
                return left < right
            if node.op == ">=":
                return left >= right
            if node.op == "<=":
                return left <= right

        reg = self.get_register()
        self.add_TAC(reg, node.op, left, right)
        return reg

    def gen_FunctionCall(self, node):
        args = []
        exprs = self.generate(node.exprs)
        if exprs is not None:
            args = exprs.copy()

        reg = self.get_register()
            
        self.add_TAC(reg, "fcall", "{}".format(node.function_name), tuple(args))

        return reg

    def gen_Tuple(self, node):
        if (node.exprs):
            return self.generate(node.exprs)
        else:
            return ()

    def gen_List(self, node):
        if (node.exprs):
            return self.generate(node.exprs)
        else:
            return []

    def gen_SequenceIndex(self, node):
        reg = self.get_register()
        self.add_TAC(reg, "index", self.generate(node.seq), self.generate(node.index))
        return reg

    def gen_SequenceSlice(self, node):
        start = self.generate(node.start) if node.start is not None else None
        end = self.generate(node.end) if node.end is not None else None
        step = self.generate(node.step) if node.step is not None else None
        reg = self.get_register()
        self.add_TAC(reg, "slice", self.generate(node.seq), (start, end, step))
        return reg

    def gen_SequenceFunctionCall(self, node):
        args = [self.generate(node.arg)]
        reg = self.get_register()
        self.add_TAC(reg, "fcall", node.function_name, tuple(args))
        return reg

    def gen_SequenceMethod(self, node):
        args = []
        args.append(self.generate(node.seq))
        if node.arg1 is not None:
            args.append(self.generate(node.arg1))
        if node.arg2 is not None:
            args.append(self.generate(node.arg2))

        reg = self.get_register()
        self.add_TAC(reg, "mcall", node.method_name, tuple(args))
        return reg
        
    def gen_ParamsList(self, node):
        exprs = []
        if node.exprs is not None:
            for expr in node.exprs:
                exprs.append(self.generate(expr))
        return exprs

    def gen_ArgsList(self, node):
        exprs = []
        if node.exprs is not None:
            for expr in node.exprs:
                exprs.append(self.generate(expr))
        return exprs

    def gen_ElementsList(self, node):
        exprs = []
        if node.exprs is not None:
            for expr in node.exprs:
                exprs.append(self.generate(expr))
        return exprs
