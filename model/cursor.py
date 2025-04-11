from typing import Tuple, List

from interfaces.ICursor import ICursor


class Cursor(ICursor):
    def __init__(self):
        self._cursor_pos = (0, 0)

    def get_pos(self) -> Tuple[int, int]:
        return self._cursor_pos

    def set_pos(self, x: int, y: int) -> None:
        self._cursor_pos = (x, y)
        #print(str(x) + " " + str(y))

    def move_cursor(self, dx: int, dy: int, lines: List) -> None:
        new_y = max(0, min(self._cursor_pos[1] + dy, len(lines) - 1))
        current_line_len = len(lines[new_y])
        new_x = max(0, min(self._cursor_pos[0] + dx, current_line_len))
        self.set_pos(new_x, new_y)
        #self._notify_observers()