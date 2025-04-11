from typing import List, Tuple, Any
from my_string import my_string as MyString
from abc import ABC, abstractmethod
from event_manager import EventManager
from interfaces.ICursor import ICursor
from interfaces.IModel import IModel
from interfaces.event_listener import EventListener
from model.cursor import Cursor


class Observer(ABC):
    @abstractmethod
    def update(self) -> None:
        pass


class Model(IModel):
    def __init__(self) -> None:
        self._lines: List[MyString] = [MyString("")]
        self._observers: List[Observer] = []
        self._cursor: ICursor = Cursor()
        self._event_manager = EventManager()
        self.command_buf = ""
        self.status = "normal"
        self.modify = False
        self.search = False

    def get_len(self) -> int:
        return len(self._lines)

    def move_cursor(self, x: int, y: int) -> None:
        # print(str(x) + " " + str(y))
        self._cursor.move_cursor(x, y, self._lines)
        self.notify_observers("cursor_moved")

    def set_command_buf(self, text: str) -> None:
        self.command_buf = text

    def get_command_buf(self) -> str:
        return self.command_buf

    def set_status(self, text: str):
        self.status = text

    def get_status(self) -> str:
        return self.status

    def get_cursor_pos(self) -> Tuple[int, int]:
        return self._cursor.get_pos()

    def set_cursor_pos(self, x: int, y: int) -> None:
        self._cursor.set_pos(x, y)

    def get_modify(self) -> bool:
        return self.modify

    def event_manager(self) -> EventManager:
        return self._event_manager

    def get_word_info(self):
        now_x, now_y = self.get_cursor_pos()
        i = j = now_x
        line = self._lines[now_y].c_str()
        while i > 0 and line[i] != ' ':
            i -= 1
        while j < len(line) and line[j] != ' ':
            j += 1
        if i == j:
            return -1, -1
        return i, j

    def replace(self, char: str) -> None:
        self.modify = True
        now_x, now_y = self.get_cursor_pos()
        now_line = self._lines[now_y]
        now_line.replace(now_x, 1, char)
        self._lines[now_y] = now_line
        self.notify_observers("text_changed")

    def str_to_start(self) -> None:
        now_x, now_y = self.get_cursor_pos()
        self.set_cursor_pos(0, now_y)
        self.notify_observers("cursor_moved")

    def str_to_end(self) -> None:
        now_x, now_y = self.get_cursor_pos()
        now_line = self._lines[now_y].c_str()
        self.set_cursor_pos(len(now_line), now_y)
        self.notify_observers("cursor_moved")

    def word_to_end(self) -> None:
        now_x, now_y = self.get_cursor_pos()
        now_line = self._lines[now_y]
        word_a, word_b = self.get_word_info()
        if word_b != -1:
            self.set_cursor_pos(word_b, now_y)
            self.notify_observers("cursor_moved")

    def word_to_start(self) -> None:
        now_x, now_y = self.get_cursor_pos()
        now_line = self._lines[now_y]
        word_a, word_b = self.get_word_info()
        if word_a != -1:
            self.set_cursor_pos(word_a + 1, now_y)
            self.notify_observers("cursor_moved")

    def delete_str(self) -> None:
        self.modify = True
        now_x, now_y = self.get_cursor_pos()
        now_line = self._lines.pop(now_y)
        self.notify_observers("text_changed")

    def delete_word(self) -> None:
        self.modify = True
        x, now_y = self.get_cursor_pos()
        s = self._lines[now_y].c_str()
        if x < 0 or x >= len(s) or s[x] == " ":
            return
        start = x
        while start > 0 and s[start - 1] != " ":
            start -= 1
        end = x
        while end < len(s) and s[end] != " ":
            end += 1
        if end < len(s) and s[end] == " ":
            end += 1
        new_str = s[:start] + s[end:]
        self._lines[now_y] = MyString(new_str)

    def copy_word(self) -> str:
        now_x, now_y = self.get_cursor_pos()
        begin_word_pos, end_word_pos = self.get_word_info()
        line = self._lines[now_y]
        return line.substr(begin_word_pos, end_word_pos - begin_word_pos).c_str()

    def copy_str(self) -> str:
        now_x, now_y = self.get_cursor_pos()
        return self._lines[now_y].c_str()

    def paste(self, copy_buffer: str) -> None:
        self.modify = True
        now_x, now_y = self.get_cursor_pos()
        line = self._lines[now_y]
        line.insert(now_x, str(copy_buffer))
        self._lines[now_y] = line
        self.set_cursor_pos(now_x, now_y)
        self.notify_observers("text_changed")

    def page_up(self, rows: int) -> None:
        now_x, now_y = self.get_cursor_pos()
        new_y = now_y - rows
        new_y = max(0, new_y)
        self._cursor.set_pos(0, new_y)
        self.notify_observers("cursor_moved")

    def page_down(self, rows: int) -> None:
        now_x, now_y = self.get_cursor_pos()
        new_y = now_y + rows
        new_y = min(len(self._lines) - 1, new_y)
        self._cursor.set_pos(0, new_y)
        self.notify_observers("cursor_moved")

    def add_observer(self, listener: EventListener, event_type: str) -> None:
        self._event_manager.subscribe(event_type, listener)
        self.notify_observers("text_changed")

    def notify_observers(self, event_type: str, data: Any = None) -> None:
        self._event_manager.notify(self, event_type, data)

    def get_data(self) -> Tuple[List[str], Tuple[int, int]]:
        cursor_pos = self._cursor.get_pos()
        return [line.c_str() for line in self._lines], cursor_pos

    def insert_char(self, char: str) -> None:
        self.modify = True
        x, y = self._cursor.get_pos()
        current_line = self._lines[y]

        if char == '\n':
            left_part = current_line.substr(0, x)
            right_part = current_line.substr(x)

            self._lines[y] = MyString(left_part)
            self._lines.insert(y + 1, MyString(right_part))

            self._cursor.set_pos(0, y + 1)
        else:
            new_content = current_line.substr(0, x) + char + current_line.substr(x)
            self._lines[y] = MyString(new_content)
            self._cursor.move_cursor(1, 0, self._lines)

        self.notify_observers("text_changed")

    def delete_char(self) -> None:
        self.modify = True
        x, y = self._cursor.get_pos()
        if x == 0 and y == 0:
            return

        if x == 0:
            prev_line = self._lines[y - 1]
            current_line = self._lines[y]

            merged_content = prev_line.substr(0) + current_line.substr(0)
            self._lines[y - 1] = MyString(merged_content)
            del self._lines[y]

            self._cursor.set_pos(len(prev_line), y - 1)
            #self.move_cursor(-1, len(prev_line))
        else:
            current_line = self._lines[y]
            new_content = current_line.substr(0, x - 1) + current_line.substr(x)
            self._lines[y] = MyString(new_content)
            self._cursor.move_cursor(-1, 0, self._lines)

        self.notify_observers("text_changed")

    def delete_char_inv(self) -> None:
        self.modify = True
        x, y = self._cursor.get_pos()
        current_line = self._lines[y] if y < len(self._lines) else None

        if y >= len(self._lines) or (x == len(current_line) and y == len(self._lines) - 1):
            return

        if x == len(current_line):
            next_line = self._lines[y + 1]
            merged_content = current_line.substr(0) + next_line.substr(0)
            self._lines[y] = MyString(merged_content)
            del self._lines[y + 1]
        else:
            new_content = current_line.substr(0, x + 1) + current_line.substr(x + 2)
            self._lines[y] = MyString(new_content)

        self._cursor.set_pos(x, y)
        self.notify_observers("text_changed")

    def save_file(self, filename: str) -> None:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for line in self._lines:
                    content = line.c_str()
                    f.write(content + '\n')
            self.modify = False
        except Exception as e:
            raise RuntimeError(f"Save error: {str(e)}")

    def load_file(self, filename: str) -> None:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self._lines = [
                    MyString(line.rstrip('\n'))
                    for line in f.readlines()
                ]
                if not self._lines:
                    self._lines = [MyString("")]
                self._cursor.set_pos(0, 0)
                self.notify_observers("text_changed")
            self.modify = False
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {filename}")
        except Exception as e:
            raise RuntimeError(f"Load error: {str(e)}")

    def search_string(self, word: str, forward: bool):
        if not self._lines or not word:
            return
        now_len = len(self._lines)
        now_x, now_y = self._cursor.get_pos()
        start_y = now_y + (1 if forward else -1)
        range_y = range(start_y, now_len) if forward else range(start_y, -1, -1)
        line = self._lines[now_y].c_str()
        line_left = line[:now_x]
        line_right = line[now_x + 1:]
        pos = line_right.find(word) if forward else line_left.rfind(word)
        if pos != -1:
            self.set_cursor_pos(pos+len(line_left)+1, now_y) if forward else self.set_cursor_pos(pos, now_y)
            return
        for y in range_y:
            line = self._lines[y].c_str()
            pos = line.find(word) if forward else line.rfind(word)

            if pos != -1:
                self.set_cursor_pos(pos, y)
                return

    def find_after(self) -> None:
        pass

    def find_before(self) -> None:
        pass
