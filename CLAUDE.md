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
| Server state | (not yet needed — Zustand covers current needs) |
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
- `ripple` — Gear 3 VERIFY step (auto, obligatorisk)
- `pr-review` — Gear 3 REVIEW step (auto, fuld 5-lags analyse)
- `security-review` — REVIEW step ved auth/API/persistence/RLS features
- `owasp-llm-audit` — REVIEW step ved AI-node features (prompt injection, data leakage)
- `spec-first` — DESIGN step for Gear 3 features >1 dag
- `diagram` — DESIGN step ved komplekse flows (>3 komponenter)
- `mem-search` — UNDERSTAND step (auto, "har vi løst dette før?")
- `smart-explore` — UNDERSTAND step (AST-baseret kode-navigation, token-effektiv)
- `ship` — SHIP step pre-merge checklist (auto)

## Current Progress

> Opdateres af dev-pipeline SHIP-step og ved session-start.
> Sidste opdatering: 2025-07-19 (efter session 4 — Sprint 4 Hybrid C execution)
> 100 tests total (50 frontend + 50 backend), CI grøn på main.

### Done
- ✅ Monorepo scaffold + CI pipeline (lint, typecheck, test, build)
- ✅ Pipeline canvas med drag-and-drop (React Flow v12 custom nodes)
- ✅ 5 node-typer: datasource, AI, action, human, base
- ✅ Node configuration panels med type-specifikke forms
- ✅ UX polish: escape-closes-config, toast notifications, delete node, unsaved changes dialog, empty state, dark mode, config panel animation
- ✅ Pipeline execution types (shared package)
- ✅ SQLAlchemy models + Alembic migrations
- ✅ Pipeline execution engine (topological sort, Kahn's algorithm)
- ✅ Cycle detection + orphan edge validation (backend + frontend)
- ✅ Run API endpoints: POST /runs, GET /runs, GET /runs/{id}
- ✅ Run persistence to database (soft fail if DB unavailable)
- ✅ Frontend run UI med engine API integration
- ✅ 7 CRITICAL fixes: ID persistence, URL parse safety, error boundaries, async execution with thread pool + 120s timeout (PR #17-20)

### Done (Session 3 — Sprint 3 HIGH fixes)
- ✅ H1: isDirty filtering — only meaningful changes mark dirty (PR #21)
- ✅ H2: Zustand granular selectors in canvas, config-panel, results-panel (PR #21)
- ✅ H3: Node ID counter syncs with loaded pipeline IDs (PR #21)
- ✅ H4: AbortController with 30s timeout on engine API calls (PR #22)
- ✅ H5: Pydantic Field constraints — max 100 nodes, 500 edges, 200-char labels (PR #22)
- ✅ H8: Removed duplicate pnpm-lock.yaml (PR #23)
- ✅ H9: Docker context → monorepo root with updated Dockerfiles (PR #23)
- ✅ H10: transpilePackages for @gridlane/shared (PR #23)
- ✅ CI pipeline fixed: lockfile path, working-directory, lint errors (PR #23)

### Done (Session 4 — Sprint 4 Hybrid C execution)
- ✅ CI fix: ESLint suppress for next-themes hydration guard, unused var rename, ruff format
- ✅ Granular Zustand selectors in pipeline toolbar (was full-store subscription)
- ✅ CORS restricted to specific methods and headers
- ✅ Frontend cycle detection (Kahn's algorithm in validate())
- ✅ Removed unused @tanstack/react-query dependency
- ✅ Removed supabase + httpx from engine runtime deps (httpx stays in dev)
- ✅ RunService: save_run(), list_runs(), get_run() with full test coverage
- ✅ GET /runs and GET /runs/{id} endpoints with pagination
- ✅ POST /runs now persists to DB (soft fail)
- ✅ 100 tests total (50 FE + 50 BE), all green

### Parked (awaiting Supabase integration)
- ⬜ H6: Health check validerer ikke DB/Redis
- ⬜ H7: Database connection pool bruger defaults

### Not Started (Foundation Sprint)
- ⬜ 3 connectors: REST API, SQL (Supabase Postgres), File (CSV/JSON)
- ⬜ AI node: provider-agnostic (Anthropic + OpenAI), BYOK, streaming, cost tracking
- ⬜ HUMAN step: pause → approve/reject → resume
- ⬜ Observability: per-step timing, tokens, cost, run history

## Architecture Decisions

> Beslutninger der er taget og HVORFOR — så vi ikke re-debatterer dem.

| Decision | Valg | Alternativ | Hvorfor |
|----------|------|-----------|---------|
| Execution order | Kahn's algorithm (topological sort) | Simple queue, DFS | Håndterer DAG-struktur korrekt, O(V+E), fanger cycles |
| Async execution | `asyncio.to_thread()` + 120s timeout | Celery, subprocess | Simpelt for foundation-phase, nok til single-user |
| Client state | Zustand | Redux, Jotai | Minimal boilerplate, granulære selectors, React Flow kompatibel |
| Node rendering | React Flow v12 custom nodes | Default nodes, Rete.js | Fuld kontrol over UI, shadcn-integration, god DX |
| Node ID | Counter-baseret (`node_${n}`) + sync on load | UUID | Counter syncs with loaded IDs via `syncNodeIdCounter()` (H3 fixed) |
| Pipeline ID | UUID (genbrug ved re-save) | Auto-increment | Idempotent saves, ingen server-roundtrip for ID |
| Monorepo | pnpm workspaces | Turborepo, Nx | Simpelt, ingen build-orchestration overhead endnu |
| Python tooling | uv + Ruff | pip + Black + isort | Hurtigere, single tool for format + lint |

## Key File Navigation

> Brug dette i stedet for at scanne hele kodebasen.

### Pipeline Execution Flow
```
Frontend trigger:    run-results-panel.tsx (Run knap)
  → API call:        engine-api.ts (executePipeline)
  → Backend route:   apps/engine/app/api/v1/endpoints/runs.py (POST /runs)
  → Engine:          apps/engine/app/services/execution.py (topological sort + orchestration)
  → Node executors:  apps/engine/app/services/executors.py (stub executors per node type)
  → Persistence:     apps/engine/app/services/run_service.py (save_run → DB, soft fail)
  → History:         GET /runs (list), GET /runs/{id} (detail)
```

### Pipeline State Management
```
Store definition:    apps/web/src/stores/pipeline-store.ts (Zustand)
  → Canvas binding:  apps/web/src/components/canvas/pipeline-canvas.tsx
  → Config panel:    apps/web/src/components/canvas/node-config-panel.tsx
  → Save/Load:       apps/web/src/lib/pipeline-api.ts
```

### Node Type System
```
Shared types:        packages/shared/src/pipeline.ts (NodeType, PipelineNode, etc.)
  → Custom nodes:    apps/web/src/components/canvas/nodes/*.tsx (visual)
  → Config forms:    apps/web/src/components/canvas/config-forms/*.tsx (per-type config)
  → Backend models:  apps/engine/app/models/run.py (SQLAlchemy)
  → API schemas:     apps/engine/app/api/v1/schemas.py (Pydantic)
```

### Test Locations
```
Frontend tests:      apps/web/src/stores/__tests__/*.test.ts (50 tests)
Backend tests:       apps/engine/tests/*.py (50 tests)
CI pipeline:         .github/workflows/ci.yml
```

## Known Technical Debt

> Ting der bevidst er udskudt — ikke glemt.

| Debt | Severity | Blocker for |
|------|----------|-------------|
| Stub executors (no real execution) | HIGH | Connectors, AI node |
| No auth (Supabase Auth not configured) | HIGH | Multi-user, deploy |
| No RLS policies | HIGH | Data isolation |
| No root package.json for pnpm scripts | LOW | DX convenience |
| `_error` prop in global-error.tsx triggers ESLint warning (unused var) | LOW | Clean lint output |
| Supabase config settings in engine config.py unused | LOW | Cleanup |

## Foundation Sprint — Definition of Done

See `~/Developer/ClaudePlans/gridlane-strategic-foundation.md` section 0.2 for full DOD.

Key criteria (see Current Progress for status):
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
