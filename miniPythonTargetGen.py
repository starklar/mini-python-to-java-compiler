#!/usr/bin/env python3

import os
import argparse
import re
from miniPythonSymbolTable import SymbolTable
from miniPythonIRGen import IRGen

class TargetGen(object):

    def __init__(self, IR):
        self.IR = IR
        self.TAC_lst = IR.TAC_lst
        self.regs = [None] * (IR.register_count + 1)
        self.register_count = 0
        self.in_func_def = False
        self.function_defs = []
        self.target = []
        self.st = SymbolTable()
        self.fcall_statement_regs = {}
        self.mcall_statement_regs = {}
        self.indents = 0
    
    # HELPER FUNCTIONS

    def write(self, line):
        if self.in_func_def:
            self.function_defs.append(line)
        else:
            self.target.append(line)

    def assign_reg(self, value):
        self.register_count += 1
        self.regs[self.register_count] = value

    def is_reg(self, value):
        if type(value) is not str:
            return False
        pattern = re.compile(r"^_t(0|([1-9][0-9]*))$")
        return pattern.match(value)
    
    def get_reg(self, reg_str):
        return self.regs[int(reg_str[2:])]

    def translate_primitives(self, prim):
        t = type(prim)
        if t == bool:
            return "true" if prim else "false"
        elif t == int or t == float:
            return str(prim)
    
    def translate_into_integer(self, expr):
        if self.is_reg(expr):
            return "(Integer) %s" % self.get_reg(expr)
        t = type(expr)
        if t == int:
            return "Integer.valueOf(%s)" % expr
        elif t == bool:
            return "Integer.valueOf(%s)" % (1 if bool else 0)
        raise Exception("translate_into_integer can only take in ints or bools.")

    def translate_string(self, string):
        return "%s" % string

    def translate_seq(self, seq):
        elems = ""
        if len(seq) > 0:
            elems += str(self.translate_expr(seq[0]))
        for elem in seq[1:]:
            elems += ", {}".format(self.translate_expr(elem))
        return "new ArrayList(Arrays.asList(%s))" % elems

    def translate_expr(self, expr):
        if self.is_reg(expr):
            return self.get_reg(expr)
        elif type(expr) == str:
            return self.translate_string(expr)
        elif type(expr) == list or type(expr) == tuple:
            return self.translate_seq(expr)
        return self.translate_primitives(expr)

    def translate_operator(self, op):
        if op == "or":
            return "||"
        elif op == "and":
            return "&&"
        elif op == "not":
            return "!"
        return op

    
    #########
    # TYPES #
    #       #
    # bool  #
    # int   #
    # float #
    # str   #
    # list  #
    # Any   #
    #########


    def gen_assign_stmnt(self, tac):
        assignment_str = ""
        
        if self.is_reg(tac.left_operand):
            expr_type = object
            type_str = "Object"
            expr_str = self.get_reg(tac.left_operand)
        else:
            expr = tac.left_operand
            expr_type = type(expr)
            if expr_type == bool:
                type_str = "boolean"
            elif expr_type == int:
                type_str = "int"
            elif expr_type == float:
                type_str = "double"
            elif expr_type == str:
                type_str = "String"
            elif expr_type == list or expr_type == tuple:
                type_str = "ArrayList"
            expr_str = self.translate_expr(expr)
        
        if self.st.check_variable(tac.result):
            assignment_str = "{} = {}".format(tac.result, expr_str)
        else:
            self.st.declare_variable(tac.result, expr_type, -1)
            assignment_str = "{} {} = {}".format(type_str, tac.result, expr_str)
        self.write(assignment_str)
        
    # END HELPERS

    def gen_unary_op(self, tac):
        op = self.translate_operator(tac.operator)
        operand = self.translate_expr(tac.left_operand)
        if op == "!":
            expr = "({} (Boolean) ({}))".format(op, operand)
        else:
            expr = "({} ({}))".format(op, operand)
        self.assign_reg(expr)

    def gen_bin_op(self, tac):
        op = self.translate_operator(tac.operator)
        left = self.translate_expr(tac.left_operand)
        right = self.translate_expr(tac.right_operand)
        if op == "**":
            expr = "Math.pow({}, {})".format(left, right)
        elif op == "//":
            expr = "Math.floor(({}) / ({}))".format(left, right)
        elif op == "&&" or op == "||":
            expr = "(Boolean) (((Boolean) {}) {} ((Boolean) {}))".format(left, op, right)
        else:
            expr = "(({}) {} ({}))".format(left, op, right)
        self.assign_reg(expr)
    
    def gen_func_def(self, tac):
        self.in_func_def = True
        self.st.push_scope()
        
        params = tac.right_operand
        params_str = ""

        if len(params) > 0:
            params_str += "Object " + params[0]
            for param in params[1:]:
                params_str += ", Object " + param

        self.write("static Object %s(%s) {" % (tac.left_operand, params_str))

    def gen_ret_stmnt(self, tac):
        if tac.left_operand is None:
            stmnt = "return null"
        else:
            stmnt = "return {}".format(self.translate_expr(tac.left_operand))
        self.write(stmnt)

    def gen_seq_index(self, tac):
        lst = self.translate_expr(tac.left_operand)
        index = self.translate_into_integer(tac.right_operand)
        expr = "{}.get({})".format(lst, index)
        self.assign_reg(expr)

    def gen_seq_slice(self, tac):
        lst = self.translate_expr(tac.left_operand)

        if tac.right_operand[0] is None:
            start = "0"
        else:
            start = self.translate_into_integer(tac.right_operand[0])

        if tac.right_operand[1] is None:
            end = "{}.size()".format(lst)
        else:
            end = self.translate_into_integer(tac.right_operand[1])

        if tac.right_operand[2] is None:
            expr = "{}.subList({}, {})".format(lst, start, end)
        else:
            step = self.translate_into_integer(tac.right_operand[2])
            expr = "step_method({}, {}, {}, {})".format(lst, start, end, step)
        
        self.assign_reg(expr)
        
    def gen_func_call(self, tac):
        if tac.left_operand == "len":
            # List and tuple `len` function call
            expr = "{}.size()".format(self.translate_expr(tac.right_operand[0]))
        else:
            # General function call
            expr = "{}(".format(tac.left_operand)
            if len(tac.right_operand) > 0:
                expr += "{}".format(self.translate_expr(tac.right_operand[0]))
            for arg in tac.right_operand[1:]:
                expr += ", {}".format(self.translate_expr(arg))
            expr += ")"

        self.assign_reg(expr)
        if tac.result in self.fcall_statement_regs:
            self.write(expr)

    def gen_seq_method_call(self, tac):
        lst = self.translate_expr(tac.right_operand[0])
        expr = "{}.".format(lst)

        if tac.left_operand == "append":
            expr += "add("
        elif tac.left_operand == "extend":
            expr += "addAll("
        elif tac.left_operand == "index":
            expr += "indexOf("
        elif tac.left_operand == "insert":
            expr += "add((int)"
        elif tac.left_operand == "pop":
            if len(tac.right_operand[1:]) == 0:
                expr += "remove({}.size() - 1".format(lst)
            else:
                expr += "remove("
        elif tac.left_operand == "copy":
            expr += "clone("
        
        if len(tac.right_operand[1:]) > 0:
            expr += "{}".format(self.translate_expr(tac.right_operand[1]))

        for arg in tac.right_operand[2:]:
            expr += ", {}".format(self.translate_expr(arg))

        expr += ")"
        self.assign_reg(expr)

        if tac.result in self.mcall_statement_regs:
            self.write(expr)

    def gen_if_stmnt(self, tac):
        self.write("if ((Boolean) %s) {" % (self.translate_expr(tac.left_operand)))
        self.st.push_scope()
    
    def gen_else_if_stmnt(self, tac):
        self.write("else if ((Boolean) %s) {" % (self.translate_expr(tac.left_operand)))
        self.st.push_scope()
        
    def gen_else_stmnt(self, tac):
        self.write("else {")
        self.st.push_scope()
        
    def gen_while_stmnt(self, tac):
        self.write("while (%s) {" % (self.translate_expr(tac.left_operand)))
        self.st.push_scope()

    def gen_end_label(self, tac):
        self.st.pop_scope()
        self.write("}")
        if self.st.get_scope() == 1:
            self.in_func_def = False

    def gen_print_statement(self, tac):
        self.write("System.out.println(" + self.translate_expr(tac.left_operand) + ")")

    def create_step_method(self, lst):
        lst.append("static ArrayList step_method(ArrayList lst, int p_start, int p_end, int step) {")
        lst.append("ArrayList return_lst = new ArrayList()")
        lst.append("if (step == 0) {")
        lst.append('throw new IllegalArgumentException("step_method() cannot have step param be 0!")')
        lst.append("}")
        lst.append("int start = p_start")
        lst.append("int end = p_end")
        lst.append("if (start < 0) {")
        lst.append("start = lst.size() - p_start")
        lst.append("}")
        lst.append("if (end < 0) {")
        lst.append("end = lst.size() - p_end")
        lst.append("}")
        lst.append("if (step > 0) {")
        lst.append("for (int index = start; index < end; index += step) {")
        lst.append("return_lst.add(lst.get(index))")
        lst.append("}")
        lst.append("}")
        lst.append("else {")
        lst.append("for (int index = start; index > end; index += step) {")
        lst.append("return_lst.add(lst.get(index))")
        lst.append("}")
        lst.append("}")
        lst.append("return return_lst")
        lst.append("}")

    def generate(self, tac):
        if tac.operator is None:
            # Assignment
            self.gen_assign_stmnt(tac)
        elif tac.operator in ["and", "or", "not", "==", "!=", "+", "-", "*", "/", "%", "**", "//", ">", "<", ">=", "<="]:
            if tac.right_operand is not None:
                # Binary operation
                self.gen_bin_op(tac)
            else:
                # Unary Operation
                self.gen_unary_op(tac)
        elif tac.operator == "fdef":
            self.gen_func_def(tac)
        elif tac.operator == "if":
            self.gen_if_stmnt(tac)
        elif tac.operator == "else-if":
            self.gen_else_if_stmnt(tac)
        elif tac.operator == "else":
            self.gen_else_stmnt(tac)
        elif tac.operator == "while":
            self.gen_while_stmnt(tac)
        elif tac.operator == "end-label":
            self.gen_end_label(tac)
        elif tac.operator == "print":
            self.gen_print_statement(tac)
        elif tac.operator == "return":
            self.gen_ret_stmnt(tac)
        elif tac.operator == "fcall":
            self.gen_func_call(tac)
        elif tac.operator == "index":
            self.gen_seq_index(tac)
        elif tac.operator == "slice":
            self.gen_seq_slice(tac)
        elif tac.operator == "mcall":
            self.gen_seq_method_call(tac)
        else:
            raise Exception("Unrecognized operator found: " + tac.operator)
    
    def format_lines(self, lines):
        for i in range(len(lines)):
            line = lines[i]
            if line[-1] == "{":
                lines[i] = "{}{}{}".format("    "*self.indents, line, "\n")
                self.indents += 1
            elif line[-1] == "}":
                self.indents -= 1
                lines[i] = "{}{}{}".format("    "*self.indents, line, "\n")
            else:
                lines[i] = "{}{}{}".format("    "*self.indents, line, ";\n")

    def generate_target(self, file_name):
        file_name_no_ext = os.path.splitext(os.path.normpath(file_name))[0]
        class_name = os.path.basename(file_name_no_ext).capitalize()

        starting_code = []
        starting_code.append("import java.util.*")
        starting_code.append("public class %s {" % class_name)
        self.create_step_method(starting_code)
        self.target.append("public static void main(String args[]) {")
        self.format_lines(starting_code)

        for tac in self.TAC_lst:
            # For knowing which function calls are standalone statements
            if tac.operator == "fcall":
                self.fcall_statement_regs[tac.result] = None
            elif tac.operator == "mcall":
                self.mcall_statement_regs[tac.result] = None
            elif tac.result in self.fcall_statement_regs:
                self.fcall_statement_regs.pop(tac.result, None)
            elif tac.result in self.mcall_statement_regs:
                self.mcall_statement_regs.pop(tac.result, None)

        for tac in self.TAC_lst:
            self.generate(tac)
        self.target.append("}")
        self.target.append("}")

        self.format_lines(self.function_defs)
        self.format_lines(self.target)

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file = open("{}/{}.java".format(output_dir, class_name), "w")
        file.writelines(starting_code)
        file.writelines(self.function_defs)
        file.writelines(self.target)
        file.close()
        
