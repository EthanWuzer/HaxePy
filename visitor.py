from abc import ABC, abstractmethod
#from stmt import Stmt, Expression,Print, Var, Block, If, While, Break, Fun, Return, Class
from stmt import Stmt, Expression, Var, Block, If, While, Break, Print
from expr import Expr, Assign, BinaryExpr, ConditionalExpr, GroupingExpr, LiteralExpr, LogicalExpr, UnaryExpr, VariableExpr


class Visitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: Assign):
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: BinaryExpr):
        pass

    @abstractmethod
    def visit_conditional_expr(self, expr: ConditionalExpr):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: GroupingExpr):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Expr):
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: LogicalExpr):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: UnaryExpr):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: VariableExpr):
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression):
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: Var):
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: Block):
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: If):
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: While):
        pass

    @abstractmethod
    def visit_break_stmt(self, stmt: Break):
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: Print):
        pass
