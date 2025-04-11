from curses_adapter import CursesAdapter
from model.model import Model
from view import CursesView
from controller.controller import VimController

def main():
    model = Model()
    adapter = CursesAdapter()
    view = CursesView(adapter)
    model.add_observer(view, "text_changed")
    model.add_observer(view, "cursor_moved")
    model.add_observer(view, "file_opened")
    model.add_observer(view, "file_saved")
    controller = VimController(model, adapter)
    controller.start()
    #view.run()

if __name__ == "__main__":
    main()