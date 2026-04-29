# Gridlane — Project Contract

## What This Is

Visual AI pipeline builder with production observability and human-in-the-loop governance. Users drag-and-drop data sources, AI analysis steps, and actions onto a canvas — then run pipelines with full per-step tracing (timing, tokens, cost).

**Domain:** gridlane.dev (purchased)
**Phase:** Foundation (week 1-8)
**Strategic docs:** `~/Developer/ClaudePlans/gridlane-strategic-foundation.md`

## Tech Stack

| Layer | Tool |
|-------|------|
| Frontend | Next.js 16 + React 19 + TypeScript |
| Canvas | React Flow `@xyflow/react` v12 |
| UI | shadcn/ui + Tailwind v4 |
| Client state | Zustand |
| Server state | TanStack Query |
| JS tooling | pnpm + ESLint + tsc |
| Backend | FastAPI + Python 3.12 |
| Py tooling | uv + Ruff + pytest |
| ORM | SQLAlchemy 2.0 async + asyncpg |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Database | Supabase Postgres (remote, RLS) |
| Auth | Supabase Auth |
| Realtime | Supabase Realtime |
| Storage | Supabase Storage |
| Queue broker | Redis 7 |
| CI | GitHub Actions |

## Monorepo Structure

```
gridlane/
├── apps/
│   ├── web/            — Next.js frontend (canvas, dashboard, UI)
│   └── engine/         — FastAPI backend (pipeline engine, API, connectors)
├── packages/
│   └── shared/         — Shared types/contracts
├── docker-compose.yml  — Local dev: frontend + backend + Redis
├── .github/workflows/  — CI pipeline
└── CLAUDE.md           — This file
```

## Conventions

- **Code language:** English (variables, functions, docs, commits, PRs)
- **Collaboration language:** Danish (plans, discussions, explanations)
- **TDD:** Default workflow — test first, implementation after
- **Commits:** Natural language, no type-prefixes, specific file staging (never `git add .`)
- **Branch:** `main` default, feature branches for all work
- **GitHub:** `gh` CLI — not GitHub MCP (token savings)

## Running

```bash
# Full stack (Docker)
docker compose up

# Frontend only
cd apps/web && pnpm dev

# Backend only
cd apps/engine && uv run uvicorn app.main:app --reload

# Tests
cd apps/engine && uv run pytest tests/ -v
cd apps/web && pnpm lint && pnpm exec tsc --noEmit
```

## Dev-Pipeline Integration

### Gear defaults
- **Gear 2:** Connectors, UI components, single features
- **Gear 3:** Pipeline engine core, canvas architecture, HUMAN step

### Token-efficient navigation
- Files > 100 lines → `smart_outline` → `smart_unfold`
- Cross-file lookup → `smart_search`
- Config/markdown/JSON → `Read`

### Framework docs (Context7 — only for specific API questions)
```
@xyflow/react: custom nodes, edge types, onNodesChange
supabase: RLS policies, auth hooks, realtime subscriptions
fastapi: dependency injection, async endpoints, streaming
pydantic: discriminated unions, custom validators
```

### Active quality skills
- `verification-before-completion` — always on
- `test-driven-development` — default workflow
- `systematic-debugging` — when something breaks
- `ripple` — after engine features, before merge
- `spec-first` — for Gear 3 features

## Foundation Sprint — Definition of Done

See `~/Developer/ClaudePlans/gridlane-strategic-foundation.md` section 0.2 for full DOD.

Key criteria:
- [ ] End-to-end pipeline: build → run → see trace
- [ ] 3 connectors: REST API, SQL (Supabase Postgres), File (CSV/JSON)
- [ ] AI node: provider-agnostic (Anthropic + OpenAI), BYOK, streaming, cost tracking
- [ ] HUMAN step: pause → approve/reject → resume
- [ ] Observability: per-step timing, tokens, cost, run history

## Deploy Decisions

- **Private repo** until pipeline engine is running
- **Supabase:** Remote project from day 1 (free tier)
- **Production deploy:** Vercel (frontend) + Railway (backend) — Beta phase
- **Domain:** gridlane.dev ready for Beta
