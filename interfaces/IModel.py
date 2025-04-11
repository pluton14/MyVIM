from typing import List, Tuple, Any
from abc import ABC, abstractmethod


class IModel(ABC):

    @abstractmethod
    def get_data(self) -> Tuple[List[str], Tuple[int, int]]:
        pass

    @abstractmethod
    def insert_char(self, char: str) -> None:
        pass

    @abstractmethod
    def delete_char(self) -> None:
        pass

    @abstractmethod
    def move_cursor(self, x: int, y: int):
        pass

    @abstractmethod
    def save_file(self, filename: str) -> None:
        pass

    @abstractmethod
    def load_file(self, filename: str) -> None:
        pass

    @abstractmethod
    def get_cursor_pos(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def add_observer(self, self1, param):
        pass

    @abstractmethod
    def notify_observers(self, event_type: str, data: Any = None) -> None:
        pass

    @abstractmethod
    def set_status(self, text: str) -> None:
        pass

    @abstractmethod
    def set_command_buf(self, text: str) -> None:
        pass

    @abstractmethod
    def get_status(self) -> str:
        pass

    @abstractmethod
    def get_command_buf(self) -> str:
        pass

    @abstractmethod
    def get_modify(self) -> bool:
        pass

    @abstractmethod
    def set_cursor_pos(self, x: int, y: int):
        pass

    @abstractmethod
    def str_to_start(self) -> None:
        pass

    @abstractmethod
    def str_to_end(self) -> None:
        pass

    @abstractmethod
    def word_to_end(self) -> None:
        pass

    @abstractmethod
    def word_to_start(self) -> None:
        pass

    @abstractmethod
    def delete_char_inv(self) -> None:
        pass

    @abstractmethod
    def delete_word(self) -> None:
        pass

    @abstractmethod
    def copy_word(self) -> str:
        pass

    @abstractmethod
    def copy_str(self) -> str:
        pass

    @abstractmethod
    def delete_str(self) -> None:
        pass

    @abstractmethod
    def paste(self, copy_buffer: str):
        pass

    @abstractmethod
    def get_len(self) -> int:
        pass

    @abstractmethod
    def page_up(self, rows: int) -> None:
        pass

    @abstractmethod
    def page_down(self, rows: int) -> None:
        pass

    @abstractmethod
    def replace(self, char: str):
        pass

    @abstractmethod
    def find_after(self) -> None:
        pass

    @abstractmethod
    def find_before(self) -> None:
        pass

    @abstractmethod
    def search_string(self, word: str, forward: bool) -> None:
        pass
