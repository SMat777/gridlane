# 06. Observability: at kunne se hvad systemet faktisk gør

> Du sidder i et hus hvor ingen kan give dig modspil på et designvalg — men hvor alle kan verificere et tal.
> Det er også det ene spor hvor arbejde og øvebane peger samme vej: dokument-ingestion, leverandørstamdata og udløbende certifikater er præcis de systemer hvor "hvorfor skete det for netop den tenant kl. 14.07" er svært at besvare.
> Og det giver dig det ene bevis der ikke kan snydes: en service du selv har driftet, med hændelser du selv har stået i.

## Progressionen: fire niveauer

| Niveau | Kendetegn | Output |
|---|---|---|
| 1. Jeg tilføjer logs | Fejlfinding er at læse tekst | Log-linjer ingen kan aggregere |
| 2. Jeg instrumenterer | Auto-instrumentering, custom spans og metrics, korrelation via `trace_id` | En service man kan fejlsøge i |
| 3. Jeg designer signaler | Beslutter hvad der bliver metric, span og log — og hvad der aldrig sendes | ADR'er, SLO-dokument, byte-budget per request |
| 4. Jeg designer et program | Instrumenteringsstandard, datapolitik, omkostningsmodel, alert-governance | Dokumenter andre kan følge uden dig |

Niveau 2 tager seks uger. Niveau 3 er hvor arkitektarbejdet begynder, og hvor næsten alle stopper — niveau 4 er ikke sværere teknisk, det er skrivearbejde og disciplin.

## Den mentale model: wide events, ikke tre signaler

De tre signaler (logs, metrics, traces) er en **lagringsmodel**, ikke en arkitekturmodel — formuleret af leverandører der solgte tre produkter. Når spørgsmålet er konkret — *hvorfor fejlede netop denne leverandørs certifikat-upload for netop denne tenant kl. 14.07* — kan du ikke joine tre datasæt i hovedet. Modellen du skal tænke i er **én bred begivenhed per arbejdsenhed** med 30-80 attributter, som du skærer i bagefter; i .NET er det tættest på "en span med mange attributter".

Konkret for dokument-ingestion: én span per upload med tenant, dokumenttype, filstørrelse, retry-flag, køalder ved consumption, den valideringsregel der fældede den, udtrukket udløbsdato og kilde-ERP. En auto-instrumenteret span fortæller dig at `POST /api/documents` tog 340 ms — og intet af ovenstående. Span-design er beslutningen om hvilke spørgsmål du kan stille om tre måneder, truffet i dag uden at vide hvilke fejl der kommer. Der kommer aldrig en ticket på det.

## Signalvalg: den ene tabel du skal kunne udenad

| Spørgsmålstype | Signal | Domæneeksempel | Regel |
|---|---|---|---|
| Skal jeg alerte på det? | Metric | Fejlrate på uploads, p95 valideringstid | Lav kardinalitet. Samples aldrig |
| Skal jeg undersøge det bagefter? | Span | tenant_id, supplier_id, dokument-id, regel-id | Høj kardinalitet hører hjemme her |
| Skal jeg læse forløbet? | Log | Valideringsafvisning med årsag, korreleret via `trace_id` | Message templates, aldrig interpolation |

**Kardinalitetsfælden har et konkret tal:** OpenTelemetry .NET har default cardinality limit på **2000 per metric**, konfigurerbar via View API og `MetricStreamConfiguration.CardinalityLimit`. Siden 1.10.0 droppes målinger over grænsen ikke — de samles i en overflow-bucket. Det er værre end et crash: `tenant_id` som metric-dimension vælter ikke systemet, det ødelægger dine tal lydløst fra kunde nummer 2001, og du opdager det når kunden spørger hvorfor tallene ikke passer.

## Modenhedsstatus 2026: det de fleste blogposts tager fejl af

| Komponent | Status | Konsekvens |
|---|---|---|
| OTel .NET SDK 1.18.0 + Instrumentation.AspNetCore / .Http / .SqlClient | Stabile på alle tre signaler (EntityFrameworkCore er 1.18.0-beta.1, Exporter.Zipkin deprecated) | Backend-instrumentering kan forsvares i en ADR i dag. Beta-valget skriver du ned |
| @opentelemetry/instrumentation 0.222.0, auto-instrumentations-web 0.67.0 (kernen sdk-trace-web 2.11.0 er stabil, men er ikke den pakke en React-app bruger) | 0.x, ingen garanti | **Ikke OTel til browser-RUM i produktion.** Brug `@microsoft/applicationinsights-web` 3.4.4 |
| semconv v1.44.0: HTTP spans Stable, messaging Development (netop omdefineret), db Mixed, browser Development; exceptions-på-spans deprecated | Delvist ustabile | Alerts på Development-attributter brækker ved næste opgradering, om natten |
| Native OTLP-ingestion; to konkurrerende distros (Azure Monitor Distro 1.6.0 GA mod nyere Microsoft OpenTelemetry Distro) | Collector-stien GA (>= 0.132.0, azureauthextension, DCE/DCR, managed identity); AMA/AKS og Health models preview | Vælg `Azure.Monitor.OpenTelemetry.AspNetCore`, skriv ADR, hold øje med navne-churn. Preview er demonstration, aldrig afhængighed |

At kunne sige **nej til browser-OTel med en genovervejelsesbetingelse** er præcis forskellen på en udvikler og en arkitekt.

**Logging i .NET 2026:** `Microsoft.Extensions.Logging` med message templates og source-generated `LoggerMessage`, plus `Microsoft.Extensions.Telemetry` og `Microsoft.Extensions.Compliance.Redaction` (begge 10.10.0, GA). Serilog.AspNetCore 10.0.0 lever fint, men at vælge det i en ny .NET 10-service kræver nu en begrundelse, ikke en vane.

**Din bedste døråbning hele året:** .NET 8 (LTS) går EOL **10. november 2026**; .NET 9 (STS) nåede allerede EOL 12. maj 2026. .NET 10 er LTS til november 2028. Er LeanLinking på .NET 8, kommer der en tvungen migration. Foreslå ikke en strategi — spørg stifteren: *"Når vi alligevel skal på .NET 10, vil I have at jeg samtidig opgraderer instrumenteringen på den service jeg arbejder i? Cirka en dags ekstra arbejde."* Det er et lille ja at give.

## Cost er et arkitekturproblem, ikke et driftsproblem

Det er den vinkel ledelsen forstår uden oversættelse, og derfor den der giver dig mandat hurtigst. Mekanikken: Azure Monitor Logs fakturerer per GB (10⁹ bytes) ingest. Standardkolonner er undtaget, så faktureret størrelse er typisk ~25% under rå JSON, op til 50% for små events. `_IsBillable` afgør om en tabel tæller; AzureActivity, Heartbeat, Usage og Operation er gratis. Commitment tiers starter ved 100 GB/dag og gælder kun Analytics — altså ikke dig.

| Table plan | Query | Alerts | Fælde |
|---|---|---|---|
| Analytics | Gratis, 31 dages retention inkl. | Ja | Dyrest ingest |
| Basic | Per GB **scannet** | Begrænset | Besparelsen vender ved hyppige queries |
| Auxiliary / Lake | Per GB scannet | **Nej — virker ikke** | Opdages først når en alert er holdt op med at fyre |

Kun **ét plan-skift per tabel per uge**: vælg forkert, og du er låst i syv dage.

Rækkefølgen af indgreb, i den orden en arkitekt siger dem: (1) instrumentér mindre, (2) sampling i SDK'et, (3) DCR ingest-transformationer der dropper felter **før** de bliver til penge, (4) summary rules, (5) table plans, (6) daily cap — kun som forsikring. Microsofts egen doc siger at når cap'en rammes, er du "effectively blind to the current state of your monitored environment".

To ting om sampling: **metrics samples aldrig** (derfor står alerts på metrics, ikke på traces), og **trace-based sampling for logs dropper logs der hører til usamplede traces** — så en alert på en log-linje forsvinder stille. Verificér med Microsofts egen query: `union requests,dependencies,exceptions,traces | summarize RetainedPercentage = 100/avg(itemCount) by bin(timestamp,1h), itemType`.

## Persondata i telemetri: her mødes faget og domænet

Telemetri fra et leverandør- og compliance-produkt indeholder uundgåeligt leverandørnavne, kontaktpersoner, certifikatnumre og dokument-metadata. Microsofts prioriterede rækkefølge: (1) filtrér eller anonymisér med **DCR-transformationer** — deres ord: "by far the best option"; (2) normalisér til interne ID'er med en lookup-tabel hvor du kan slette én række; (3) først derefter Delete Data og Purge API. Detaljen der ændrer regnestykket: *"Deleting or purging data doesn't affect billing."*

Byg redaction i tre lag fra første commit: `Microsoft.Extensions.Compliance.Redaction` i koden, en OTel-processor, en DCR-transformation. Skriv en **telemetri-datapolitik på én side**: hvilke felter må logges, hvilke aldrig, hvem har læseadgang, hvor længe, og hvad der sker ved en sletteanmodning med legal hold.

## Spikes: hvad du bygger, og hvad der ligger på disken bagefter

Alt hænger på én opdigtet service, **SupplierDocs**: modtager leverandørdokumenter, validerer asynkront via en kø, udtrækker certifikaters udløbsdato, udsender påmindelser. Multi-tenant fra dag ét, ingen UI ud over Swagger. Udvikl og verificér lokalt mod **Aspire-dashboardet i standalone mode** over OTLP — nul Azure-kroner, og kun lokalt, for det accepterer uautentificeret telemetri som default.

| Spike | Tid | Fysisk output |
|---|---|---|
| **O-1** Fuld OTel-instrumentering fra nul | 2 uger, ~25 t | ADR-001 (distro-valg med genovervejelsesbetingelse), ADR-002 (auto-instrumenteringer slået **fra**), diagram over telemetri-stien med sampling- og omkostningspunkt, MB per 1000 requests før/efter |
| **O-2** Span-design og sampling under tvang | 1-2 uger, ~15 t | Byte-budget per request, ADR-003 med **listen over spørgsmål du ikke længere kan besvare**, før/efter MB/måned |
| **O-3** SLI, SLO, error budget, burn-rate alerts | 2 uger, ~25 t | SLO-dokument per SLI, burn-rate alerts som Bicep i git, KQL der beregner error budget i hånden, request-based mod window-based, ADR-004 |
| **O-4** Kardinalitetseksplosion og omkostningsmodel | 1 uge, ~12 t | Model på målte `_BilledSize` ved 1x/10x/100x, dokumenteret overflow-adfærd, ADR-005 (kardinalitetspolitik), notat med tre indgreb: kroner sparet mod indsigt tabt |
| **O-5** (forfremmet til drift) 10 ugers drift med provokerede incidents | 10-12 uger, 2-3 t/uge | Tre blameless postmortems, SLO-rapport, log over hvad der brækkede dine dashboards, liste over alerts du **slettede** |
| **O-6** (valgfri, ryger først) Health model og governance | ~15 t | Health model i Bicep, Azure Policy for diagnostic settings, instrumenteringsstandard på to sider |

**O-2 ligner rigtigt arkitektarbejde mest.** Fast loft: 150 MB/måned ved 50.000 requests/dag, mens fem spørgsmål stadig skal kunne besvares — flest fejlede uploads per tenant i sidste uge; p95 valideringstid per dokumenttype; ældste kø-besked i går; hyppigst fejlende valideringsregler og for hvilke leverandører; hvad der skete da upload nr. X fejlede kl. 14.07. Regn baglæns til et byte-budget per request, byg tre lag (altid-metrics, samplede spans, kun-ved-fejl-logs), og dokumentér tabet. I O-3 skriver du tilsvarende SLI'en i ord først — *"andelen af dokument-uploads der kvitteres inden for 3 sekunder, målt på serversiden, ekskl. filer over 50 MB"* — og opdager at du ikke kan måle den med din nuværende instrumentering. Det er pointen.

**O-5 kan ikke hastes — start senest måned 5-6.** Fem fejlmønstre med en uges mellemrum: en afhængighed der bliver langsom men ikke fejler; en poison message der retryer i det uendelige; en bagudinkompatibel schema-ændring deployet mens gamle beskeder ligger i køen; et certifikat der udløber; en deployment der 20-dobler telemetrivolumen og rammer din daily cap, så du bliver blind midt i en hændelse. Den sidste er den mest lærerige. Notér tre tidspunkter: fejlens opståen, **din** opdagelse, mitigation.

## Ressourcer

| Ressource | Prioritet | Tid | Hvad du henter |
|---|---|---|---|
| OTel .NET `docs/logs`, `docs/metrics`, `docs/trace` — github.com/open-telemetry/opentelemetry-dotnet/tree/main/docs | Kerne | 4-6 t | Mere aktuel end nogen bog. Bedste kardinalitetsforklaring der findes |
| MS Learn: Analyze monitoring data with KQL — learn.microsoft.com/training/paths/analyze-monitoring-data-with-kql/ | Kerne | 6-8 t | KQL-grundlaget. Ikke også SC-200 eller Fabric |
| Log Analytics demo — aka.ms/lademo (alt. portal.loganalytics.io/demo) og Kusto Detective Agency — detective.kusto.io | Kerne | 45 min × 2/uge, 10-15 t | Rigtige data uden egen Azure-konto; løs 4-5 cases |
| Google SRE Workbook kap. 2 og 5 — sre.google/workbook/table-of-contents/ | Kerne | 4-5 t | Burn-rate-matematikken bag Azures burn-felter |
| Google SRE Book kap. 3, 4, 6, 12, 14, 15 — sre.google/sre-book/table-of-contents/ | Kerne | 5-6 t | Error budgets, golden signals, incident command |
| Azure Monitor: service-level-indicators-create, logs/cost-logs, logs/personal-data-mgmt, containers/opentelemetry-options | Kerne | 6 t i alt | SLO-produktet, fakturamekanikken, persondatarækkefølgen, distro-valget |
| Observability Engineering (Majors, Fong-Jones, Miranda) | Kerne | 8-10 t | Wide events. Del I-II, spring build-vs-buy over (uverificeret) |
| Aspire standalone dashboard — github.com/microsoft/aspire | Kerne | 2 t | Gratis lokal viewer. Halverer Azure-regningen |
| Azure Monitor: app/opentelemetry-sampling og logs/logs-table-plans (+ transformations, summary rules, daily cap) | Støtte | 3 t | Sampling-fælderne, verifikations-KQL'en og den faktiske cost-governance |
| OpenTelemetry Demo — github.com/open-telemetry/opentelemetry-demo; Azure Monitor Baseline Alerts — github.com/Azure/azure-monitor-baseline-alerts; Must Learn KQL — github.com/rod-trent/MustLearnKQL | Støtte | 5 t + opslag | Span-design i en rigtig kodebase (spring Kubernetes over), alerting som governance, KQL-opslagsværk |
| AZ-400 | Senere | 40-60 t | Eneste Azure-cert med reelt observability-domæne. **(uverificeret)** — tjek selv eksamenskode og pris. Deadline-motor, først efter O-3 og O-5 |

Learn-URL'erne følger formen `learn.microsoft.com/azure/azure-monitor/<sti>`; indholdet er verificeret i Microsofts offentlige docs-repo, selve URL-formen er ikke afprøvet **(uverificeret)**. Alle beløb i kroner er **uverificerede** — hent priserne for din region selv før O-4.

**Fravalgt bevidst, og du skal kunne begrunde det:** Prometheus/Grafana i dybden, Jaeger og Zipkin, ELK/OpenSearch, eBPF og continuous profiling (OTLP-profiles er stadig Development), custom Collector-builds, og OpenTelemetry- eller SRE-"foundation"-certifikater.

## Timebudget

| Post | Timer |
|---|---|
| O-1 til O-4 | 77 |
| O-5 (drift over 10-12 uger) | 28 |
| KQL, 45 min × 2/uge i 10-12 uger | 15 |
| Læsning | 10 |
| **I alt** | **130** |

Det er 20-25% af din samlede spike-kapacitet inden for 10-15 timer/uge. O-6 findes ikke i budgettet: skrider timerne, laver du kun instrumenteringsstandarden — tre timers arbejde, og det mest LeanLinking-relevante artefakt i hele sporet.

## På jobbet, uden at spørge om lov

- **Før spørgsmålsloggen.** Hver gang nogen stiller et spørgsmål om produktionsadfærd som ingen kan besvare på 10 minutter: dato, hvem spurgte, spørgsmålet, hvor lang tid det tog. Efter 8-12 uger har du ikke en mening om observability — du har data om dit eget firma. Mål samtidig find-tid mod fix-tid på egne tickets; er forholdet 5:1, har du et argument ingen kan modsige.
- **Instrumentér den kode du alligevel rører,** og gem hver KQL-query der besvarede et rigtigt spørgsmål. En `Activity`-span, to-tre attributter, message templates — inden for ticketens scope. Efter 20-30 queries: en side med "Queries til de spørgsmål vi får tit".
- **Lær firmaets Azure-regning at kende.** Med kun læseadgang: `Usage | where IsBillable == true | summarize sum(Quantity) by DataType, bin(TimeGenerated, 1d) | render timechart`. Efter en time ved du hvad I betaler for, og om der er en tabel ingen bruger.
- **Spørg småt, ikke stort.** "Må jeg få Monitoring Reader på vores App Insights?" — ikke "må jeg lave en observability-strategi?". Stigen er måling, spørgsmålslog, ét A4 med kroner, et to-ugers forsøg med succeskriterie **og** exit-betingelse. Ingen teknik i pitchen: kun timer, kroner og daterede eksempler.

## Eksternt modspil: den del du ikke må springe over

Ingen på arbejdet kan fortælle dig at dit span-design er forkert. Den største risiko i sporet er at du øver dig forkert i 12 måneder uden at opdage det. Løs det mekanisk.

- **Publicér ADR-003 og ADR-005 offentligt** og bed eksplicit om modsigelse. En ADR med et dokumenteret tab inviterer skarpere kritik end en blogpost der forklarer noget.
- **Byt code review** med én uden for firmaet der arbejder med .NET og Azure: du reviewer hans instrumentering, han din. Aftal kadence, ikke goodwill.
- **Stil ét spørgsmål i alle interne code reviews:** "hvordan ser vi at det her virker i produktion?" Efter et par måneder stiller andre det selv.
- **Lad en udefrakommende teste dig** på KQL og på telemetri-stien med uforberedte spørgsmål. Selvevaluering er værdiløs her.

## Faldgruber

1. **At instrumentere alt og drukne.** Modgiften er tvang: definér først de fem spørgsmål telemetrien skal besvare, instrumentér derefter kun det.
2. **At forveksle dashboards med observability.** Et dashboard besvarer spørgsmål du kendte i forvejen. Bruger du over 10% af tiden på at gøre dashboards pæne, er du på afveje — og det føles produktivt.
3. **At alerte på årsager i stedet for symptomer.** Testen: hvem vågner, hvad gør de, hvad sker der hvis ingen reagerer i to timer. Består den ikke, slettes alerten.
4. **At sætte SLO'en til 99,9% fordi det lyder pænt.** Og værre: en SLO uden konsekvens ved brud er bare en graf. Sig det højt, også når det er ubelejligt.
5. **At logge PII og opdage det bagefter.** Oprydningen fjerner ikke regningen, og med leverandørnavne og certifikatnumre i telemetrien er det ikke hypotetisk.
6. **At lære Prometheus og Grafana i dybden fordi internettet gør det.** Timer der ikke bliver brugt på KQL, hvor afkastet er ti gange større. Samme fejl: at læse Google SRE-bogen forfra.
7. **At glemme at slukke.** Budget-alarm før første deployment, daily cap fra dag ét, ressourcegruppen slettes efter hver ikke-forfremmet spike. Kun O-5's service får lov at køre.
8. **At tage en cert i stedet for at drifte noget.** Ti ugers drift med tre postmortems giver et ægte svar når nogen spørger "fortæl om en gang noget gik galt".
9. **At bygge en observability-platform i stedet for at instrumentere én service ordentligt.** En arkitekt kendes på dybden af sine beslutninger, ikke på bredden af sit stillads. Og O-5 må ikke skride: kalendertid kan ikke komprimeres.

## Sådan ved du at du kan det

- [ ] Du kan, foran en fremmed, tegne telemetri-stien fra et klik i frontenden til en lagret række i Log Analytics — inkl. hvor context propageres, hvor den **tabes** (baggrundsjobs, kø-consumers, `Task.Run`), hvor sampling besluttes, hvor persondata kunne slippe med, og hvor der bliver brugt penge — på under 10 minutter uden noter.
- [ ] Der findes en service du har driftet uafbrudt i mindst 8 uger mod egne SLO'er, og du kan vise error budget-forbruget som graf og forklare hvert udsving.
- [ ] Tre skrevne postmortems med tidslinje i minutter, detection-tid målt **separat** fra diagnose- og mitigationstid, årsag skelnet fra udløsende faktor, og mindst ét udført action item — med commit-link.
- [ ] En anden person stiller dig et KQL-spørgsmål du aldrig har set, og du besvarer det på under fem minutter uden at slå syntaks op, inkl. join, `summarize` med `bin()` og `percentile()`.
- [ ] Du kan sige i kroner, med målte `_BilledSize`-tal bag, hvad servicen koster per måned, og ved 10x og 100x — opdelt på table plan.
- [ ] For hver alert kan du sige hvem der vågner, hvad de gør, og hvad der sker hvis ingen reagerer i to timer. Og du har **slettet** mindst én alert du selv byggede. Sletningen er det egentlige målepunkt.
- [ ] Mindst én ADR hvor du siger nej til noget populært med en eksplicit genovervejelsesbetingelse — ingen OTel browser-instrumentering, fordi pakkerne er 0.x; vi genovervejer når `auto-instrumentations-web` når 1.0. Og du kan navngive to andre ustabile ting i landskabet lige nu og hvad du gør anderledes.
- [ ] Du kan forklare hvorfor den samme 99,9%-SLO giver to forskellige tal målt request-based mod window-based.
- [ ] En instrumenteringsstandard på maks to sider, som en kollega der ikke kender OpenTelemetry har fulgt på under 30 minutter. Testen er kollegaens stopur, ikke din vurdering.
- [ ] Spørgsmålsloggen har 20 daterede indførsler, er konverteret til ét A4 med timer og kroner, og er vist til én med beslutningskraft. Om der blev sagt ja er ikke målepunktet — at dokumentet findes og er set, er.
- [ ] Mindst én ændring i produktionskoden som du foreslog, som ikke stod på en ticket, og som blev merged. Nul er et rødt flag ved kompetenceporten i måned 9-10.
