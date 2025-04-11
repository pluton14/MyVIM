from abc import ABC, abstractmethod
from typing import Any

from interfaces.IModel import IModel


class EventListener(ABC):
    @abstractmethod
    def update(self, model: IModel, event_type: str, data: Any) -> None:
        """Метод, вызываемый при уведомлении о событии"""
        pass