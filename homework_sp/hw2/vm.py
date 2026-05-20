class VM:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.stack = []
        self.env = {}
        self.ip = 0

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
                    continue
            self.ip += 1
