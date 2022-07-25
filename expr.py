from abc import ABC, abstractmethod
from typing import Any
from tokens import Token


class Expr:
    pass


class Assign(Expr):
    def __init__(self, name: str, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)


class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


class ConditionalExpr(Expr):
    def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_conditional_expr(self)


class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


class LiteralExpr(Expr):
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


class LogicalExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_logical_expr(self)


class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


class VariableExpr(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)


class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, args: list[Expr]):
        self.callee = callee
        self.paren = paren
        self.args = args
