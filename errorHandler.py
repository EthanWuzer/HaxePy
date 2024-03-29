import sys

from tokens import Token
from tokenType import TokenType
from error import RuntimeError


class ErrorHandler:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True

    def error_on_token(self, token: Token, message: str):
        if token.type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, error: RuntimeError):
        print(f"[line {error.token.line}] Runtime error: {error.message}")
        self.had_runtime_error = True
