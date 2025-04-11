import curses
from typing import Tuple
from interfaces.IControllerAdapter import IControllerAdapter
from interfaces.IViewAdapter import IViewAdapter


class CursesAdapter(IControllerAdapter, IViewAdapter):

    def __init__(self) -> None:
        self.screen = curses.initscr()

    def init_curses(self) -> None:
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        curses.start_color()

    def get_screen_size(self) -> Tuple[int, int]:
        return self.screen.getmaxyx()

    def clear_screen(self) -> None:
        self.screen.clear()

    def add_str(self, x: int, y: int, text: str) -> None:
        self.screen.addstr(x, y, text)
        # curses.curs_set(0)
        # try:
        #     self.screen.addstr(y, x, text)
        # except curses.error:
        #     pass
        # curses.curs_set(1)

    def move_cursor(self, x: int, y: int) -> None:
        try:
            self.screen.move(y, x)
            #print(str(x) + " " + str(y))
        except curses.error:
            pass

    def refresh(self) -> None:
        self.screen.refresh()

    def get_char(self) -> int:
        return self.screen.getch()

    def end_curses(self) -> None:
        curses.endwin()
