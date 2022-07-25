from msilib.schema import Condition
import sys
import operator
from typing import Any
from visitor import Visitor
from environment import Environment
from tokenType import TokenType
from tokens import Token
from error import ParseError, LoxRunTimeError, DivisionByZeroError, BreakException, ReturnException
from runMode import RunMode
from errorHandler import ErrorHandler
from stmt import Stmt, Expression, Var, Block, If, While, Break, Print
from expr import Expr, Assign, BinaryExpr, ConditionalExpr, GroupingExpr, Call, LiteralExpr, LogicalExpr, UnaryExpr, VariableExpr


class Interpreter(Visitor):
    unititialized = object()
    op_dic = {
        TokenType.LESS: operator.lt,
        TokenType.LESS_EQUAL: operator.le,
        TokenType.GREATER: operator.gt,
        TokenType.GREATER_EQUAL: operator.ge,
        TokenType.MINUS: operator.sub,
        TokenType.SLASH: operator.truediv,
        TokenType.STAR: operator.mul,
        TokenType.EQUAL_EQUAL: operator.eq,
        TokenType.BANG_EQUAL: operator.ne,
    }

    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.globals = {}
        self.environment = None
        # self.globals['clock'] = Clock()
        # self.globals['read'] = Read()
        # self.globals['array'] = Array()
        self.locals = {}
        self.slots = {}

    def interpret(self, statements: list[Stmt], mode: RunMode):
        try:
            for statement in statements:
                self.executeByMode(statement, mode)
        except ParseError as e:
            self.error_handler.error(e.token, e.message)

    def visit_print_stmt(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(value)

    def executeByMode(self, statement: Stmt, mode: RunMode):
        if mode == RunMode.REPL and type(statement) == Expression and type(statement.expression) is not Assign:
            value = self.evaluate(statement.expr)
            print(self.stringify(value))
        else:
            self.execute(statement)

    def execute(self, statement: Stmt):
        statement.accept(self)

    def resolve(self, expr: Expr, depth: int, slot: int):
        self.locals[expr] = depth
        self.slots[expr] = slot

    def visit_var_stmt(self, stmt: Var):
        value = Interpreter.unititialized
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.define(stmt.name.lexeme, value)

    def visit_expression_stmt(self, stmt: Expression):
        expr = self.evaluate(stmt.expression)

    def visit_block_stmt(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_if_stmt(self, stmt: If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_while_stmt(self, stmt: While):
        try:
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        except ParseError as e:
            self.error_handler.error(e.token, e.message)

    def visit_break_stmt(self, stmt: Break):
        raise Break()

    def visit_variable_expr(self, expr: VariableExpr):
        return self.look_up_variable(expr.name, expr)

    def visit_assign_expr(self, expr: Assign):
        value = self.evaluate(expr.value)
        if expr in self.locals:
            self.environment.assign_at(
                self.locals[expr], self.slots[expr], value)
        else:
            if expr.name.lexeme in self.globals:
                self.globals[expr.name.lexeme] = value
            else:
                raise LoxRunTimeError(
                    expr.name, "Undefined variable!")
        return value

    def visit_literal_expr(self, expr: Expr):
        return expr.value

    def visit_grouping_expr(self, expr: GroupingExpr):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)
        if expr.operator.type == TokenType.MINUS:
            value = -float(right)
            value = int(value) if value.is_integer() else value
            return value
        if expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)

    def visit_binary_expr(self, expr: BinaryExpr) -> str:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, left, right)
            value = float(left) - float(right)
            value = int(value) if value.is_integer() else value
            return value
        elif expr.operator.type == TokenType.STAR:
            self.check_number_operand(expr.operator, left, right)
            value = float(left) * float(right)
            value = int(value) if value.is_integer() else value
            return value
        elif expr.operator.type == TokenType.SLASH:
            if self.legal_divisor(expr.operator, right):
                self.check_number_operand(expr.operator, left, right)
                value = float(left) / float(right)
                value = int(value) if value.is_integer() else value
                return value
        elif expr.operator.type == TokenType.PLUS:
            '''
            Notice that because of Pythons dynamic typing, we didnt have to check for types,
            but we did so for learning purposes.
            '''
            if (type(left) is float or type(left) is int) and (type(right) is float or type(right) is int):
                value = float(left) + float(right)
                value = int(value) if value.is_integer() else value
                return value
            elif type(left) is str or type(right) is str:
                value = self.stringify(left)+self.stringify(right)
                return value
            raise LoxRunTimeError(
                expr.operator, "Operands must either strings or numbers.")
        elif expr.operator.type in Interpreter.op_dic:
            op_func = Interpreter.op_dic[expr.operator.type]
            self.check_comparison_operands(expr.operator, left, right)
            return op_func(left, right)
        elif expr.operator.type == TokenType.COMMA:
            return right
        return None

    def visit_conditional_expr(self, expr: ConditionalExpr) -> str:
        condition = self.evaluate(expr.condition)
        then_branch = self.evaluate(expr.then_branch)
        else_branch = self.evaluate(expr.else_branch)
        if self.is_truthy(condition):
            return then_branch
        else:
            return else_branch

    def visit_logical_expr(self, expr: LogicalExpr):
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
            else:
                return self.evaluate(expr.right)

    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def is_truthy(self, expression):
        if expression is None:
            return False
        if type(expression) is bool:
            return expression
        return True

    def look_up_variable(self, name: Token, expr: Expr):
        if expr in self.locals:
            value = self.environment.get_at(
                self.locals[expr], self.slots[expr])
        elif name.lexeme in self.globals:
            value = self.globals[name.lexeme]
        else:
            raise LoxRunTimeError(name, f"Undefined variable {name.lexeme}.")
        if value == Interpreter.unititialized:
            raise LoxRunTimeError(
                name, f"Variable {name.lexeme} is not initialized.")
        return value

    def check_number_operand(self, operator: Token, *args):
        for arg in args:
            if type(arg) is not float and type(arg) is not int:
                raise LoxRunTimeError(operator, "Operand must be a number.")

    def stringify(self, value: any) -> str:
        if value is None:
            return "nil"
        if type(value) is float:
            text = str(value)
            if text.endswith(".0") or value.is_integer():
                text = text[0:len(text)-2]
            return text
        return str(value)

    def legal_divisor(self, operator: Token, divisor: float) -> bool:
        if divisor == 0:
            raise DivisionByZeroError(operator)
            return False
        return True

    def define(self, name: str, value: Any):
        if self.environment is not None:
            self.environment.define(value)
        else:
            self.globals[name] = value

    def check_comparison_operands(self, operator: Token, *args):
        all_string = True
        all_num = True
        for arg in args:
            if type(arg) is not str:
                all_string = False
            if type(arg) is not float and type(arg) is not int:
                all_num = False
        if all_string == False and all_num == False:
            raise LoxRunTimeError(
                operator, "Operands must be strings or numbers.")
