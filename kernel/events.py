import asyncio
from typing import Callable, Dict, List, Any

class EventBus
    def __init__(self)
        self._listeners Dict[str, List[Callable]] = {}

    def subscribe(self, event_type str, callback Callable)
        if event_type not in self._listeners
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def publish(self, event_type str, data Any)
        if event_type in self._listeners
            for callback in self._listeners[event_type]
                if asyncio.iscoroutinefunction(callback)
                    await callback(data)
                else
                    callback(data)

# Instance unique du bus d'événements du Kernel
event_bus = EventBus()