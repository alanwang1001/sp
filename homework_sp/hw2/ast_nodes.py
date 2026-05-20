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
