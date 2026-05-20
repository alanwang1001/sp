from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self): return self.tokens[self.pos]
    
    def consume(self, expected_type, expected_val=None):
        tok = self.current()
        if tok[0] == expected_type and (expected_val is None or tok[1] == expected_val):
            self.pos += 1
            return tok[1]
        raise SyntaxError(f"Parser 錯誤：預期 {expected_type} {expected_val}，但得到 {tok}")

    def parse(self):
        stmts = []
        while self.current()[0] != 'EOF':
            stmts.append(self.parse_statement())
        return Program(stmts)

    def parse_statement(self):
        tok = self.current()
        if tok[1] == 'let':
            self.consume('KEYWORD', 'let')
            name = self.consume('IDENTIFIER')
            self.consume('OP', '=')
            expr = self.parse_expression()
            self.consume('PUNCT', ';')
            return Let(name, expr)
        elif tok[1] == 'print':
            self.consume('KEYWORD', 'print')
            expr = self.parse_expression()
            self.consume('PUNCT', ';')
            return Print(expr)
        elif tok[1] == 'if':
            self.consume('KEYWORD', 'if')
            cond = self.parse_expression()
            self.consume('PUNCT', '{')
            body = []
            while self.current()[1] != '}':
                body.append(self.parse_statement())
            self.consume('PUNCT', '}')
            return If(cond, body)

    def parse_expression(self):
        node = self.parse_term()
        while self.current()[1] in ('+', '-', '>', '<', '=='):
            op = self.consume('OP')
            right = self.parse_term()
            node = BinOp(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current()[1] in ('*', '/'):
            op = self.consume('OP')
            right = self.parse_factor()
            node = BinOp(node, op, right)
        return node

    def parse_factor(self):
        tok = self.current()
        if tok[0] == 'NUMBER':
            return Num(int(self.consume('NUMBER')))
        elif tok[0] == 'IDENTIFIER':
            return Var(self.consume('IDENTIFIER'))
