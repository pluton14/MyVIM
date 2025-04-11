import sys

from curses_adapter import CursesAdapter
from interfaces.IControllerAdapter import IControllerAdapter
from model.model import IModel
from my_string import my_string as MyString

from interfaces.ICommandState import ICommandState


class CommandHandler(ICommandState):
    def __init__(self, model: IModel, adapter: IControllerAdapter):
        self._adapter = adapter
        self._model = model
        self._buffer = MyString("")
        self._active = False
        self._filename = ""
        #self._observers: List[CommandHandlerObserver] = []

    @property
    def buffer(self) -> str:
        return self._buffer.substr(0)

    @property
    def is_active(self) -> bool:
        return self._active

    # def add_observer(self, observer: CommandHandlerObserver) -> None:
    #     self._observers.append(observer)
    #     for observer in self._observers:
    #         observer.on_command_handler_deactivated()

    def activate(self) -> None:
        self._active = True
        self._buffer = MyString("")
        self._model.notify_observers("text_changed", "")

    def deactivate(self) -> None:
        self._active = False
        self._model.notify_observers("text_changed", "")

    def handle_input(self, char: int) -> None:
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
        self._model.set_command_buf(self._buffer.c_str())
        rows, cols = self._adapter.get_screen_size()
        self._adapter.move_cursor(rows - 1, len(self.buffer+char)+1)

    def _delete_char(self) -> None:
        if len(self._buffer) > 0:
            # now_buffer = self._buffer.c_str()
            # if len(now_buffer) > 0:
            #     now_buffer = now_buffer[:-1]
            now_len = self._buffer.size()
            new_buffer = self._buffer.substr(0, now_len-1)
            self._buffer = MyString(new_buffer)
            self._model.set_command_buf(self._buffer.c_str())

    def _execute_command(self) -> None:
        try:
            # Ручной парсинг команды
            buffer_str = self._buffer.c_str()
            cmd_parts = []
            start = 0
            in_quotes = False

            for i, c in enumerate(buffer_str):
                if c == ' ' and not in_quotes:
                    if start < i:
                        cmd_parts.append(buffer_str[start:i])
                    start = i + 1
                elif c == '"':
                    in_quotes = not in_quotes

            if start < len(buffer_str):
                cmd_parts.append(buffer_str[start:])

            # Обработка команд
            if len(cmd_parts) == 0:
                return

            if cmd_parts[0] == 'w' and len(cmd_parts) > 1:
                self._model.save_file(cmd_parts[1])
                self._filename = cmd_parts[1]
            elif cmd_parts[0] == 'o' and len(cmd_parts) > 1:
                self._model.load_file(cmd_parts[1])
                self._filename = cmd_parts[1]
            elif cmd_parts[0] == 'q!' and len(cmd_parts) == 1:
                sys.exit(0)
            elif cmd_parts[0] == 'w' and len(cmd_parts) == 1:
                if self._filename != "":
                    self._model.save_file(self._filename)
            elif (cmd_parts[0] == 'wq!' or cmd_parts[0] == 'x') and len(cmd_parts) == 1:
                if self._filename != "":
                    self._model.save_file(self._filename)
                sys.exit(0)
            elif cmd_parts[0] == 'q' and len(cmd_parts) == 1:
                if not self._model.get_modify():
                    sys.exit(0)
            elif cmd_parts[0] == 'number' and len(cmd_parts) > 1:
                self._model.set_cursor_pos(0, int(cmd_parts[1])-1)
            elif cmd_parts[0] == 'h' and len(cmd_parts) == 1:
                self._model.load_file("helper.txt")
            else:
                raise RuntimeError("Unknown command")

        except Exception as e:
            raise RuntimeError(f"Command error: {str(e)}")
        finally:
            self.deactivate()
            self._model.set_command_buf("")
