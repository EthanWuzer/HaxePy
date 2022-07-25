import sys
from tokens import Token


class RuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


class ParseError(Exception):
    def __init__(self,  message: str):
        super().__init__(message)


class LoxRunTimeError(RuntimeError):
    def __init__(self, token: Token, message):
        super().__init__(token, message)


class DivisionByZeroError(LoxRunTimeError):
    def __init__(self, token: Token):
        super().__init__(token, "Division by zero.")


class BreakException(Exception):
    def __init__(self):
        pass


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
