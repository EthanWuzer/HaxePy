import sys
from token import Token

class RunTimeError(Exception):
    def __init__(self, token: Token, message: str) :
        super().__init__(message)
        self.token = token

class ParseError(Exception):
    def __init__(self,  message: str) :
        super().__init__(message)
