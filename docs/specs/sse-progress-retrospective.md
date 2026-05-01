# Retrospective: SSE Progress Reporting (Sprint 6B Phase 1a)

> Dato: 2026-04-30
> Scope: PR #26 (a1) + PR #27 (a2) + PR #28 (a3) — combined ~2,100 LOC
> Resultat: 208 tests grønne (111 BE + 97 FE), CI grøn på alle 3 PRs

## Hvad blev shipped

End-to-end real-time pipeline observability i én session:

- **Async run launch** — `POST /runs/async` returnerer 202 + run_id øjeblikkeligt
- **Cooperativ cancellation** — `POST /runs/{id}/cancel` med flag-baseret signalering
- **SSE event-stream** — `GET /runs/{id}/stream` med 7 event-typer
- **Event log** — `run_events` tabel for replay + reconnect-support
- **Heartbeat** — 15s comment-events imod proxy-timeouts
- **Last-Event-ID resume** — reconnect-safe gennem per-run sequence numbers
- **Frontend EventSource** — live step-by-step progress + Stop-knap
- **Tre stacked PRs** — main aldrig brudt undervejs

## Hvad gik godt

### Arkitektur
1. **CQRS-light separation** — Engine emit() → Bus → DB → Stream gør det muligt at tilføje features (logging, metrics, multi-client) uden at røre engine-kerne. Bevisbar via at vi tilføjede SSE i a2 uden at ændre execution.py struktur.
2. **Backward compat strategi** — At bevare sync `POST /runs` mens vi tilføjede `/runs/async` betød main aldrig var halv-brudt. Hver PR var atomisk reviewable.
3. **Per-PR scope-disciplin** — a1 = lifecycle, a2 = streaming, a3 = UI. Hver PR kunne testes selvstændigt før næste blev startet.
4. **Bounded queue + drop-oldest** — Slow client kan ikke blokere engine. Enkel teknik der løser et reelt produktionsproblem.

### Process
1. **Spec-first betalte sig** — Da vi skrev cancel-semantik op i spec (cooperativ, current step finishes), var implementation 5 linjer. Uden spec havde vi diskuteret mid-PR.
2. **Stacked branches gjorde rebase trivielt** — a2 og a3 byggede på lokale commits, rebase efter merge var skip+done.
3. **TDD red→green for hver service-metode** — fanger interface-fejl tidligt. `cancel_requested` default-bug blev fanget af test før det ramte CI.
4. **Per-PR commit-message med spec-link** — fremtidige reviewere kan se "hvorfor er dette bygget".

## Hvad kunne være bedre

### Testdækning
1. **Manglende integration test der starter en rigtig FastAPI server + EventSource** — alle nuværende tests mock'er HTTP eller kører isoleret. Bug i SSE-headers ville først blive fanget i manuel test. **Action:** Tilføj `pytest-httpx` + en e2e-test der bruger `httpx.AsyncClient.stream()`.
2. **Ingen test for thread-to-loop event publishing** — `asyncio.run_coroutine_threadsafe` er en kompliceret bro. Vores tests mocker bus.publish, så hvis publishing ind i loopen fejler, opdager vi det først lokalt. **Action:** Integrationstest med faktisk asyncio.Event mellem to threads.
3. **Ingen test af heartbeat** — Vi har 15s timeout. Test ville kræve mock-time eller kortere interval i test-config. **Action:** Gør heartbeat-interval konfigurerbar via env.

### Robusthed
1. **Single-process antagelse** — RunCoordinator + EventBus er process-lokale dicts. Med mere end én uvicorn-worker bryder cancel + SSE. **Action:** Dokumentér at deploy skal være single-worker indtil vi tilføjer Redis pub/sub. Eller migrér nu hvis vi forventer prod inden Q3.
2. **Engine-thread bus.publish race** — Hvis engine emit'er hurtigere end loopen kan dræne queues, vil vi droppe events. Det er OK for step-events (DB er truth), men terminal-event drop = broken UX. **Action:** Marker terminal events i kø som "non-droppable" eller flush før channel close.
3. **Ingen graceful shutdown** — Hvis processen genstartes mid-run, har vi en run der står som "running" i DB for evigt. **Action:** Startup-task der finder running runs > 1 time gamle og marker them failed.
4. **Unbounded background tasks** — Coordinator har ingen limit på antal samtidige runs. Et stress-scenario kan udsulte event loop. **Action:** Semaphore eller worker pool med max concurrent runs.

### Sikkerhed
1. **Stream endpoint er unauthenticated** — Anyone with run_id kan tappe stream. UUID-gæt er praktisk umuligt (~10^36), men det er ingen reel adgangskontrol. **Action:** Når auth lander (next phase), enforce user_id == run.user_id.
2. **Cancel endpoint samme situation** — Anyone med run_id kan stoppe en kørsel. **Action:** Same as above.
3. **Event payloads kan lække connector-output** — Hvis en SQL-connector returnerer rådata fra DB, ender det i SSE event. **Action:** Connector-spec skal kræve eksplicit `redact()` for sensitive fields. Pålægges som contract i NodeExecutor ABC.
4. **Last-Event-ID parser har ingen øvre grænse** — `int(header_value)` accepterer arbitrære store tal. Ikke reelt sikkerhedsproblem (DB-query bare returnerer tom), men test edge cases. **Action:** Cap til realistisk max sequence (10000?).
5. **CORS er åben** — Vi har ikke set CORS-headers i denne session, men SSE kræver dem. Verificér at FastAPI's CORS middleware ikke står `allow_origins=["*"]` i prod-config.

### Observability
1. **Ingen metrics** — Vi har ingen Prometheus-counter for "runs started", "runs cancelled", "event publish failures". **Action:** Tilføj `prometheus-fastapi-instrumentator` plus custom counters for cancel og publish-drop.
2. **Logging er minimal** — Coordinator logger exceptions men ikke happy path. Debugging produktion kræver mere kontekst. **Action:** Structured logging (loguru eller stdlib JSON formatter) med run_id på hver line.
3. **Ingen distributed tracing** — Når vi får flere services, vil vi gerne korrelere request → run → step → SSE-event. **Action:** OpenTelemetry når vi rammer multi-service.

### UX-mangler
1. **Ingen "step in progress" visuel** — UI viser status som tekst, men ingen progress-bar eller spinner per step. **Action:** Tilføj animeret border/pulse til running step.
2. **Ingen estimeret tid** — Når step kører i 30+ sekunder ved bruger ikke om det er normalt. **Action:** Log historisk per-node-type duration → vis "average time: 12s" i tooltip.
3. **Ingen run history filter** — Run history endpoint findes men frontend mangler det helt. **Action:** Phase 1b (allerede planlagt).
4. **Cancel toast er passiv** — "Cancellation requested" — men brugeren ved ikke hvor lang tid current step tager. **Action:** Vis countdown eller "step X is finishing..."

## Feature-muligheder for next phase

### Foundation-relevant (kort sigt, 1-2 sessions hver)
1. **Run history frontend** — backend klar, mangler RunHistoryPanel + filter UI
2. **AI executor med streaming tokens** — udnyt SSE-infrastrukturen til Anthropic/OpenAI streaming
3. **REST API connector** — første rigtige executor (stub erstattes), bruger validering fra session 6
4. **Persistent run_events cleanup** — TTL-baseret deletion, fx 30 dage retention
5. **Run replay i UI** — vis en gammel run som om den lige var kørt (afspil events fra DB)

### B2B-grade (mellem sigt, 3-5 sessions hver)
1. **Multi-client viewing** — kollega kan se din kørsel; kræver auth+RLS først
2. **Webhook trigger** — pipeline kan udløses fra ekstern HTTP-call, returnerer run_id
3. **Schedule trigger** — cron-baseret pipeline-execution (Celery beat eller GitHub Actions style)
4. **Pipeline versioning** — gem snapshot ved hver kørsel, vis diff
5. **Step retry/resume** — efter failed step, retry fra failed-step (ikke hele runnet)
6. **Conditional edges** — `if step_X.output.matches(condition)` for branch-baseret flow
7. **Parallel step grouping** — eksplicit "kør disse 3 sammen" i stedet for at stole på topological-sort race
8. **Resource limits per run** — max 100MB RAM, max 60s per step, kill on overflow

### Enterprise-grade (lang sigt, full sprint hver)
1. **Audit log** — hver bruger-action (cancel, schedule, manual run) i append-only log
2. **Role-based access** — owner / editor / viewer per pipeline
3. **Workspace/team-niveau isolation** — multi-tenant Postgres med RLS pr workspace_id
4. **Pipeline templates marketplace** — community-shared pipelines med variable substitution
5. **Cost budgets** — "stop alle pipelines hvis månedlig OpenAI-cost > $X"
6. **SOC2/GDPR mode** — DPIA-kompatibel data handling, EU-region deployment, BYOK encryption-at-rest

### Connector-økosystem (parallelt med ovenfor)
1. **REST API** (eksisterende plan)
2. **SQL** (Postgres, MySQL, SQLite)
3. **File** (CSV, JSON, S3)
4. **AI** (Anthropic, OpenAI, Azure OpenAI, Ollama for selvhost)
5. **HUMAN approval step** (pause → review-link → approve/reject → resume)
6. **Webhook out** (POST result til ekstern URL)
7. **Email/Slack notification** (low-effort, høj brugerværdi)
8. **Vector DB** (Pinecone, Weaviate, Qdrant — for RAG-pipelines)

## Anbefalet næste fase

**Top 3 prioriteret efter feature-rich-værdi vs. effort:**

1. **REST API Connector** (Phase 1c i den oprindelige plan)
   - Erstatter første stub med rigtig implementation
   - Bygger på validate_config() pattern fra session 6
   - Beviser end-to-end flow med rigtig connector → SSE → UI
   - 1-2 sessions

2. **Run History Frontend** (Phase 1b)
   - Backend 100% klar, kun UI mangler
   - Lavt risk, kort effort
   - Komplementerer SSE: live progress + historisk overblik = komplet observability story
   - 1 session

3. **AI Executor med streaming** (mest pedagogisk, mest produktværdi)
   - Bruger SSE-infrastrukturen til at streame tokens
   - Anthropic + OpenAI med BYOK
   - Cost-tracking pr. step (vi har allerede `cost_usd` felt)
   - Beviser at SSE-arkitekturen kan håndtere fine-grained sub-step events
   - 2-3 sessions

## Læring til mig selv (Simon)

- **Stacked branches** = enkelt mønster der undgår "main brudt mens jeg arbejder". Brug det altid for multi-PR features.
- **Spec-first** for større features sparer tid samlet — diskussionen sker oppe i text-form, ikke nede i kode-review.
- **CQRS-light** er ikke kun for store systemer — selv en monolith har gavn af at separere "command" (write-side) fra "query" (read/observe-side). SSE-stream er en query der observerer command-side state.
- **Cooperativ cancellation** er det rigtige default. Hård cancellation (kill thread) bryder connector-side effects. Enhver workflow-engine bør være kooperativ.
