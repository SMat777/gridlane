# Gridlane

Visual AI pipeline builder with production observability and human-in-the-loop governance.

Build pipelines by dragging data sources, AI analysis steps, and actions onto a canvas. Run them with full per-step tracing — timing, tokens, cost, and complete audit trails.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Frontend (Next.js 16 + React Flow)         │
│  Canvas → Dashboard → Run Explorer          │
└──────────────────┬──────────────────────────┘
                   │ REST API /api/v1/
                   ▼
┌─────────────────────────────────────────────┐
│  Engine (FastAPI + Python 3.12)             │
│  Pipeline Runner → Connectors → AI Nodes   │
│  Observability → Audit Log → HUMAN Step    │
└──────────┬──────────────┬───────────────────┘
           │              │
           ▼              ▼
┌──────────────┐  ┌──────────────┐
│  Supabase    │  │  Redis 7     │
│  Postgres    │  │  Task Queue  │
│  Auth + RLS  │  │              │
│  Realtime    │  │              │
└──────────────┘  └──────────────┘
```

## Quick Start

```bash
# Clone and install
git clone https://github.com/SMat777/gridlane.git
cd gridlane

# Start everything
docker compose up

# Or run individually:
cd apps/web && pnpm install && pnpm dev      # Frontend on :3000
cd apps/engine && uv sync && uv run uvicorn app.main:app --reload  # Backend on :8000
```

## Project Structure

```
gridlane/
├── apps/
│   ├── web/            — Next.js frontend
│   └── engine/         — FastAPI backend
├── packages/
│   └── shared/         — Shared types
├── docker-compose.yml  — Local dev environment
└── .github/workflows/  — CI pipeline
```

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, React Flow, shadcn/ui, Tailwind v4, Zustand |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Pydantic v2 |
| Database | Supabase (Postgres + Auth + RLS + Realtime) |
| Queue | Redis 7 |
| CI | GitHub Actions |

## Status

🚧 **Foundation sprint** — building core canvas, pipeline engine, connectors, and observability.
