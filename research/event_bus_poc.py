import asyncio
import random
import time
from enum import Enum, auto

class EventType(Enum):
    MARKET_DATA = auto()
    SIGNAL = auto()
    ORDER = auto()
    FILL = auto()

class Event:
    def __init__(self, type, payload):
        self.type = type
        self.payload = payload
        self.timestamp = time.time()

class EventBus:
    def __init__(self):
        self.subscribers = {}
        self.queue = asyncio.Queue()

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def publish(self, event):
        await self.queue.put(event)

    async def run(self):
        print("Event Bus Started...")
        while True:
            event = await self.queue.get()
            if event.type in self.subscribers:
                for callback in self.subscribers[event.type]:
                    # In a real system, these might be awaited or spawned as tasks
                    try:
                        await callback(event)
                    except Exception as e:
                        print(f"Error processing event {event.type}: {e}")
            self.queue.task_done()

# --- Components ---

class MarketDataSource:
    def __init__(self, bus):
        self.bus = bus

    async def stream_data(self):
        print("Market Data Stream Started...")
        for i in range(5):
            price = 100 + random.uniform(-1, 1)
            event = Event(EventType.MARKET_DATA, {"symbol": "AAPL", "price": round(price, 2)})
            print(f"[DATA] Published {event.payload}")
            await self.bus.publish(event)
            await asyncio.sleep(0.5)

class Strategy:
    def __init__(self, bus):
        self.bus = bus

    async def on_market_data(self, event):
        price = event.payload["price"]
        # Logic: Buy if price < 99.5
        if price < 99.5:
            signal = Event(EventType.SIGNAL, {"symbol": "AAPL", "side": "BUY", "price": price})
            print(f"[STRAT] Signal Generated: {signal.payload}")
            await self.bus.publish(signal)

class ExecutionEngine:
    async def on_signal(self, event):
        # Simulate latency
        await asyncio.sleep(0.1)
        print(f"[EXEC] Order Filled: {event.payload}")

async def main():
    bus = EventBus()
    
    strat = Strategy(bus)
    exec_engine = ExecutionEngine()
    data_source = MarketDataSource(bus)
    
    # Wiring
    bus.subscribe(EventType.MARKET_DATA, strat.on_market_data)
    bus.subscribe(EventType.SIGNAL, exec_engine.on_signal)
    
    # Run Bus in background
    bus_task = asyncio.create_task(bus.run())
    
    # Run Data Stream
    await data_source.stream_data()
    
    # Wait for processing
    await asyncio.sleep(1)
    bus_task.cancel()
    print("POC Finished.")

if __name__ == "__main__":
    asyncio.run(main())
