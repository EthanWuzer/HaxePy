import sys
from tokenType import TokenType
from tokens import Token
from error import ParseError
from errorHandler import ErrorHandler
from stmt import Stmt, Expression, Var, Block, If, While, Break, Print
from expr import Expr, Assign, BinaryExpr, ConditionalExpr, GroupingExpr, Call, LiteralExpr, LogicalExpr, UnaryExpr, VariableExpr


class Parser:

    def __init__(self, tokens: list[Token], error_handler: ErrorHandler):
        self.tokens = tokens
        self.current = 0
        self.error_handler = error_handler
        self.loop_depth = 0

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Stmt:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError as error:
            self.synchronize()
            return None

    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON,
                     "Expected ';' after variable declaration.")
        return Var(name, initializer)

    def statement(self) -> Stmt:

        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.BREAK):
            return self.break_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        else:
            return self.expression_statement()

    def print_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return Print(expr)

    def block(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end() and (not self.check(TokenType.RIGHT_BRACE)):
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def expression_statement(self) -> Expression:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return Expression(expr)

    def if_statement(self) -> If:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def while_statement(self) -> While:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        try:
            self.loop_depth += 1
            body = self.statement()
            return While(condition, body)
        finally:
            self.loop_depth -= 1

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")
        initializer = None
        if self.match(TokenType.VAR):
            initializer = self.var_declaration()
        elif not self.match(TokenType.SEMICOLON):
            initializer = self.expression_statement()
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")
        try:
            self.loop_depth += 1
            body = self.statement()
            if increment is not None:
                body = Block([body, Expression(increment)])
            if condition is None:
                condition = LiteralExpr(True)
            body = While(condition, body)
            if initializer is not None:
                body = Block([initializer, body])
                return body
        finally:
            self.loop_depth -= 1

    def break_statement(self) -> Break:
        if self.loop_depth == 0:
            self.error(self.previous(),
                       "Cannot use 'break' outside of a loop.")
        self.consume(TokenType.SEMICOLON, "Expected ';' after 'break'.")
        return Break()

    def expression(self) -> Expr:
        return self.comma_op()

    def comma_op(self) -> Expr:
        expr = self.assignment()
        while self.match(TokenType.COMMA):
            expr = BinaryExpr(expr, self.previous(), self.assignment())
        return expr

    def assignment(self) -> Expr:
        expr = self.conditional()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if type(expr) is VariableExpr:
                name = expr.name
                return Assign(name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def conditional(self) -> Expr:
        expr = self.orExpr()
        if self.match(TokenType.QUESTION):
            then_branch = self.orExpr()
            #self.consume(TokenType.COLON, " Expect ':' seperator after then branch in ternary conditional.")
            else_branch = self.orExpr()
            expr = ConditionalExpr(expr, then_branch, else_branch)
        return expr

    def orExpr(self) -> Expr:
        expr = self.andExpr()
        while self.match(TokenType.OR):
            expr = BinaryExpr(expr, self.previous(), self.andExpr())
        return expr

    def andExpr(self) -> Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            expr = BinaryExpr(expr, self.previous(), self.equality())
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            expr = BinaryExpr(expr, self.previous(), self.comparison())
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            expr = BinaryExpr(expr, self.previous(), self.term())
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            expr = BinaryExpr(expr, self.previous(), self.factor())
        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            expr = BinaryExpr(expr, self.previous(), self.unary())
        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            expr = UnaryExpr(self.previous(), self.unary())
        else:
            expr = self.call()
        return expr

    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def primary(self) -> Expr:
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        if self.match(TokenType.NULL):
            return LiteralExpr(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().literal)
        # grouping -> "(" expression ")"
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)
        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())
        # The following if clauses are productions for missing left operands - "error productions"
        if self.match(TokenType.COMMA):
            self.error(self.previous(), "Missing left-hand operand.")
            self.comma_op()
            return None
        if self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            self.error(self.previous(), "Missing left-hand operand.")
            self.equality()
            return None
        if self.match(TokenType.QUESTION):
            self.error(self.previous(),
                       "Missing condition expression for ternary conditional.")
            self.conditional()
            return None
        if self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            self.error(self.previous(), "Missing left-hand operand.")
            self.comparison()
            return None
        if self.match(TokenType.PLUS):
            self.error(self.previous(), "Missing left-hand operand.")
            self.term()
            return None
        if self.match(TokenType.SLASH, TokenType.STAR):
            self.error(self.previous(), "Missing left-hand operand.")
            self.factor()
            return None
        self.error_handler.error_on_token(self.peek(), "Expect expression.")

    # arguments -> expression ("," expression)*
    def finish_call(self, callee: Call) -> Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(
                        self.peek(), "Cant have more than 255 arguments. ")
                arguments.append(self.conditional())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN,
                             "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def match(self, *types) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def check_next(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        if self.tokens[self.current+1].type == TokenType.EOF:
            return False
        return self.tokens[self.current+1].type == type

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self) -> Token:
        return self.tokens[self.current-1]

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        self.error_handler.error_on_token(token, message)
        return ParseError("")

    def synchronize(self):
        self.advance()
        keywords = {TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR,
                    TokenType.IF, TokenType.WHILE,  TokenType.PRINT, TokenType.RETURN}
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in keywords:
                return
            self.advance()
