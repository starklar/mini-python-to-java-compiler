#!/usr/bin/env python3

import sys

class Node(object):
    """
    Abstract base class for AST nodes
    """
    def children(self):
        """
        A sequence of all children that are Nodes
        """
        pass

    # Set of attributes for a given node
    attr_names = ()

class NodeVisitor(object):
    def visit(self, node, offset=0):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node, offset)

    def generic_visit(self, node, offset=0):
        lead = ' ' * offset

        output = lead + node.__class__.__name__ + ': '
        if node.attr_names:
            vlist = [getattr(node, n) for n in node.attr_names]
            output += ', '.join('%s' % v for v in vlist)

        print(output)

        for (child_name, child) in node.children():
            self.visit(child, offset=offset + 2)
    ''' End citation '''
    
    def visit_Program(self, node, offset=0):
        lead = ' ' * offset

        output = lead + node.__class__.__name__ + ': '
        
        if node.attr_names:
            vlist = [getattr(node, n) for n in node.attr_names]
            output += ', '.join('%s' % v for v in vlist)

        print(output)
        for (child_name, child) in node.children():
            for line in child:
                self.visit(line, offset=offset + 2)
    
    def visit_WhileStatement(self, node, offset=0):
        lead = ' ' * offset

        output = lead + node.__class__.__name__ + ': '
        
        if node.attr_names:
            vlist = [getattr(node, n) for n in node.attr_names]
            output += ', '.join('%s' % v for v in vlist)

        print(output)
        for (child_name, child) in node.children():
            if type(child) is list:
                for line in child:
                    self.visit(line, offset=offset + 2)
            else:
                self.visit(child, offset=offset + 2)
    
    def visit_IfStatement(self, node, offset=0):
        lead = ' ' * offset

        output = lead + node.__class__.__name__ + ': '
        
        if node.attr_names:
            vlist = [getattr(node, n) for n in node.attr_names]
            output += ', '.join('%s' % v for v in vlist)

        print(output)
        for (child_name, child) in node.children():
            if child_name == "else_body":
                print(lead + "ElseBody:")
                for line in child:
                    self.visit(line, offset=offset + 2)
            elif type(child) is list:
                for line in child:
                    self.visit(line, offset=offset + 2)
            else:
                self.visit(child, offset=offset + 2)
    
    def visit_ElifStatement(self, node, offset=0):
        lead = ' ' * offset

        output = lead + node.__class__.__name__ + ': '
        
        if node.attr_names:
            vlist = [getattr(node, n) for n in node.attr_names]
            output += ', '.join('%s' % v for v in vlist)

        print(output)
        for (child_name, child) in node.children():
            if type(child) is list:
                for line in child:
                    self.visit(line, offset=offset + 2)
            else:
                self.visit(child, offset=offset + 2)
    
    def visit_FunctionDef(self, node, offset=0):
        lead = ' ' * offset

        output = lead + node.__class__.__name__ + ': '
        
        if node.attr_names:
            vlist = [getattr(node, n) for n in node.attr_names]
            output += ', '.join('%s' % v for v in vlist)

        print(output)
        for (child_name, child) in node.children():
            if type(child) is list:
                for line in child:
                    self.visit(line, offset=offset + 2)
            else:
                self.visit(child, offset=offset + 2)
    

class Program(Node):
    def __init__(self, code_lines, coord=None):
        self.code_lines = code_lines
        self.coord = coord

    def children(self):
        nodelist = []
        if self.code_lines is not None:
            nodelist.append(('code_lines', self.code_lines))
        return tuple(nodelist)

    attr_names = ()

class FunctionDef(Node):
    def __init__(self, name, body, params=None, coord=None):
        self.name = name
        self.params = params
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.params is not None:
            nodelist.append(('params', self.params))
        if self.body is not None:
            nodelist.append(('body', self.body))
        return tuple(nodelist)

    attr_names = ('name', )

class CodeLine(Node):
    def __init__(self, code_line, coord=None):
        self.code_line = code_line
        self.coord = coord

    def children(self):
        nodelist = []
        nodelist.append(('Code Line', self.code_line))
        return tuple(nodelist)

    attr_names = ()

class AssignmentStatement(Node):
    def __init__(self, name, expr, coord=None):
        self.name = name
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None:
            nodelist.append(('expr', self.expr))
        return tuple(nodelist)

    attr_names = ('name', )

class IfStatement(Node):
    def __init__(self, cond, if_body, elif_bodies=None, else_body=None, coord=None):
        self.cond = cond
        self.if_body = if_body
        self.elif_bodies = elif_bodies
        self.else_body = else_body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None:
            nodelist.append(('cond', self.cond))
        if self.if_body is not None:
            nodelist.append(('if_body', self.if_body))
        if self.elif_bodies is not None:
            nodelist.append(('elif_bodies', self.elif_bodies))
        if self.else_body is not None:
            nodelist.append(('else_body', self.else_body))
        return tuple(nodelist)
        
    attr_names = ()

class ElifStatement(Node):
    def __init__(self, cond, elif_body, other_elifs=None, coord=None):
        self.cond = cond
        self.elif_body = elif_body
        self.other_elifs = other_elifs
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None:
            nodelist.append(('cond', self.cond))
        if self.elif_body is not None:
            nodelist.append(('elif_body', self.elif_body))
        if self.other_elifs is not None:
            nodelist.append(('other elif_body', self.other_elifs))
        return tuple(nodelist)
        
    attr_names = ()

''' Node class for while statement: miniJavaAST.py from tutorial'''
class WhileStatement(Node):
    def __init__(self, cond, body, coord=None):
        self.cond = cond
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None:
            nodelist.append(('cond', self.cond))
        if self.body is not None:
            nodelist.append(('body', self.body))
        return tuple(nodelist)

    attr_names = ()
''' End citation '''

class ReturnStatement(Node):
    def __init__(self, expr=None, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None:
            nodelist.append(('expr', self.expr))
        return tuple(nodelist)

    attr_names = ()

class ID(Node):
    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name', )

class Literal(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('value', )

class UnaryOperation(Node):
    def __init__(self, op, expr, coord=None):
        self.op = op
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None:
            nodelist.append(('expr', self.expr))
        return tuple(nodelist)

    attr_names = ('op', )

class BinaryOperation(Node):
    def __init__(self, op, left, right, coord=None):
        self.op = op
        self.left = left
        self.right = right
        self.coord = coord

    def children(self):
        nodelist = []
        if self.left is not None:
            nodelist.append(('left', self.left))
        if self.right is not None:
            nodelist.append(('right', self.right))
        return tuple(nodelist)

    attr_names = ('op', )

class FunctionCall(Node):
    def __init__(self, function_name, exprs=None, coord=None):
        self.function_name = function_name
        self.exprs = exprs
        self.coord = coord

    def children(self):
        nodelist = []
        if self.exprs is not None:
            nodelist.append(('exprs', self.exprs))
        return tuple(nodelist)

    attr_names = ('function_name',)

class Sequence(Node):
    def __init__(self, exprs=None, coord=None):
        self.coord = coord
        self.exprs = exprs

    def children(self):
        nodelist = []
        if self.exprs is not None:
            nodelist.append(('exprs', self.exprs))
        return tuple(nodelist)

    attr_names = ()

class List(Sequence): pass
class Tuple(Sequence): pass

class SequenceIndex(Node):
    def __init__(self, seq, index, coord=None):
        self.seq = seq
        self.index = index
        self.coord = coord

    def children(self):
        nodelist = []
        if self.seq is not None:
            nodelist.append(('seq', self.seq))
        if self.index is not None:
            nodelist.append(('index', self.index))
        return tuple(nodelist)

    attr_names = ()

class SequenceSlice(Node):
    def __init__(self, seq, start=None, end=None, step=None, coord=None):
        self.seq = seq
        self.start = start
        self.end = end
        self.step = step
        self.coord = coord

    def children(self):
        nodelist = []
        if self.seq is not None:
            nodelist.append(('seq', self.seq))
        if self.start is not None:
            nodelist.append(('start', self.start))
        if self.end is not None:
            nodelist.append(('end', self.end))
        if self.step is not None:
            nodelist.append(('step', self.step))
        return tuple(nodelist)

    attr_names = ('start', 'end', 'step',)

class SequenceFunctionCall(Node):
    def __init__(self, function_name, arg, coord=None):
        self.arg = arg
        self.function_name = function_name
        self.coord = coord

    def children(self):
        nodelist = []
        if self.arg is not None:
            nodelist.append(('arg', self.arg))
        return tuple(nodelist)

    attr_names = ('function_name',)

class SequenceMethod(Node):
    def __init__(self, seq, method_name, arg1=None, arg2=None, coord=None):
        self.seq = seq
        self.method_name = method_name
        self.arg1 = arg1
        self.arg2 = arg2
        self.coord = coord

    def children(self):
        nodelist = []
        if self.seq is not None:
            nodelist.append(('seq', self.seq))
        if self.arg1 is not None:
            nodelist.append(('arg1', self.arg1))
        if self.arg2 is not None:
            nodelist.append(('arg2', self.arg2))
        return tuple(nodelist)

    attr_names = ('method_name',)

class ExprList(Node):
    def __init__(self, exprs=None, coord=None):
        self.exprs = exprs
        self.coord = coord

    def children(self):
        nodelist = []
        for i, expr in enumerate(self.exprs or []):
            nodelist.append(('expr[%d]' % i, expr))
        return tuple(nodelist)

    attr_names = ()

class ParamsList(ExprList): pass
class ArgsList(ExprList): pass
class ElementsList(ExprList): pass

class PrintStatement(Node):
    def __init__(self, expr=None, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None:
            nodelist.append(('expr', self.expr))
        else:
            nodelist.append(('expr', "''"))
        return tuple(nodelist)

    attr_names = ()