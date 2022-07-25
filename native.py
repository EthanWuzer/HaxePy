import time
from typing import List, Any
from abc import ABC, abstractmethod
from callable import Callable
from tokens import Token
from error import LoxRunTimeError


class Print(Callable):
    def call(self, interpreter, arguments: list[Any]):
        message = arguments[0]
        message = interpreter.stringify(message)
        print(message)

    def arity(self):
        return 1
