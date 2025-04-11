from abc import ABC, abstractmethod
from typing import Tuple


class IViewAdapter(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def init_curses(self) -> None:
        pass

    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def clear_screen(self) -> None:
        pass

    @abstractmethod
    def add_str(self, x: int, y: int, text: str) -> None:
        pass

    @abstractmethod
    def move_cursor(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def refresh(self) -> None:
        pass

    @abstractmethod
    def get_char(self) -> int:
        pass

    @abstractmethod
    def end_curses(self) -> None:
        pass
