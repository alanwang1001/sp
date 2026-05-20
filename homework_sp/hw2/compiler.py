from ast_nodes import *

class Compiler:
    def __init__(self):
        self.bytecode = []

    def compile(self, node):
        if isinstance(node, Program):
            for stmt in node.stmts: self.compile(stmt)
        elif isinstance(node, Let):
            self.compile(node.expr)
            self.bytecode.append(('STORE', node.name))
        elif isinstance(node, Print):
            self.compile(node.expr)
            self.bytecode.append(('PRINT',))
        elif isinstance(node, If):
            self.compile(node.cond)
            jump_idx = len(self.bytecode)
            self.bytecode.append(['JMP_IF_FALSE', 0])
            for stmt in node.body:
                self.compile(stmt)
            self.bytecode[jump_idx][1] = len(self.bytecode)
        elif isinstance(node, BinOp):
            self.compile(node.left)
            self.compile(node.right)
            self.bytecode.append(('OP', node.op))
        elif isinstance(node, Var):
            self.bytecode.append(('LOAD', node.name))
        elif isinstance(node, Num):
            self.bytecode.append(('PUSH', node.value))
        return self.bytecode
