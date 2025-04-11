from abc import ABC, abstractmethod
from typing import Optional


class ICommandModel(ABC):
    @abstractmethod
    def add_char(self, char: str) -> None:
        pass

    @abstractmethod
    def delete_char(self) -> None:
        pass