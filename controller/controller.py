import curses
from typing import Dict, Any
from abc import ABC, abstractmethod
from my_string import my_string as MyString
from controller.command_handler import CommandHandler
from controller.find_handler import FindHandler
from curses_adapter import CursesAdapter
from interfaces.ICommandState import ICommandState
from interfaces.IControllerAdapter import IControllerAdapter
from model.model import IModel

KEY_LEFT = 260
KEY_RIGHT = 261
KEY_UP = 259
KEY_DOWN = 258
PAGE_UP = 57
PAGE_DOWN = 51

class IController(ABC):
    @abstractmethod
    def handle_input(self) -> None:
        pass


class VimController(IController):
    def __init__(self, model: IModel, adapter: IControllerAdapter) -> None:
        self.model = model
        self._adapter = adapter
        self.modes = ['normal', 'insert', 'command']
        self.current_mode = 'normal'
        self._command_buffer = MyString("")
        self.command_map = self._create_command_map()
        self.find_handler = FindHandler(model, adapter)
        self.command_handler = CommandHandler(model, adapter)
        self.normal_buffer = "aaa"
        self.numbers_buffer = ""
        self.copy_buffer = ""
        self.state: ICommandState

    @property
    def command_buffer(self) -> str:
        return self._command_buffer.c_str()

    def _execute_command(self) -> None:
        try:
            cmd = self._command_buffer.substr(0)
            if cmd.startswith('w '):
                filename = cmd[2:].strip()
                self.model.save_file(filename)
            elif cmd.startswith('o '):
                filename = cmd[2:].strip()
                self.model.load_file(filename)
            else:
                raise RuntimeError("Unknown command")
        except Exception as e:
            self._show_error(str(e))
        finally:
            self._cancel_command()

    def _create_command_map(self) -> Dict[str, Any]:
        return {
            'normal': {
                ord('^'): lambda: self.model.str_to_start(),
                ord('$'): lambda: self.model.str_to_end(),
                ord('w'): lambda: self.model.word_to_end(),
                ord('b'): lambda: self.model.word_to_start(),
                ord('G'): lambda: self.file_to_end(),
                ord('x'): lambda: self.model.delete_char_inv(),
                ord('p'): lambda: self.paste(),
                ord('i'): self._enter_insert_mode,
                ord('I'): self._enter_insert_mode_start_str,
                ord('A'): self._enter_insert_mode_finish_str,
                ord('S'): self._enter_insert_mode_delete_str,
                ord('r'): self.replace,
                ord(':'): self._enter_command_mode,
                ord('/'): lambda: self._enter_find_mode(True),
                ord('?'): lambda: self._enter_find_mode(False),
                8: self.model.delete_char,  # Backspace
                KEY_LEFT: lambda: self.model.move_cursor(-1, 0),
                KEY_RIGHT: lambda: self.model.move_cursor(1, 0),
                KEY_UP: lambda: self.model.move_cursor(0, -1),
                KEY_DOWN: lambda: self.model.move_cursor(0, 1),
                PAGE_UP: lambda: self.model.page_up(self._adapter.get_screen_size()[0]),
                PAGE_DOWN: lambda: self.model.page_down(self._adapter.get_screen_size()[0]),
            },
            'insert': {
                27: self._enter_normal_mode,  # ESC
                8: self.model.delete_char,  # Backspace
                KEY_LEFT: lambda: self.model.move_cursor(-1, 0),
                KEY_RIGHT: lambda: self.model.move_cursor(1, 0),
                KEY_UP: lambda: self.model.move_cursor(0, -1),
                KEY_DOWN: lambda: self.model.move_cursor(0, 1),
            },
            'command': {

            },
            'find': {

            }
        }

    def _enter_insert_mode_start_str(self) -> None:
        self.model.str_to_start(),
        self.current_mode = 'insert'
        self.normal_buffer = "aaa"
        self.model.set_status(self.current_mode)
        self.model.notify_observers("text_changed", "")

    def _enter_insert_mode_finish_str(self) -> None:
        self.model.str_to_end(),
        self.current_mode = 'insert'
        self.normal_buffer = "aaa"
        self.model.set_status(self.current_mode)
        self.model.notify_observers("text_changed", "")

    def _enter_insert_mode_delete_str(self) -> None:
        self.model.delete_str(),
        self.current_mode = 'insert'
        self.normal_buffer = "aaa"
        self.model.set_status(self.current_mode)
        self.model.notify_observers("text_changed", "")

    def replace(self):
        char = self._adapter.get_char()
        self.model.replace(chr(char))

    def _enter_insert_mode(self) -> None:
        self.current_mode = 'insert'
        self.normal_buffer = "aaa"
        self.model.set_status(self.current_mode)
        self.model.notify_observers("text_changed", "")

    def _enter_normal_mode(self) -> None:
        self.current_mode = 'normal'
        self.normal_buffer = "aaa"
        self.model.set_status(self.current_mode)
        self.model.notify_observers("text_changed", "")

    def _enter_command_mode(self) -> None:
        self.state = self.command_handler
        self.command_handler.activate()
        self.current_mode = 'command'
        self.normal_buffer = "aaa"
        self.model.set_status(self.current_mode)
        self.model.notify_observers("text_changed", "")

    def _enter_find_mode(self, before: bool) -> None:
        self.state = self.find_handler
        self.find_handler.activate(not before)
        self.current_mode = 'find'
        self.normal_buffer = "aaa"
        self.model.set_status(self.current_mode)
        self.model.notify_observers("text_changed", "")

    def paste(self) -> None:
        self.model.paste(self.copy_buffer)

    def file_to_end(self) -> None:
        if len(self.numbers_buffer) > 0:
            self.model.set_cursor_pos(0, int(self.numbers_buffer) - 1)
        else:
            self.model.set_cursor_pos(0, self.model.get_len() - 1)
        self.numbers_buffer = ""

    def start(self):
        self.model.set_status("normal")
        while True:
            self.handle_input()

    def handle_input(self) -> None:
        if not self.command_handler.is_active and self.current_mode == "command":
            self.current_mode = "normal"
            self.model.set_status(self.current_mode)
            self.model.notify_observers("text_changed", "")
        if not self.find_handler.is_active and self.current_mode == "find":
            self.current_mode = "normal"
            self.model.set_status(self.current_mode)
            self.model.notify_observers("text_changed", "")
        char = self._adapter.get_char()
        handler = self.command_map[self.current_mode].get(char)
        # file = open("log.txt", "a+")
        # file.write(str(int(char)) + "\n")
        # file.close()
        trig = 0
        if self.normal_buffer[2] == "d" or self.normal_buffer[2] == "y" or self.normal_buffer[1:] == "di":
            trig = 1
        if trig == 0:
            if handler:
                handler()
            elif self.current_mode == 'normal' and char < 256:
                now_char = str(chr(char))
                if '0' <= now_char <= '9':
                    self.numbers_buffer += now_char
                else:
                    self.numbers_buffer = ""
                    self.normal_buffer += str(chr(char))
                    if len(self.normal_buffer) > 3:
                        self.normal_buffer = self.normal_buffer[1:]
                    if self.normal_buffer == "diw":
                        self.model.delete_word()
                        self.normal_buffer = "aaa"
                    elif self.normal_buffer[1:] == "gg":
                        self.model.set_cursor_pos(0, 0)
                    elif self.normal_buffer[1:] == "dd":
                        self.model.delete_str()
                        self.normal_buffer = "aaa"
                    elif self.normal_buffer[1:] == "yy":
                        self.copy_buffer = self.model.copy_str()
                        self.normal_buffer = "aaa"
                    elif self.normal_buffer[1:] == "yw":
                        self.copy_buffer = self.model.copy_word()
                        self.normal_buffer = "aaa"
            elif self.current_mode == 'insert' and char < 256:
                self.model.insert_char(chr(char))
                #self.model.notify_observers("text_changed", "")
            elif self.current_mode == 'command':
                if self.command_handler.is_active:
                    self.command_handler.handle_input(char)
            elif self.current_mode == 'find':
                if self.find_handler.is_active:
                    self.find_handler.handle_input(char)

                    #self.model.notify_observers("text_changed", "")
                # if char in self.command_map['command']:
                #     self.command_map['command'][char]()
                # elif 32 <= char <= 126:  # Печатные ASCII символы
                #     # Вставляем символ через MyString
                #     new_content = self._command_buffer.c_str() + chr(char)
                #     self._command_buffer = MyString(new_content)
                #     self.view.update()
        else:
            now_char = str(chr(char))
            if '0' <= now_char <= '9':
                self.numbers_buffer += now_char
            else:
                self.numbers_buffer = ""
                self.normal_buffer += str(chr(char))
                if len(self.normal_buffer) > 3:
                    self.normal_buffer = self.normal_buffer[1:]
                if self.normal_buffer == "diw":
                    self.model.delete_word()
                    self.normal_buffer = "aaa"
                elif self.normal_buffer[1:] == "gg":
                    self.model.set_cursor_pos(0, 0)
                elif self.normal_buffer[1:] == "dd":
                    self.model.delete_str()
                    self.normal_buffer = "aaa"
                elif self.normal_buffer[1:] == "yy":
                    self.copy_buffer = self.model.copy_str()
                    self.normal_buffer = "aaa"
                elif self.normal_buffer[1:] == "yw":
                    self.copy_buffer = self.model.copy_word()
                    self.normal_buffer = "aaa"

        self.model.notify_observers("text_changed", "")
