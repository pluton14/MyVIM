from abc import ABC, abstractmethod


class ICommandState(ABC):
    @abstractmethod
    def handle_input(self, char: int) -> None:
        pass

    @property
    @abstractmethod
    def buffer(self) -> str:
        pass

    @property
    @abstractmethod
    def is_active(self) -> bool:
        pass

    @abstractmethod
    def _execute_command(self) -> None:
        pass

    @abstractmethod
    def activate(self) -> None:
        pass

    @abstractmethod
    def deactivate(self) -> None:
        pass
