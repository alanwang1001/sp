import re

# ==========================================
# 1. 詞法分析器 (Lexer)
# 負責將原始碼字串轉換成一個個的 Token
# ==========================================
TOKEN_TYPES = [
    ('KEYWORD', r'\b(let|if|print)\b'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER', r'\d+'),
    ('OP', r'[+\-*/><]|==|='),
    ('PUNCT', r'[;{}]'),
    ('SKIP', r'[ \t\n\r]+'),
]

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.tokenize()

    def tokenize(self):
        pos = 0
        while pos < len(self.code):
            match = None
            for token_type, regex in TOKEN_TYPES:
                regex_match = re.match(regex, self.code[pos:])
                if regex_match:
                    value = regex_match.group(0)
                    if token_type != 'SKIP':
                        self.tokens.append((token_type, value))
                    pos += len(value)
                    match = True
                    break
            if not match:
                raise SyntaxError(f"Lexer 錯誤：無法解析的字元 '{self.code[pos]}'")
        self.tokens.append(('EOF', ''))

# ==========================================
# 2. 抽象語法樹節點 (AST Nodes)
# ==========================================
class ASTNode: pass
class Program(ASTNode):
    def __init__(self, stmts): self.stmts = stmts
class Let(ASTNode):
    def __init__(self, name, expr): self.name, self.expr = name, expr
class Print(ASTNode):
    def __init__(self, expr): self.expr = expr
class If(ASTNode):
    def __init__(self, cond, body): self.cond, self.body = cond, body
class BinOp(ASTNode):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
class Var(ASTNode):
    def __init__(self, name): self.name = name
class Num(ASTNode):
    def __init__(self, value): self.value = value

# ==========================================
# 3. 語法分析器 (Parser)
# 負責將 Tokens 轉換成 AST (遞迴下降法)
# ==========================================
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
        # 處理加減法與條件比較
        node = self.parse_term()
        while self.current()[1] in ('+', '-', '>', '<', '=='):
            op = self.consume('OP')
            right = self.parse_term()
            node = BinOp(node, op, right)
        return node

    def parse_term(self):
        # 處理乘除法 (優先級高於加減法)
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

# ==========================================
# 4. 編譯器 (Compiler)
# 將 AST 轉換為堆疊虛擬機的中間碼 (Bytecode)
# ==========================================
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
            self.bytecode.append(['JMP_IF_FALSE', 0]) # 預留跳轉位置 (用 List 方便修改)
            for stmt in node.body:
                self.compile(stmt)
            self.bytecode[jump_idx][1] = len(self.bytecode) # 回填正確的跳轉位址
        elif isinstance(node, BinOp):
            self.compile(node.left)
            self.compile(node.right)
            self.bytecode.append(('OP', node.op))
        elif isinstance(node, Var):
            self.bytecode.append(('LOAD', node.name))
        elif isinstance(node, Num):
            self.bytecode.append(('PUSH', node.value))
        return self.bytecode

# ==========================================
# 5. 堆疊虛擬機 (Stack VM)
# 負責執行 Bytecode
# ==========================================
class VM:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.stack = []
        self.env = {} # 變數儲存區
        self.ip = 0   # 指令指標 (Instruction Pointer)

    def run(self):
        while self.ip < len(self.bytecode):
            instr = self.bytecode[self.ip]
            op = instr[0]

            if op == 'PUSH':
                self.stack.append(instr[1])
            elif op == 'STORE':
                self.env[instr[1]] = self.stack.pop()
            elif op == 'LOAD':
                self.stack.append(self.env[instr[1]])
            elif op == 'PRINT':
                print(f"[VM 輸出] {self.stack.pop()}")
            elif op == 'OP':
                b = self.stack.pop()
                a = self.stack.pop()
                operator = instr[1]
                if operator == '+': self.stack.append(a + b)
                elif operator == '-': self.stack.append(a - b)
                elif operator == '*': self.stack.append(a * b)
                elif operator == '/': self.stack.append(a // b)
                elif operator == '>': self.stack.append(1 if a > b else 0)
                elif operator == '<': self.stack.append(1 if a < b else 0)
                elif operator == '==': self.stack.append(1 if a == b else 0)
            elif op == 'JMP_IF_FALSE':
                cond = self.stack.pop()
                if cond == 0:
                    self.ip = instr[1]
                    continue # 直接跳轉，不遞增 ip
            self.ip += 1

# ==========================================
# 6. 測試執行
# ==========================================
if __name__ == '__main__':
    source_code = """
    let x = 10;
    let y = 5;
    let result = x + y * 2;

    if result > 15 {
        print result;
    }
    """

    print("1. 原始碼:")
    print(source_code.strip())
    
    # 管線運作
    tokens = Lexer(source_code).tokens
    ast = Parser(tokens).parse()
    bytecode = Compiler().compile(ast)

    print("\n2. 編譯後的 Bytecode (指令, 參數):")
    for i, instr in enumerate(bytecode):
        print(f"{i:02d}: {instr}")

    print("\n3. 虛擬機執行結果:")
    VM(bytecode).run()
