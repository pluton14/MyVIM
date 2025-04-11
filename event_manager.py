from typing import Dict, List, Any

from interfaces.IModel import IModel
from interfaces.event_listener import EventListener

class EventManager:
    def __init__(self):
        self._listeners: Dict[str, List[EventListener]] = {}

    def subscribe(self, event_type: str, listener: EventListener) -> None:
        """Подписывает слушателя на определенный тип события"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: EventListener) -> None:
        """Отписывает слушателя от определенного типа события"""
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    def notify(self, model: IModel, event_type: str, data: Any = None) -> None:
        """Уведомляет всех подписчиков о событии"""
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                listener.update(model, event_type, data)