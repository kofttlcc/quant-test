import asyncio
import logging
from typing import Dict, List, Callable, Awaitable, Any
from .events import Event, EventType

logger = logging.getLogger(__name__)

class EventBus:
    """
    AsyncIO-based Event Bus.
    Core of the V2.0 Event-Driven Architecture.
    """
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], Awaitable[None]]]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task = None

    def subscribe(self, event_type: EventType, callback: Callable[[Event], Awaitable[None]]):
        """
        Subscribe to an event type.
        Callback must be an async function.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed {callback.__name__} to {event_type}")

    async def publish(self, event: Event):
        """
        Publish an event to the queue.
        """
        await self._queue.put(event)
        # logger.debug(f"Published event: {event.type}")

    async def start(self):
        """
        Start the event processing loop.
        """
        self._running = True
        logger.info("Event Bus Started.")
        while self._running:
            try:
                event = await self._queue.get()
                if event.type in self._subscribers:
                    for callback in self._subscribers[event.type]:
                        try:
                            # Execute callbacks sequentially for safety, 
                            # or use asyncio.create_task for parallelism (trade-off)
                            await callback(event)
                        except Exception as e:
                            logger.error(f"Error in subscriber {callback.__name__}: {e}", exc_info=True)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event Bus Error: {e}")
        
        logger.info("Event Bus Stopped.")

    def stop(self):
        """
        Stop the event loop.
        """
        self._running = False
