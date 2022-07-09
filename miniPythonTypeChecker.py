#!/usr/bin/env python3

from miniPythonSymbolTable import SymbolTable, ParseError
import miniPythonAST as ast

class TypeChecker(object):
    def typecheck(self, node, st):
        method = 'check_' + node.__class__.__name__
        return getattr(self, method, self.generic_typecheck)(node, st)

    def generic_typecheck(self, node, st):
        print(node)
        if node is None:
            return ''
        else:
            return ''.join(self.typecheck(c, st) for c_name, c in node.children())

    def check_Program(self, node, st):
        """
        Generate global symbol table. Recursively typecheck its classes and
        add its class symbol table to itself.
        """
        # Generate global symbol table
        global_st = SymbolTable()

        for codeline in node.code_lines:
            self.typecheck(codeline, global_st)

        return global_st

    def check_FunctionDef(self, node, st):
        st.push_scope()

        self.typecheck(node.params, st)

        # Go through the method body and type check each statements
        for codeline in node.body:
            self.typecheck(codeline, st)

        st.pop_scope()

        st.declare_function(node.name, node, node.coord)
        return "Any"

    def check_CodeLine(self, node, st):
        return self.typecheck(node.code_line, st)

    def check_AssignmentStatement(self, node, st):
        expr_type = self.typecheck(node.expr, st)
        if expr_type is None:
            raise ParseError("Cannot use None type", node.coord)
        if not st.check_variable(node.name):
            st.declare_variable(node.name, expr_type, node.coord)
        else:
            old_type = st.lookup_variable(node.name, node.coord)
            if old_type != expr_type and (old_type != "Any" and expr_type != "Any"):
                raise ParseError("Cannot change already assigned variable type: " + str(old_type) + " to: " + str(expr_type), node.coord)
        return expr_type

    def check_IfStatement(self, node, st):
        if self.typecheck(node.cond, st) is None:
            raise ParseError("Cannot use None type", node.coord)

        if node.if_body is not None:
            st.push_scope()
            for codeline in node.if_body:
                self.typecheck(codeline, st)
            st.pop_scope()
        if node.elif_bodies is not None:
            self.typecheck(node.elif_bodies, st)
        if node.else_body is not None:
            st.push_scope()
            for codeline in node.else_body:
                self.typecheck(codeline, st)
            st.pop_scope()

        return None

    def check_ElifStatement(self, node, st):
        if self.typecheck(node.cond, st) is None:
            raise ParseError("Cannot use None type", node.coord)
        
        st.push_scope()
        for codeline in node.elif_body:
            self.typecheck(codeline, st)
        st.pop_scope()
        
        if node.other_elifs is not None:
            self.typecheck(node.other_elifs, st)
        
        return None

    def check_WhileStatement(self, node, st):
        if self.typecheck(node.cond, st) is None:
            raise ParseError("Cannot use None type", node.coord)

        if node.body is not None:
            st.push_scope()
            for codeline in node.body:
                self.typecheck(codeline, st)
            st.pop_scope()

        return None

    def check_ReturnStatement(self, node, st):
        return_type = self.typecheck(node.expr, st)
        if return_type is None:
            raise ParseError("Cannot use None type", node.coord)
        return return_type
    
    def check_PrintStatement(self, node, st):
        self.typecheck(node.expr, st)
        return None

    def check_ID(self, node, st):
        return st.lookup_variable(node.name, node.coord)

    def check_Literal(self, node, st):
        return type(node.value)

    def check_UnaryOperation(self, node, st):
        expr_type = self.typecheck(node.expr, st)
        if expr_type is None:
            raise ParseError("Cannot use None type", node.coord)

        if expr_type is None:
            raise ParseError("Cannot use None type", node.coord)
        elif node.op == "not":
            return bool
        elif node.op == "+" or node.op == "-":
            if expr_type == int or expr_type == bool:
                return int
            elif expr_type == float:
                return float
            elif expr_type == str or expr_type == list:
                raise ParseError("Illegal type for unary operation, was %s" % expr_type, node.coord)
            elif expr_type == "Any":
                return "Any"

        raise Exception("Shouldn't reach here")

    ###############################
    # bool, int, float, str, list #
    ###############################

    def check_BinaryOperation(self, node, st):
        left_type = self.typecheck(node.left, st)
        right_type = self.typecheck(node.right, st)

        if left_type is None or right_type is None:
            raise ParseError("Cannot use None type", node.coord)
        if left_type == "Any" or right_type == "Any":
            return "Any"
        
        # AND, OR, '==', '!='
        if node.op in ["and", "or", "==", "!="]:
            return bool
        
        # '+'
        elif node.op == "+":
            if left_type == bool:
                if right_type in [int, bool]:
                    return int
                elif right_type == float:
                    return float
                else:
                    raise ParseError("Can only add bool with int, float or bool, was %s" % right_type, node.coord)
            elif left_type == int:
                if right_type in [int, bool]:
                    return int
                elif right_type == float:
                    return float
                else:
                    raise ParseError("Can only add int with int, float or bool, was %s" % right_type, node.coord)
            elif left_type == float:
                if right_type in [int, bool, float]:
                    return float
                else:
                    raise ParseError("Can only add floats with int, float or bool, was %s" % right_type, node.coord)
            elif left_type == str:
                if right_type == str:
                    return str
                else:
                    raise ParseError("Can only add strings with strings, was %s" % right_type, node.coord)
            elif left_type == list:
                if right_type == list:
                    return list
                else:
                    raise ParseError("Can only add lists with lists, was %s" % right_type, node.coord)
            elif left_type == tuple:
                if right_type == tuple:
                    return tuple
                else:
                    raise ParseError("Can only add tuples with tuples, was %s" % right_type, node.coord)

        # '*'
        elif node.op == "*":
            if left_type in [int, bool]:
                if right_type in [int, bool]:
                    return int
                elif right_type == float:
                    return float
                elif right_type == str:
                    return str
                elif right_type == list:
                    return list
            elif left_type == float:
                if right_type in [int, bool, float]:
                    return float
                else:
                    raise ParseError("Can only multiply floats with int, float or bool, was %s" % right_type, node.coord)
            elif left_type == str:
                if right_type in [int, bool]:
                    return str
                else:
                    raise ParseError("Can only multiply strings with int or bool, was %s" % right_type, node.coord)
            elif left_type == list:
                if right_type in [int, bool]:
                    return list
                else:
                    raise ParseError("Can only multiply lists with int or bool, was %s" % right_type, node.coord)
            elif left_type == tuple:
                if right_type in [int, bool]:
                    return tuple
                else:
                    raise ParseError("Can only multiply tuples with int or bool, was %s" % right_type, node.coord)

    ###############################
    # bool, int, float, str, list #
    ###############################

        # '-', '/', '%', '**', '//'
        elif node.op in ["-", "/", "%", "**", "//"]:
            if left_type not in [bool, int, float] or right_type not in [bool, int, float]:
                raise ParseError(node.op + " can only work with bools, ints, and floats, was %s and %s" % (left_type, right_type), node.coord)
            elif left_type in [bool, int]:
                if right_type == float:
                    return float
                return int
            elif left_type == float:
                return float

        # '>', '<', '>=', '<='
        elif node.op in [">", "<", ">=", "<="]:
            return bool
        
        raise Exception("Shouldn't reach here")

    def check_FunctionCall(self, node, st):
        function = st.lookup_function(node.function_name, node.coord)

        if len(function.params.exprs or []) != len(node.exprs.exprs or []):
            raise ParseError("Argument length mismatch with function", node.coord)

        return "Any"

    def check_Tuple(self, node, st):
        if node.exprs != None:
            for expr in node.exprs.exprs:
                if self.typecheck(expr, st) is None:
                    raise ParseError("Cannot use None type", node.coord)
        return tuple

    def check_List(self, node, st):
        if node.exprs != None:
            for expr in node.exprs.exprs:
                if self.typecheck(expr, st) is None:
                    raise ParseError("Cannot use None type", node.coord)
        return list

    def check_SequenceIndex(self, node, st):
        seq_type = self.typecheck(node.seq, st)
        if seq_type is None:
            raise ParseError("Cannot use None type", node.coord)
        elif seq_type not in [list, tuple, "Any"]:
            raise ParseError("Can only get elements of list or tuple, was %s" % seq_type, node.coord)

        index_type = self.typecheck(node.index, st)
        if index_type is None:
            raise ParseError("Cannot use None type", node.coord)
        if index_type not in [int, bool, "Any"]:
            raise ParseError("Cannot call list or tuple index with a non int or bool argument, was %s" % index_type, node.coord)
        
        return "Any"

    def check_SequenceSlice(self, node, st):
        seq_type = self.typecheck(node.seq, st)
        if seq_type is None:
            raise ParseError("Cannot use None type", node.coord)
        elif seq_type not in [list, tuple, "Any"]:
            raise ParseError("Can only slice a list or tuple, was %s" % seq_type, node.coord)

        if node.start is not None:
            start_type = self.typecheck(node.start, st)
            if start_type is None:
                raise ParseError("Cannot use None type", node.coord)
            elif start_type not in [bool, int, "Any"]:
                raise ParseError("Slice start type must be an int or a bool, was %s" % start_type, node.coord)
        elif node.end is not None:
            end_type = self.typecheck(node.end, st)
            if end_type is None:
                raise ParseError("Cannot use None type", node.coord)
            elif end_type not in [bool, int, "Any"]:
                raise ParseError("Slice end type must be an int or a bool, was %s" % end_type, node.coord)
        elif node.step is not None:
            step_type = self.typecheck(node.step, st)
            if step_type is None:
                raise ParseError("Cannot use None type", node.coord)
            elif step_type not in [bool, int, "Any"]:
                raise ParseError("Slice step type must be an int or a bool, was %s" % step_type, node.coord)

        return seq_type

    def check_SequenceFunctionCall(self, node, st):
        seq_type = self.typecheck(node.arg, st)
        if seq_type is None:
            raise ParseError("Cannot use None type", node.coord)
        elif seq_type not in [list, tuple, "Any"]:
            raise ParseError("Can only call len() on a list or tuple", node.coord)
        return int

    def check_SequenceMethod(self, node, st):
        seq_type = self.typecheck(node.seq, st)
        if seq_type is None:
            raise ParseError("Cannot use None type", node.coord)
        elif self.typecheck(node.seq, st) not in [list, tuple, "Any"]:
            raise ParseError("Can only call sequence methods on a list or tuple, was %s" % seq_type, node.coord)
        
        if node.method_name == "append":
            if seq_type == tuple:
                raise ParseError("Cannot call append() on tuples", node.coord)
            elif node.arg1 is None:
                raise ParseError("Sequence method append() requires an argument", node.coord)
            self.typecheck(node.arg1, st)
            return None
        elif node.method_name == "extend":
            if seq_type == tuple:
                raise ParseError("Cannot call extend() on tuples", node.coord)
            elif node.arg1 is None:
                raise ParseError("Sequence method extend() requires a list argument", node.coord)
            elif self.typecheck(node.arg1, st) != list:
                raise ParseError("Sequence method extend() requires a list as an argument, not: " + self.typecheck(node.arg1, st), node.coord)
            return list
        elif node.method_name == "insert":
            if seq_type == tuple:
                raise ParseError("Cannot call insert() on tuples", node.coord)
            elif node.arg1 is None or node.arg2 is None:
                raise ParseError("Sequence method insert() requires 2 arguments", node.coord)
            if self.typecheck(node.arg1, st) not in [int, bool, "Any"]:
                raise ParseError("Sequence method insert()'s first argument must be either an int or bool, not " + self.typecheck(node.arg1, st), node.coord)
            return None
        elif node.method_name == "index":
            if node.arg1 is None:
                raise ParseError("Sequence method index() requires an argument", node.coord)
            return int
        elif node.method_name == "pop":
            if seq_type == tuple:
                raise ParseError("Cannot call pop() on tuples", node.coord)
            elif node.arg1 is not None:
                arg1_type = self.typecheck(node.arg1, st)
                if arg1_type not in [int, bool, "Any"]:
                    raise ParseError("Sequence method pop() does not support as an argument: " + arg1_type, node.coord)
            return "Any"
        elif node.method_name == "copy":
            return seq_type
          
        raise Exception("Given list operation unknown: " + node.method_name)

    def check_ParamsList(self, node, st):
        if node.exprs != None:
            for expr in node.exprs:
                st.declare_variable(expr.name, "Any", node.coord)

    def check_ArgsList(self, node, st):
        for expr in node.exprs:
            if self.typecheck(expr, st) is None:
                raise ParseError("Cannot use None type", node.coord)
        return None

    def check_ElementsList(self, node, st):
        for expr in node.exprs:
            if self.typecheck(expr, st) is None:
                raise ParseError("Cannot use None type", node.coord)
        return None
