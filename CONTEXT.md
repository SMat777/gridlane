# Gridlane — Context Snapshot

> Sidst opdateret: 2025-07-21 (session 6)

## Current State

- **Tests:** 157 (89 FE + 68 BE), CI grøn
- **Branch:** `feature/config-validation` (2 commits, klar til PR)
- **Næste:** SSE Progress → Run History → REST Connector
- **Blokeret:** Intet

## Filstruktur — Hvad eksisterer

```
gridlane/
├── apps/engine/                         — FastAPI backend
│   ├── app/core/
│   │   ├── config.py                    ✅ pydantic-settings
│   │   ├── database.py                  ✅ async SQLAlchemy session
│   │   └── errors.py                    ✅ ErrorCode enum + PipelineError
│   ├── app/models/
│   │   ├── base.py                      ✅ declarative base
│   │   └── run.py                       ✅ PipelineRunModel + StepResultModel
│   ├── app/api/v1/endpoints/
│   │   ├── health.py                    ✅ GET /health (ingen DB/Redis check)
│   │   └── runs.py                      ✅ POST/GET /runs
│   ├── app/services/
│   │   ├── execution.py                 ✅ Kahn's topological sort + orchestration
│   │   ├── executors.py                 🔶 4 STUB executors (contract + validation klar)
│   │   └── run_service.py              ✅ save/list/get med DB persistence
│   └── tests/                           ✅ 56 tests (5 filer)
│
├── apps/web/src/
│   ├── app/page.tsx                     ✅ single page → PipelineCanvas
│   ├── middleware.ts                    ✅ Supabase SSR middleware
│   ├── stores/pipeline-store.ts        ✅ Zustand: nodes/edges/CRUD/validate
│   ├── components/canvas/
│   │   ├── pipeline-canvas.tsx          ✅ React Flow + DnD + cycle prevention
│   │   ├── pipeline-toolbar.tsx         ✅ save/load/validate/run/new
│   │   ├── node-palette.tsx            ✅ drag palette (4 typer)
│   │   ├── node-config-panel.tsx       ✅ slide-in config editor
│   │   ├── run-results-panel.tsx       ✅ step results + timing + cost
│   │   ├── nodes/                      ✅ 4 custom nodes + base-node
│   │   └── config-forms/              ✅ 4 forms + field-error component + Zod validation
│   ├── lib/
│   │   ├── engine-api.ts               ✅ POST /runs client (30s timeout)
│   │   ├── pipeline-api.ts             ✅ Supabase CRUD
│   │   └── supabase/                   ✅ @supabase/ssr (browser+server+middleware)
│   └── stores/__tests__/               ✅ 58 tests (4 filer)
│
├── packages/shared/src/
│   ├── pipeline.ts                     ✅ NodeType, PipelineNode, configs
│   ├── execution.ts                    ✅ Run/step/status types
│   └── validation.ts                   ✅ Zod schemas for all 4 node configs
│
├── supabase/
│   ├── migrations/                     ✅ SQL schema (source of truth)
│   └── seed.sql                        ✅ sample pipeline + run
│
└── ⬜ Ikke bygget endnu:
    ├── Auth UI (login/signup)
    ├── Dashboard / run history page
    ├── Config form validation (Zod)
    ├── SSE progress reporting
    ├── REST/SQL/File connectors
    ├── AI node (Anthropic/OpenAI)
    └── HUMAN step (pause/resume)
```

## Etablerede Patterns

### Connector Contract
```python
class NodeExecutor(ABC):
    @classmethod
    @abstractmethod
    def manifest(cls) -> ConnectorManifest: ...
    def validate_config(self, config: dict) -> list[ConfigError]: ...
    @abstractmethod
    def execute(self, config: dict, input_data: Any) -> ExecutorResult: ...

_EXECUTORS: dict[str, type[NodeExecutor]] = {
    "datasource": StubDataSourceExecutor,  # alle 4 er stubs
    "ai": StubAIExecutor, "human": StubHumanExecutor, "action": StubActionExecutor,
}
```

### Config Validation (Zod + Python)
```typescript
// Frontend: Zod schema in packages/shared/src/validation.ts
import { validateNodeConfig } from "@gridlane/shared";
const result = validateNodeConfig("ai", config);
// → { valid: false, errors: [{ field: "prompt", message: "Prompt is required" }] }

// Forms receive errors prop:
<AIConfigForm config={...} onUpdate={...} errors={fieldErrors} />
// FieldError + fieldErrorClass for inline error display
```
```python
# Backend: validate_config() override per executor
errors = executor.validate_config(config)
# → [ConfigError(field="url", message="URL is required for REST sources")]

# Preflight in ExecutionEngine.execute():
# Validates ALL configs before running ANY step → PipelineError(VALIDATION_ERROR)
```

### Structured Errors
```python
class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CYCLE_DETECTED = "CYCLE_DETECTED"
    EXECUTOR_FAILED = "EXECUTOR_FAILED"  # 12 codes total

class PipelineError(Exception):
    def __init__(self, code: ErrorCode, message: str,
                 status_code: int = 400, details: dict | None = None): ...
# → JSON: { error: { code, message, details } }
```

### Zustand Granular Selectors
```typescript
const { nodes, edges, onNodesChange } = usePipelineStore(
  useShallow((s) => ({
    nodes: s.nodes, edges: s.edges, onNodesChange: s.onNodesChange,
  })),
);
// Single values:
const addNode = usePipelineStore((s) => s.addNode);
```

### Migration Naming
```
supabase/migrations/YYYYMMDD000NNN_description.sql
20250720000001_create_schema.sql
20250720000002_create_rls_policies.sql
```

## Database — Nøgletabeller

### pipelines
`id` uuid PK | `user_id` uuid FK (nullable) | `name` text | `definition` jsonb | timestamps

### pipeline_runs
`id` uuid PK | `pipeline_id` uuid FK → pipelines | `status` varchar (pending/running/completed/failed/cancelled) | `total_duration_ms` int | `total_cost_usd` numeric(10,6) | `pipeline_snapshot` jsonb | timestamps

### step_results
`id` uuid PK | `run_id` uuid FK → pipeline_runs (cascade) | `node_id` varchar | `node_type` varchar | `status` varchar | `order` int | `input_data`/`output_data` jsonb | `duration_ms` int | `input_tokens`/`output_tokens`/`total_tokens` int | `cost_usd` numeric(10,6)

**RLS:** Enabled, permissive (user_id nullable i foundation-fase).

## Progress

### Done (sessions 1-5)
- ✅ Monorepo + CI (lint, typecheck, test, build)
- ✅ Pipeline canvas med drag-and-drop (React Flow v12)
- ✅ 5 node-typer med config forms
- ✅ Pipeline execution engine (Kahn's algorithm)
- ✅ Run API: POST/GET /runs med DB persistence
- ✅ Frontend run UI med engine API integration
- ✅ Supabase CLI consolidation (migrations, RLS, seed)
- ✅ Connector Interface Contract (manifest/validate/execute)
- ✅ Structured error system (ErrorCode + PipelineError)
- ✅ UX polish: escape-closes, toasts, delete, unsaved changes, dark mode

### Done (session 6)
- ✅ Config Validation (Zod frontend + Python backend + preflight execution check)

### Not Started (Foundation Sprint)
- ⬜ SSE Progress Reporting
- ⬜ Run History Frontend (backend klar)
- ⬜ 3 connectors: REST API, SQL, File (CSV/JSON)
- ⬜ AI node: Anthropic + OpenAI, BYOK, streaming, cost tracking
- ⬜ HUMAN step: pause → approve/reject → resume

## Known Debt

| Debt | Severity | Note |
|------|----------|------|
| 4 stub executors | HIGH | Connector contract klar, implementation mangler |
| Ingen auth UI | HIGH | Supabase infra klar, ingen login/signup |
| RLS permissive (nullable user_id) | MEDIUM | Blokerer production deploy |
| TS/Python types manuelt duplikeret | MEDIUM | Schema drift risiko |
| ~~Config forms uden validation~~ | ~~MEDIUM~~ | ✅ Fixed session 6 — Zod + backend validation |
| Health check mangler DB/Redis | LOW | H6 parked |
