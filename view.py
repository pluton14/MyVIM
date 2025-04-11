from abc import ABC, abstractmethod
from typing import Tuple, Any

from controller.controller import IController
# from controller import IController
from curses_adapter import CursesAdapter
from model.model import Observer, IModel
from interfaces.event_listener import EventListener
from interfaces.IViewAdapter import IViewAdapter


class IView(ABC):
    @abstractmethod
    def update(self, model: IModel, event_type: str, data: Any) -> None:
        pass


class CursesView(IView, EventListener):
    def __init__(self, adapter: IViewAdapter) -> None:
        self.adapter = adapter
        self.adapter.init_curses()
        rows, cols = self.adapter.get_screen_size()
        self._screen_width = cols
        self._screen_height = rows
        self._virtual_offset_y = 0  # Смещение по вертикали
        self._line_wrap_cache = {}  # Кэш переносов строк

    def update(self, model: IModel, event_type: str, data: Any) -> None:
        rows, cols = self.adapter.get_screen_size()
        self._screen_width = cols
        self._screen_height = rows
        self._calculate_wrap_cache(model)
        self._handle_scroll(model)
        self._draw_ui(model)
        if event_type == "text_changed":
            rows, cols = self.adapter.get_screen_size()
            self._screen_width = cols
            self._screen_height = rows
            self._calculate_wrap_cache(model)
            self._handle_scroll(model)
            self._draw_ui(model)
        elif event_type == "cursor_moved":
            self.draw_cursor(model)
    def _calculate_wrap_cache(self, model: IModel):
        """Рассчитывает кэш переносов строк для всего текста"""
        lines, (x, y) = model.get_data()
        self._line_wrap_cache.clear()
        total_virtual = 0

        for y, line in enumerate(lines):
            line_len = len(line)
            wraps = (line_len // self._screen_width) + 1
            self._line_wrap_cache[y] = {
                'wraps': wraps,
                'start_virtual': total_virtual
            }
            total_virtual += wraps

    def _real_to_virtual(self, real_x: int, real_y: int) -> Tuple[int, int]:
        """Преобразует реальные координаты в виртуальные"""
        if real_y not in self._line_wrap_cache:
            return (0, 0)

        wrap_info = self._line_wrap_cache[real_y]
        virtual_y = wrap_info['start_virtual'] + (real_x // self._screen_width)
        virtual_x = real_x % self._screen_width
        return (virtual_x, virtual_y)

    def _virtual_to_real(self, virtual_x: int, virtual_y: int) -> Tuple[int, int]:
        """Преобразует виртуальные координаты в реальные"""
        for real_y, wrap_info in self._line_wrap_cache.items():
            if virtual_y < wrap_info['start_virtual'] + wrap_info['wraps']:
                wrap_offset = virtual_y - wrap_info['start_virtual']
                real_x = wrap_offset * self._screen_width + virtual_x
                return (real_x, real_y)
        return (0, 0)

    def draw_cursor(self, model: IModel) -> None:
        lines, (cursor_x, cursor_y) = model.get_data()
        virt_cursor_x, virt_cursor_y = self._real_to_virtual(cursor_x, cursor_y)
        start_virtual = self._virtual_offset_y
        end_virtual = start_virtual + self._screen_height - 2  # -2 для статусной строки
        if start_virtual <= virt_cursor_y <= end_virtual:
            visible_cursor_y = virt_cursor_y - start_virtual
            self.adapter.move_cursor(virt_cursor_x, visible_cursor_y)

    def _draw_ui(self, model: IModel):
        """Отрисовка с учетом переносов строк"""
        self.adapter.clear_screen()
        lines, (cursor_x, cursor_y) = model.get_data()

        # Рассчитываем виртуальную позицию курсора
        virt_cursor_x, virt_cursor_y = self._real_to_virtual(cursor_x, cursor_y)
        # print(str(virt_cursor_x) + " " + str(virt_cursor_y))
        # self.adapter.move_cursor(virt_cursor_y, virt_cursor_x)

        # Определяем видимую область
        start_virtual = self._virtual_offset_y
        end_virtual = start_virtual + self._screen_height - 2  # -2 для статусной строки

        # Отрисовываем видимые виртуальные строки
        row = 0
        for real_y in self._line_wrap_cache:
            wrap_info = self._line_wrap_cache[real_y]
            line = lines[real_y]

            for wrap in range(wrap_info['wraps']):
                virtual_y = wrap_info['start_virtual'] + wrap
                if start_virtual <= virtual_y <= end_virtual:
                    start = wrap * self._screen_width
                    end = start + self._screen_width
                    self.adapter.add_str(row, 0, line[start:end])
                    row += 1

        # Отрисовка курсора
        self._draw_status_bar(model)
        if (start_virtual <= virt_cursor_y <= end_virtual and model.get_status() != "command"
                and (model.get_status() != "find" or model.search)):
            visible_cursor_y = virt_cursor_y - start_virtual
            self.adapter.move_cursor(virt_cursor_x, visible_cursor_y)

        # Статусная строка
        # self._draw_status_bar(model)

    def _handle_scroll(self, model: IModel):
        """Автоматическая прокрутка при выходе за границы"""
        _, virt_cursor_y = self._real_to_virtual(model.get_cursor_pos()[0], model.get_cursor_pos()[1])

        if virt_cursor_y < self._virtual_offset_y:
            self._virtual_offset_y = virt_cursor_y
        elif virt_cursor_y >= self._virtual_offset_y + self._screen_height - 1:
            self._virtual_offset_y = virt_cursor_y - self._screen_height + 2

    def _draw_status_bar(self, model: IModel):
        """Статусная строка с информацией"""
        mode = model.get_status()
        if mode == "command":
            status = f":{model.get_command_buf()}"
        elif mode == "find":
            status = f"{model.get_command_buf()}"
        else:
            real_x, real_y = model.get_cursor_pos()
            status = f"{mode} | Line: {real_y + 1} Col: {real_x + 1}"

        self.adapter.add_str(self._screen_height - 1, 0, status)

    # def run(self) -> None:
    #     self._draw_ui()
    #     while True:
    #         self.controller.handle_input()

    def __del__(self) -> None:
        self.adapter.end_curses()