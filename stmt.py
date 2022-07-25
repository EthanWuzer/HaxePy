from abc import ABC, abstractmethod
from expr import Expr
from tokens import Token


class Stmt:
    pass


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class Var(Stmt):
    def __init__(self, name: str, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)


class Block(Stmt):
    def __init__(self, statements: list):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)


class Break(Stmt):
    def __init__(self):
        pass

    def accept(self, visitor):
        return visitor.visit_break_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)
