from abc import ABC, abstractmethod
from typing import Tuple, List


class ICursor(ABC):

    @abstractmethod
    def get_pos(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def set_pos(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def move_cursor(self, dx: int, dy: int, lines: List) -> None:
        pass
