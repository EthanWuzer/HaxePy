import sys

from token import Token
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