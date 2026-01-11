import unittest
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.core.event_bus import EventBus
from src.core.events import Event, EventType
from src.core.data_models import Bar

class TestCoreFoundation(unittest.IsolatedAsyncioTestCase):
    
    async def test_event_bus_pub_sub(self):
        bus = EventBus()
        received_events = []

        async def market_data_handler(event: Event):
            received_events.append(event)

        bus.subscribe(EventType.MARKET_DATA, market_data_handler)
        
        # Start bus in background task
        bus_task = asyncio.create_task(bus.start())
        
        # Publish Event
        payload = {"symbol": "AAPL", "price": 150.0}
        evt = Event(EventType.MARKET_DATA, payload)
        await bus.publish(evt)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].payload["price"], 150.0)
        
        bus.stop()
        # Cancel task to clean up (it waits on queue.get)
        bus_task.cancel()
        try:
            await bus_task
        except asyncio.CancelledError:
            pass

    def test_data_models(self):
        now = datetime.now()
        bar = Bar(
            symbol="BTCUSD",
            time=now,
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000.0
        )
        self.assertEqual(bar.period, timedelta(minutes=1))
        self.assertEqual(bar.end_time, now + timedelta(minutes=1))

if __name__ == '__main__':
    unittest.main()
