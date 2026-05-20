import re

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
