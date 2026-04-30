"""
In-process event bus for pipeline run progress events.

The engine publishes events to a per-run channel; the SSE endpoint
subscribes to the channel and streams events to the client. Each subscriber
gets its own bounded asyncio.Queue so a slow consumer doesn't block emission
or affect other subscribers.

Persistence model:
  - Every published event is also written to the `run_events` table by the
    coordinator before going onto subscriber queues.
  - On reconnect with Last-Event-ID, the subscriber first replays missed
    events from the DB, then attaches to the live channel for new events.
  - When a run is already terminal at subscribe time, the subscriber gets a
    pure DB replay and the channel never spins up.

Event identity:
  - sequence is per-run, monotonically increasing, starts at 0.
  - This is what gets sent as `id:` on the SSE wire and what
    `Last-Event-ID` resumes from.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)

# Bounded queue size per subscriber. Generous: a subscriber would have to fall
# behind by 256 events — far more than any realistic single-step pipeline emits.
SUBSCRIBER_QUEUE_MAX = 256


@dataclass
class RunEvent:
    """A single event in a pipeline run's progress stream."""

    sequence: int
    event_type: str
    payload: dict[str, Any]


@dataclass
class RunChannel:
    """Per-run pub/sub channel with a list of bounded subscriber queues.

    The channel exists only while a run is actively executing. After a
    terminal event, subscribers receive that event and the channel is
    removed from the bus. Late subscribers fall through to DB replay.
    """

    run_id: UUID
    sequence: int = 0
    subscribers: list[asyncio.Queue] = field(default_factory=list)
    terminated: bool = False

    def next_sequence(self) -> int:
        """Allocate and return the next event sequence number."""
        seq = self.sequence
        self.sequence += 1
        return seq

    async def publish(self, event: RunEvent) -> None:
        """Push an event to all current subscribers.

        If a subscriber's queue is full, drop the oldest event for that
        subscriber rather than blocking the publisher. Terminal events are
        critical — if we have to drop, drop a non-terminal first.
        """
        for queue in self.subscribers:
            if queue.full():
                try:
                    queue.get_nowait()  # drop oldest
                except asyncio.QueueEmpty:
                    pass
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # Should not happen — we just drained — but defensive
                logger.warning(
                    "Subscriber queue still full after drain for run %s",
                    self.run_id,
                )

    def subscribe(self) -> asyncio.Queue:
        """Register a subscriber and return its event queue."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=SUBSCRIBER_QUEUE_MAX)
        self.subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Remove a subscriber's queue (e.g. on client disconnect)."""
        try:
            self.subscribers.remove(queue)
        except ValueError:
            pass


class EventBus:
    """Process-local pub/sub bus, keyed by run_id."""

    def __init__(self):
        self._channels: dict[UUID, RunChannel] = {}

    def open_channel(self, run_id: UUID) -> RunChannel:
        """Create (or return existing) channel for a run.

        Called by the coordinator when launching a run, so subscribers that
        connect before the engine emits its first event still have a channel
        to attach to.
        """
        if run_id not in self._channels:
            self._channels[run_id] = RunChannel(run_id=run_id)
        return self._channels[run_id]

    def get_channel(self, run_id: UUID) -> RunChannel | None:
        """Return the channel for a run if one is currently active."""
        return self._channels.get(run_id)

    def close_channel(self, run_id: UUID) -> None:
        """Mark channel terminated and remove from registry.

        Subscribers still draining their queues will see the queued terminal
        event before realizing the channel is gone.
        """
        channel = self._channels.pop(run_id, None)
        if channel is not None:
            channel.terminated = True


# Process-local singleton. Same caveat as RunCoordinator: multi-worker
# setups need a cross-process pub/sub (Redis pub/sub is the obvious next step).
bus = EventBus()
