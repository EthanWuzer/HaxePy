

import sys
from tokens import Token
from tokenType import TokenType
from errorHandler import ErrorHandler
from collections import namedtuple

DoubleToken = namedtuple("DoubleToken", "single, double")


class Scanner:
    def __init__(self, error_handler: ErrorHandler, source: str):
        self.error_handler = error_handler
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

        self.keywords = {
            "and": TokenType.AND,
            "break": TokenType.BREAK,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for:": TokenType.FOR,
            "if": TokenType.IF,
            "nil": TokenType.NULL,
            "or": TokenType.OR,
            "return": TokenType.RETURN,
            "print": TokenType.PRINT,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE
        }

        self.double_tokens = {
            "!": DoubleToken(TokenType.BANG, TokenType.BANG_EQUAL),
            "=": DoubleToken(TokenType.EQUAL, TokenType.EQUAL_EQUAL),
            "<": DoubleToken(TokenType.LESS, TokenType.LESS_EQUAL),
            ">": DoubleToken(TokenType.GREATER, TokenType.GREATER_EQUAL)
        }

        self.single_tokens = {
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            "-": TokenType.MINUS,
            "+": TokenType.PLUS,
            ";": TokenType.SEMICOLON,
            "*": TokenType.STAR
        }

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self):
        char = self.advance()
        if char in self.single_tokens:
            self.add_token(self.single_tokens.get(char))
        elif char in self.double_tokens:
            if(self.match('=')):
                self.add_token(self.double_tokens[char].double)
            else:
                self.add_token(self.double_tokens[char].single)

        elif char == '/':
            if self.peek() == '*':
                self.skip_comment()
            elif self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif char == '?':
            self.add_conditional()
        elif char in ['', '\r', '\t', ' ']:
            pass
        elif char == '\n':
            self.line += 1
        elif char == '"':
            self.string()
        elif self.is_digit(char):
            self.number()
        elif self.is_alpha(char):
            self.identifier()
        else:
            self.error_handler.error(self.line, "Unexpected character.")

    def advance(self) -> chr:
        char = self.peek()
        self.current += 1
        return char

    def add_token(self, token_type: TokenType, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def match(self, char: chr) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != char:
            return False
        self.current += 1
        return True

    def peek(self) -> chr:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_at_end():
            self.error_handler.error(self.line, "Unterminated string.")
            return None
        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def is_digit(self, char: chr) -> bool:
        return char >= '0' and char <= '9'

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        self.add_token(TokenType.NUMBER, float(
            self.source[self.start:self.current]))

    def peek_next(self) -> chr:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def is_alpha(self, char: chr) -> chr:
        return (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z') or char == '_'

    def is_alpha_numeric(self, char: chr) -> chr:
        return self.is_alpha(char) or self.is_digit(char)

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        type = TokenType.IDENTIFIER
        if text in self.keywords:
            type = self.keywords[text]
        self.add_token(type)

    def skip_comment(self):
        comment_lines = [self.line]
        nesting = 1
        while nesting > 0:
            if self.is_at_end():
                for line in comment_lines:
                    self.error_handler.error(line, "Unterminated comment.")
                return
            if self.peek() == '\n':
                self.line += 1
            if self.peek() == '/' and self.peek_next() == '*':
                comment_lines.append(self.line)
                nesting += 1
            if self.peek() == '*' and self.peek_next() == '/':
                nesting -= 1
                self.advance()
                self.advance()
            self.advance()

    def add_conditional(self):
        self.add_token(token_type=TokenType.QUESTION)
        while not self.match(':'):
            if self.is_at_end():
                self.error_handler.error(
                    self.line, "Unterminated conditional.")
                return
            self.start = self.current
            self.scan_token()
        self.current -= 1
        self.advance()
