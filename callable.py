from abc import ABC, abstractmethod
from typing import Any, List


class Callable:
    @abstractmethod
    def call(self, interpreter, arguments: list[Any]):
        pass

    @abstractmethod
    def arity(self):
        pass
