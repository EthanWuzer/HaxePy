from tokenType import TokenType

class Token():
    def __init__(self, type: int, lexeme: str, literal: object, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        
    def __str__(self):
        return f"{self.lexeme} {self.literal} {self.line}"