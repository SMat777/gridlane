"""
EventBus + RunChannel unit tests.

Tests the in-process pub/sub mechanism that powers SSE streaming:
  - sequence numbering is monotonic per channel
  - publish delivers to all subscribers
  - bounded queue drops oldest when full (prevents publisher blocking)
  - close removes channel from registry
"""

import asyncio

import pytest

from app.services.event_bus import (
    SUBSCRIBER_QUEUE_MAX,
    EventBus,
    RunChannel,
    RunEvent,
)


class TestRunChannelSequence:
    def test_sequence_is_monotonic_from_zero(self):
        channel = RunChannel(run_id=__import__("uuid").uuid4())
        assert channel.next_sequence() == 0
        assert channel.next_sequence() == 1
        assert channel.next_sequence() == 2


class TestRunChannelPubSub:
    @pytest.mark.asyncio
    async def test_publish_delivers_to_all_subscribers(self):
        channel = RunChannel(run_id=__import__("uuid").uuid4())
        q1 = channel.subscribe()
        q2 = channel.subscribe()

        event = RunEvent(sequence=0, event_type="run_started", payload={"x": 1})
        await channel.publish(event)

        assert q1.qsize() == 1
        assert q2.qsize() == 1
        e1 = await q1.get()
        assert e1.sequence == 0
        assert e1.payload == {"x": 1}

    @pytest.mark.asyncio
    async def test_unsubscribe_removes_subscriber(self):
        channel = RunChannel(run_id=__import__("uuid").uuid4())
        q = channel.subscribe()
        channel.unsubscribe(q)

        event = RunEvent(sequence=0, event_type="run_started", payload={})
        await channel.publish(event)

        # Unsubscribed queue receives no events
        assert q.qsize() == 0

    @pytest.mark.asyncio
    async def test_full_queue_drops_oldest(self):
        """If a subscriber lags, the bus drops the oldest event rather than
        blocking the publisher (other subscribers shouldn't suffer)."""
        channel = RunChannel(run_id=__import__("uuid").uuid4())
        q = channel.subscribe()

        # Fill the queue
        for i in range(SUBSCRIBER_QUEUE_MAX):
            await channel.publish(
                RunEvent(sequence=i, event_type="step_completed", payload={"i": i})
            )

        assert q.qsize() == SUBSCRIBER_QUEUE_MAX

        # One more publish should drop the oldest, not block
        await asyncio.wait_for(
            channel.publish(
                RunEvent(
                    sequence=SUBSCRIBER_QUEUE_MAX,
                    event_type="step_completed",
                    payload={"newest": True},
                )
            ),
            timeout=0.5,
        )

        # Queue size unchanged, but newest event is in the queue
        assert q.qsize() == SUBSCRIBER_QUEUE_MAX
        # Oldest dropped: first event we now see has sequence > 0
        first = await q.get()
        assert first.sequence > 0


class TestEventBus:
    def test_open_channel_idempotent(self):
        import uuid

        bus = EventBus()
        run_id = uuid.uuid4()
        ch1 = bus.open_channel(run_id)
        ch2 = bus.open_channel(run_id)
        assert ch1 is ch2

    def test_close_channel_removes_from_registry(self):
        import uuid

        bus = EventBus()
        run_id = uuid.uuid4()
        bus.open_channel(run_id)
        assert bus.get_channel(run_id) is not None

        bus.close_channel(run_id)
        assert bus.get_channel(run_id) is None

    def test_get_channel_returns_none_for_unknown(self):
        import uuid

        bus = EventBus()
        assert bus.get_channel(uuid.uuid4()) is None
