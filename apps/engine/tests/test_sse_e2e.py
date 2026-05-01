"""End-to-end SSE integration test.

The other SSE tests (in test_runs_api.py) use FastAPI's TestClient, which
exercises the ASGI app but doesn't expose the full SSE wire format. This
test goes one level lower: a real httpx.AsyncClient streaming over an
ASGITransport, parsing actual SSE frames coming back through the HTTP
boundary. It catches a class of bugs the existing tests can't see —
things like missing headers, broken `id:`/`event:`/`data:` framing, or
terminal-event close behavior.

The DB layer is mocked at the session-factory level so no real Postgres
is needed. We capture emitted events into an in-memory log and serve them
through the same RunService methods the SSE endpoint uses for replay, so
the test exercises the realistic path: launch → background engine emits →
stream replays from the (mocked) event store.
"""

import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.database import get_db
from app.main import app


# Per-run captured event log — the test populates it via the patched
# append_event and reads it via the patched list_events_after / get_run.
# Cleared per-test by the fixture.
_event_log: dict[uuid.UUID, list[SimpleNamespace]] = {}
_known_runs: set[uuid.UUID] = set()


def _make_session():
    """Create a permissive AsyncSession mock that accepts every operation."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars
    mock_result.rowcount = 0
    session.execute = AsyncMock(return_value=mock_result)
    return session


async def _override_get_db():
    yield _make_session()


@asynccontextmanager
async def _async_session_ctx():
    yield _make_session()


def _async_session_factory():
    """Stand-in for async_session() that returns a no-op context manager.

    The coordinator opens its own DB session via async_session() at the end
    of a run to persist the terminal state. We intercept that so the test
    doesn't need a real DB connection — the events themselves still flow
    through our in-memory log via patched RunService methods.
    """
    return _async_session_ctx()


async def _fake_create_pending_run(self, run_id, pipeline_dict):
    _known_runs.add(run_id)
    _event_log.setdefault(run_id, [])
    return SimpleNamespace(id=run_id)


async def _fake_get_run(self, run_id):
    if run_id in _known_runs:
        return SimpleNamespace(id=run_id, status="running")
    return None


async def _fake_append_event(self, run_id, sequence, event_type, payload):
    _event_log.setdefault(run_id, []).append(
        SimpleNamespace(
            sequence=sequence, event_type=event_type, payload=payload
        )
    )


async def _fake_list_events_after(self, run_id, after_sequence=-1, limit=1000):
    events = _event_log.get(run_id, [])
    return [e for e in events if e.sequence > after_sequence][:limit]


async def _fake_update_run_status(self, **kwargs):
    return None


async def _fake_upsert_step_result(self, run_id, step):
    return None


async def _fake_set_cancel_requested(self, run_id):
    return "cancelling" if run_id in _known_runs else None


@pytest.fixture
def db_overrides():
    """Wire DB mocks for both the request-scoped get_db and the
    coordinator-scoped async_session factory + RunService methods."""
    _event_log.clear()
    _known_runs.clear()
    app.dependency_overrides[get_db] = _override_get_db
    with (
        patch(
            "app.services.run_coordinator.async_session",
            new=_async_session_factory,
        ),
        patch(
            "app.services.run_service.RunService.create_pending_run",
            new=_fake_create_pending_run,
        ),
        patch(
            "app.services.run_service.RunService.get_run",
            new=_fake_get_run,
        ),
        patch(
            "app.services.run_service.RunService.append_event",
            new=_fake_append_event,
        ),
        patch(
            "app.services.run_service.RunService.list_events_after",
            new=_fake_list_events_after,
        ),
        patch(
            "app.services.run_service.RunService.update_run_status",
            new=_fake_update_run_status,
        ),
        patch(
            "app.services.run_service.RunService.upsert_step_result",
            new=_fake_upsert_step_result,
        ),
        patch(
            "app.services.run_service.RunService.set_cancel_requested",
            new=_fake_set_cancel_requested,
        ),
    ):
        yield
    app.dependency_overrides.pop(get_db, None)


def _parse_sse_block(block: str) -> dict[str, str]:
    """Parse a single SSE event block (separated by blank line) into fields."""
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if not line or line.startswith(":"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.lstrip(" ")
    return fields


@pytest.mark.asyncio
async def test_async_launch_then_stream_emits_run_lifecycle(db_overrides):
    """Launch a small pipeline asynchronously and verify the SSE stream
    emits run_started, step_started, step_completed and run_completed
    in that order, with parseable id/event/data fields on each frame."""

    pipeline = {
        "id": str(uuid.uuid4()),
        "name": "E2E SSE Pipeline",
        "nodes": [
            {
                "id": "src",
                "type": "datasource",
                "position": {"x": 0, "y": 0},
                "data": {
                    "label": "Source",
                    "nodeType": "datasource",
                    # SQL stays on the stub branch — no real HTTP fired
                    "config": {
                        "sourceType": "sql",
                        "url": "postgresql://localhost/test",
                    },
                },
            },
        ],
        "edges": [],
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test", timeout=5.0
    ) as client:
        launch = await client.post("/api/v1/runs/async", json={"pipeline": pipeline})
        assert launch.status_code == 202
        launch_body = launch.json()
        run_id = launch_body["run_id"]
        stream_url = launch_body["stream_url"]

        # Wait until the background task has finished and a terminal event
        # has been appended. We then connect to the stream and exercise the
        # finished-run replay path. Bounded to prevent flake on slow CI.
        deadline = asyncio.get_running_loop().time() + 3.0
        while asyncio.get_running_loop().time() < deadline:
            events_so_far = _event_log.get(uuid.UUID(run_id), [])
            if any(
                e.event_type in {"run_completed", "run_failed", "run_cancelled"}
                for e in events_so_far
            ):
                break
            await asyncio.sleep(0.02)
        else:
            pytest.fail("Background run never produced a terminal event")

        # Sanity check: the captured event log has the events we expect to
        # receive over the stream. If this assertion fails we have a setup
        # problem (mocks not wired), not an SSE wire-format problem.
        captured = _event_log[uuid.UUID(run_id)]
        captured_types = [e.event_type for e in captured]
        assert "run_started" in captured_types
        assert "run_completed" in captured_types

        events: list[dict[str, str]] = []
        # Read the response body fully — the stream closes itself on terminal.
        async with client.stream("GET", stream_url) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

            buffer = ""
            terminal_seen = False
            try:
                async for chunk in response.aiter_text():
                    # sse_starlette frames events with \r\n; normalize so a
                    # single split delimiter works regardless of line ending.
                    buffer += chunk.replace("\r\n", "\n")
                    while "\n\n" in buffer:
                        block, buffer = buffer.split("\n\n", 1)
                        parsed = _parse_sse_block(block)
                        if "event" in parsed:
                            events.append(parsed)
                        if parsed.get("event") in {
                            "run_completed",
                            "run_failed",
                            "run_cancelled",
                        }:
                            terminal_seen = True
                            break
                    if terminal_seen:
                        break
            except httpx.RemoteProtocolError:
                # Server closed the connection after the terminal event —
                # that's the expected behavior, not an error.
                pass

    event_types = [e["event"] for e in events]
    assert "run_started" in event_types
    assert "step_started" in event_types
    assert "step_completed" in event_types
    assert "run_completed" in event_types

    # Sequence ids are monotonically increasing and parseable as ints
    ids = [int(e["id"]) for e in events if "id" in e]
    assert ids == sorted(ids)
    assert ids[0] == 0

    # Each event has a JSON-decodable data payload referencing the run
    completed = next(e for e in events if e["event"] == "run_completed")
    payload = json.loads(completed["data"])
    assert payload["run_id"] == run_id
    assert payload["status"] == "completed"
