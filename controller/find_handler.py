from curses_adapter import CursesAdapter
from interfaces.IControllerAdapter import IControllerAdapter
from model.model import IModel
from my_string import my_string as MyString
from interfaces.ICommandState import ICommandState


class FindHandler(ICommandState):
    def __init__(self, model: IModel, adapter: IControllerAdapter):
        self._adapter = adapter
        self._model = model
        self._buffer = MyString("")
        self._active = False
        self._search = False
        self._search_forward = True  # True для /, False для ?
        self._last_search = ""

    @property
    def buffer(self) -> str:
        return self._buffer.c_str()

    @property
    def is_active(self) -> bool:
        return self._active

    def activate(self, forward: bool = True) -> None:
        self._active = True
        self._search_forward = forward
        self._buffer = MyString("")
        self._update_display()
        self._model.notify_observers("text_changed", "")

    def deactivate(self) -> None:
        self._active = False
        self._model.search = False
        self._model.notify_observers("text_changed", "")
        self._model.set_command_buf("")

    def handle_input(self, char: int) -> None:
        if self._model.search:
            # Обработка команд n/N без активации
            if char == ord('n'):
                self._search_forward = True
                self._model.search_string(self._last_search, self._search_forward)
            elif char == ord('N'):
                self._search_forward = False
                self._model.search_string(self._last_search, self._search_forward)
            else:
                self._model.search = False
            self._model.notify_observers("cursor_moved", "")
            return

        if char == 27:  # ESC
            self.deactivate()
        elif char == 10:  # Enter
            self._execute_command()
        elif char == 8:  # Backspace
            self._delete_char()
        elif 32 <= char <= 256:
            self._add_char(chr(char))

    def _add_char(self, char: str) -> None:
        self._buffer = MyString(self.buffer + char)
        self._update_display()

    def _delete_char(self) -> None:
        if len(self._buffer) > 0:
            new_len = self._buffer.size() - 1
            self._buffer = MyString(self._buffer.substr(0, new_len))
            self._update_display()

    def _update_display(self):
        self._model.search = False
        self._model.set_command_buf(self._get_prompt() + self.buffer)
        rows, cols = self._adapter.get_screen_size()
        self._adapter.move_cursor(rows - 1, 1 + len(self.buffer))
        self._model.notify_observers("text_changed", "")

    def _get_prompt(self):
        return "?" if self._search_forward else "/"

    def _execute_command(self):
        self._last_search = self.buffer
        self._model.search_string(self._last_search, self._search_forward)
        self._model.search = True
        # if self._search_forward:
        #     self._model.find_after()
        # else:
        #     self._model.find_before()
