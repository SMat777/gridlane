# 02. Det tekniske fundament: dybden der gør dig troværdig

> Du har ingen titel, og der findes ingen arkitektstige at klatre på hos en arbejdsgiver med ni ansatte. Der er heller ikke noget review board der kan give dig ret.
> Det eneste du kan handle med er at have ret om ting andre ikke kan verificere på fornemmelse — og kunne fremvise tallet der beviser det.
> Dybden er derfor ikke forberedelse til arkitektrollen. Den er rollen, indtil nogen giver den et navn.
> Til gengæld sidder du der hvor certifikater udløber i millionvis, hvor leverandørstamdata indlæses fra fremmede ERP-systemer, og hvor et revisionsspor skal kunne holde til en audit. Det er ægte arkitekturproblemer, og de er gratis for dig.

## Rækkefølgen der afgør alt: måling først, ikke sidst

Næsten alle læringsplaner placerer profilering og observability til sidst, under "advanced". Det er den forkerte rækkefølge. Uden et måleapparat er alt hvad du lærer bagefter uverificerbart, og ethvert arkitekturargument du fremfører reduceres til en mening. En junior med meninger taber altid mod en senior med meninger. En junior med et reproducerbart tal taber ikke.

Den anden grund til at måleapparatet skal stå færdigt i uge 1-2: arkitektur er trade-off-analyse, og trade-off-analyse kræver at kende **størrelsesordenen** på omkostningskurven. Bøger fortæller dig at trade-offs findes. Kun målinger fortæller dig hvad de koster. Du kan ikke vide hvad et netværkshop, en Gen2-collection eller 40.000 ekstra logical reads koster, før du har målt et. Størrelsesordenen er hele jobbet; resten er ordforråd.

Adgangsbilletten til arkitekturbøgerne er derfor konkret og falsificerbar: **én** service du kan instrumentere, load-teste, profilere, finde flaskehalsen i, fixe, bevise fixet med tal, deploye uden nedetid, rulle tilbage, og udvikle både databaseskema og API-kontrakt på uden at brække en consumer. Kan du ikke det hele, er *Fundamentals of Software Architecture* ordforråd uden dækning — og en senior hører forskellen på første sætning.

## Hvor din leverage ligger

Supplier compliance er relationelt, transaktionstungt, tenant-partitioneret og skævt fordelt (nogle kunder har en uforholdsmæssig stor andel af dataen). Det flytter datalaget øverst på din liste — over distributed systems-teori, over microservices, langt over Kubernetes.

| # | Kompetence | Hvorfor lige den, lige her | Niveau du skal nå |
|---|---|---|---|
| 1 | SQL og query-planer | Højest rangerende enkeltkompetence i et dokument- og leverandørtungt LOB-SaaS. De fleste .NET-udviklere kan skrive SQL og kan ikke læse en plan | Stærk |
| 2 | Måling, profilering, observability | Fundamentet under alt andet. Konverterer hurtigst til synlighed på jobbet | Stærk |
| 3 | Transaktioner og isolationsniveauer | To samtidige godkendelser af samme dokument der begge passerer en check-then-act — det er ikke akademisk hos jer | Stærk |
| 4 | Datamodellering og multi-tenancy | Tenancy-modellen bestemmer omkostningsstruktur, blast radius og hvad I kontraktuelt kan love en kunde | Stærk |
| 5 | Drift: deploy, rollback, bagudkompatibilitet | Uden det er du designer, ikke arkitekt. Kan ikke simuleres | Kompetent, gerne stærk |
| 6 | API-design: versionering, fejlkontrakter, idempotens | Integrationer mod kunders ERP-systemer gør bagudkompatibilitet til forretningskritik | Kompetent |
| 7 | Async/await og concurrency | Fire fejlmønstre vælter ellers velskrevne .NET-services under last. Usynlige i code review | Kompetent |
| 8 | Allokering og GC | Den skjulte variabel bag halvdelen af de p99-problemer folk tilskriver databasen | Kompetent |
| 9 | Systematisk læsning af ukendt kodebase | Dit faktiske daglige arbejde som ticket-taker, og dit billigste synlighedskort | Stærk |
| 10 | Caching og invalidering | I et system hvor et certifikat kan være udløbet, er staleness-vinduet en juridisk størrelse | Kompetent |
| 11 | Teststrategi som arkitekturbeslutning | Bestemmer hvor hurtigt systemet kan ændres — altså den modificerbarhed alle påstår de optimerer for | Kompetent |
| 12 | Kalibrering: prædiktion før måling | Metakompetencen der gør alle de andre falsificerbare | Stærk |

To rækkefølgekrav der ikke må byttes om af bekvemmelighed: **lær SQL før EF Core**, og **byg måleapparatet før du optimerer noget som helst**. Den omvendte rækkefølge producerer udviklere der ikke kan diagnosticere deres eget ORM, og optimeringer der er ritual.

## Selvvurdering: tre niveauer med spørgsmål du ikke kan bluffe dig igennem

Scoringsreglen: du er på det niveau hvor du kan svare ja til **hvert** spørgsmål uden noter, og pege på et artefakt der beviser det. Ét nej trækker dig ned et niveau. Vurder dig selv i dag, i måned 6 og i måned 9.

**Niveau 1 — du kan bruge det.** Baseline. Skal være passeret ved udgangen af måned 2.

- Kan du starte `dotnet-counters` mod en kørende proces og sige hvad ThreadPool Queue Length betyder?
- Kan du skrive "nyeste gyldige certifikat per leverandør" i ren SQL uden ORM og uden at slå syntaks op?
- Kan du forklare hvad en transaktion garanterer, og hvad en dirty read er?
- Kan du deploye din egen service gennem en pipeline du selv har sat op?
- Kan du sige hvilken SQL EF Core genererer for en simpel Where plus Include?
- Kan du forklare hvorfor `.Result` på en async-metode er farligt — uden at sige "det er bare dårlig praksis"?

**Niveau 2 — du kan diagnosticere det.** Målet for måned 6.

- Får du symptomet "endpointet er langsomt om morgenen", vælger du selv rigtigt værktøj (counter, trace, dump, gcdump eller benchmark) uden at prøve dem alle?
- Kan du læse en execution plan og udpege den dyreste operator uden at et værktøj markerer den — og forklare hvorfor den er dyr i logical reads og cardinality-estimat?
- Kan du navngive hvilket isolationsniveau der forhindrer hvilken anomali, og reproducere mindst én af dem deterministisk på under 30 minutter?
- Kan du forklare hvorfor Azure SQL Database og on-prem SQL Server opfører sig forskelligt på samtidighed, fordi RCSI er slået til som default det ene sted og fra det andet?
- Kan du tage fem foreslåede API-ændringer og sige, med bevis, hvilke der brækker en consumer?
- Kan du rulle et deploy tilbage under tidspres, med en runbook du selv har skrevet og brugt?
- Kan du sige staleness-vinduet på en cache i sekunder, og hvem der bærer risikoen for det?
- Kan du læse MemoryDiagnoser-output og skelne en optimering der virkede fra en der bare føltes rigtig?

**Niveau 3 — du kan prædiktere det.** Målet for måned 9-12. Det er her titlen bliver bærbar.

- Kan du sige p99 og allokeringer per request for et endpoint **før** du måler, og ramme inden for en faktor 10 konsistent — dokumenteret i en prædiktionslog hvor fejlmarginen er faldet målbart over seks måneder?
- Kan du prædiktere execution plan og logical reads for en forespørgsel før du kører den?
- Kan du sige "det indeks vil ikke hjælpe, og her er hvorfor" før nogen har brugt en dag på det?
- Kan du argumentere **imod** den mere sofistikerede løsning i et designmøde med et tal du selv har målt?
- Kan du levere dataflow-diagram, tre sandsynlige fejlmønstre og én sundhedsmetrik for et modul du aldrig har set, på under 45 minutter?
- Kan du sige prisen på dit eget idempotenslag i millisekunder og i ekstra database-writes?
- Kan du navngive tre ting du var sikker på og tog fejl om, og præcis hvad målingen viste?

Det sidste spørgsmål er det hårdeste og det mest afslørende. "Jeg har brugt det" og "jeg forstår det" føles fuldstændig ens indefra. Prædiktion er den eneste måde at skelne dem uden en ekstern bedømmer — og du har ingen ekstern bedømmer på arbejdet.

## Ressourcerne, med prioritet og timeforbrug

Alt bygges på .NET 10 (LTS, support til 14. november 2028). .NET 8 og .NET 9 udløber begge 10. november 2026 — om to måneder. Jag ikke .NET 11; den er STS, og I bliver på LTS i årevis.

| Prioritet | Ressource | Timer | Hvornår | Pris | URL |
|---|---|---|---|---|---|
| Kerne | Use The Index, Luke! (Winand) | 6-8 | Måned 2, sideløbende med spike 4 | Gratis | https://use-the-index-luke.com/sql/table-of-contents |
| Kerne | .NET diagnostics tools overview | 4 | Spike 1, derefter opslag | Gratis | https://learn.microsoft.com/en-us/dotnet/core/diagnostics/tools-overview |
| Kerne | BenchmarkDotNet (brug 0.15.x, ikke 0.16-preview) | 3 | Spike 1, derefter løbende | Gratis | https://benchmarkdotnet.org/ |
| Kerne | Testcontainers for .NET | 4 | Spike 1, fundament under alle spikes | Gratis | https://dotnet.testcontainers.org/ |
| Kerne | Hermitage (isolationsniveau-testsuite) | 6-8 | Spike 6 | Gratis | https://github.com/ept/hermitage |
| Kerne | Stephen Cleary om ConfigureAwait i .NET 8 | 5-6 | Spike 2 | Gratis | https://blog.stephencleary.com/2023/11/configureawait-in-net-8.html |
| Kerne | sharplab.io (uverificeret URL, men velkendt værktøj) | 10 min ad gangen | Løbende | Gratis | https://sharplab.io |
| Kerne | EF Core 10 breaking changes | 2 | Spike 5 og EOL-assessmentet | Gratis | https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes |
| Kerne | RFC 9457 Problem Details (afløste RFC 7807) | 2 | Spike 7 | Gratis | https://www.rfc-editor.org/info/rfc9457/ |
| Kerne | Idempotency-Key — stadig IETF-draft, ikke RFC | 1 | Spike 8 | Gratis | https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07 |
| Kerne | Azure Architecture Center: tenancy models | 5 | Spike 9 | Gratis | https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/tenancy-models |
| Kerne | MADR 4.0.0 — vælg én ADR-template og hold fast | 1 + 45-60 min pr. ADR | Fra spike 1 | Gratis | https://adr.github.io/madr/ |
| Kerne | .NET supportpolitik (versionslivscyklus) | 0,3 | Uge 1, bogmærk | Gratis | https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core |
| Kerne | DDIA 2. udgave (Kleppmann og Riccomini, 2026) | 25 | Måned 3-6, ét kapitel i den uge dets spike kører | Bog | https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ |
| Kerne | The Programmer's Brain, kun Del 1 | 4 | Måned 1-2 | Bog | https://www.manning.com/books/the-programmers-brain |
| Støtte | Brent Ozar First Responder Kit | 4 | Spike 4 | Gratis | https://github.com/BrentOzarULTD/SQL-Server-First-Responder-Kit |
| Støtte | Kendra Little om read committed | 1-2 | Spike 6 | Kursus | https://kendralittle.com/course/read-committed-is-bonkers/ |
| Støtte | Aspire 13.x som lokalt stillads | 4 | Spike 1 | Gratis | https://aspire.dev/whats-new/aspire-13/ |
| Støtte | OpenTelemetry semantic conventions (status "Mixed") | 2 | Spike 1 | Gratis | https://opentelemetry.io/docs/specs/semconv/http/ |
| Støtte | DATAS: forbered dig på .NET 10-GC'en | 2 | Spike 3 | Gratis | https://devblogs.microsoft.com/dotnet/preparing-for-dotnet-10-gc/ |
| Støtte | Toub: Performance Improvements in .NET 10 | 4 | Måned 4-5, ikke før | Gratis | https://devblogs.microsoft.com/dotnet/performance-improvements-in-net-10/ |
| Støtte | API-versionering plus OpenAPI i .NET 10 | 3 | Spike 7 | Gratis | https://devblogs.microsoft.com/dotnet/api-versioning-in-dotnet-10-applications/ |
| Støtte | Validation i ASP.NET Core 10 (source generator) | 2 | Spike 7 | Gratis | https://learn.microsoft.com/en-us/aspnet/core/validation/overview?view=aspnetcore-10.0 |
| Støtte | PactNet — forstå det, indfør det ikke hos jer | 5 | Spike 7 | Gratis | https://github.com/pact-foundation/pact-net |
| Støtte | HybridCache (v10.9.0) | 4 | Spike 11 | Gratis | https://www.nuget.org/packages/Microsoft.Extensions.Caching.Hybrid |
| Støtte | Your Code as a Crime Scene, 2. udg. | 6 | Spike 12 | Bog | https://pragprog.com/titles/atcrime2/your-code-as-a-crime-scene-second-edition/ |
| Støtte | Pro .NET Memory Management, 2. udg. — opslagsværk | 8-10 | Spike 3, ikke mere | Bog | https://prodotnetmemory.com/ |
| Støtte | dotnet/eShop som **læseøvelse**, ikke template | 6 | Måned 3 | Gratis | https://github.com/dotnet/eShop |
| Senere | Fundamentals of Software Architecture, 2. udg. | 20 | Måned 7-9, ikke før | Bog | https://www.oreilly.com/library/view/fundamentals-of-software/9781098175504/ |
| Senere | Learning DDD (Khononov) — kun den strategiske halvdel | 8 | Måned 8+ | Bog | https://www.oreilly.com/library/view/learning-domain-driven-design/9781098100124/ |

Fravalgene er lige så meget en del af planen som valgene. De frigør ca. 145 timer, som er cirka to hele spikes.

| Fravalgt | Hvorfor | Timer sparet |
|---|---|---|
| Clean Code og Clean Architecture | Du skal kunne genkende og navngive mønstret på 20 minutter for at kunne argumentere imod det, ikke praktisere det | 20 |
| DDD, den blå bog (Evans) | Det brugbare får du fra Khononov på en brøkdel | 30 |
| C# in Depth 4. udg. | Stopper ved C# 7-8; vi er på C# 14 | 25 |
| Building Microservices | Læst nu får den dig til at foreslå microservices. Hurtigste vej til at miste troværdighed i et designmøde | 20 |
| System Design Interview-genren | Forkert spil. Et dansk SaaS-interview er "fortæl om en beslutning du traf, hvad den kostede" | 15-20 |
| Database Internals, Understanding Distributed Systems | Redundant med DDIA | 15 |
| CodeCrafters | Lærer systemprogrammering, ikke solution architecture. Gem det til måned 13+ | 0 i denne plan |
| Kubernetes-dybde | Kun hvis du faktisk møder det. Beslutningspunkt i måned 8 | 0 indtil videre |

Certificeringer optræder bevidst ikke i dette timebudget. De virker som deadline-motor og HR-filter, ikke som bevis for dybde — og bemærk at AZ-204 blev pensioneret 31. juli 2026, så ethvert råd der stadig anbefaler den, er forældet. Hvis du fanger dig selv i at læse eksamensmateriale i stedet for at køre en spike, er dybdesporet forladt.

## Spikes: fysisk output, ellers talte det ikke

Ingen spike er færdig uden fire ting: **en ADR, et diagram, mindst ét tal, og et retrospektiv**. Retrospektivets vigtigste afsnit hedder "hvad var jeg sikker på og tog fejl om". Uden det er en spike et weekendprojekt du har glemt om otte uger.

Regel mod scope creep: bruger en spike mere end 10 procent af sin tid på forretningslogik eller UI, er den designet forkert. Skær featuren ned, ikke målingen.

| Spike | Emne | Tid |
|---|---|---|
| 1 | Måleapparatet — trivielt endpoint, fuld instrumentering | 20-24 t |
| 2 | Seks async-fejlmønstre med observerbar signatur | 12 t |
| 3 | Allokering, GC og hvilke optimeringer der var overtro | 22 t |
| 4 | SQL uden ORM mod skævt fordelt leverandørskema | 24 t |
| 5 | EF Core-afsløringen: diff mod din håndskrevne SQL | 12 t |
| 6 | Isolationsniveauer og en race du fremkalder med vilje | 24 t |
| 7 | API-kontrakt, versionering, hvad der brækker en consumer | 22 t |
| 8 | Idempotens og outbox under fejlinjektion | 24 t |
| 9 | Multi-tenancy: tre modeller, samme feature, målte omkostninger | 26 t |
| 10 | Teststrategi som arkitekturbeslutning (ingen ny kode) | 12 t |
| 11 | Caching, invalidering og staleness som målt størrelse | 12 t |
| 12 | Kodebase-arkæologi på jeres eget repo | 20 t |
| Drift | Spike 1 forfremmet og driftet resten af året | 2 t/uge, ca. 90 t |

Fire af dem i detaljer, fordi de bærer mest.

**Spike 1 — måleapparatet.** Mindst mulige ASP.NET Core-service på .NET 10: ét endpoint, én SQL-forespørgsel mod SQL Server i en Testcontainer. Fuld instrumentering: OpenTelemetry traces plus metrics plus struktureret log med semantic conventions, `dotnet-counters` live, en load-generator, og et separat BenchmarkDotNet-projekt. Aspire 13.x som lokalt stillads, så du får OTel-dashboard gratis. **Kravet:** en baseline for p50/p95/p99 og allokeringer per request som du kan reproducere to gange inden for 5 procents afvigelse. Første gang afviger de mere, og fejlfindingen på selve *målingen* er hele læringen. Output: ADR-001 "sådan måler vi" med hvad hvert værktøj svarer på og hvad det ikke svarer på, telemetri-diagram, baselinetabel med to kørsler, og prædiktionsloggens første post. Byg den som noget der skal leve i 12 måneder — den bliver forfremmet.

**Spike 4 — SQL uden ORM.** Seed en SQL Server med et realistisk skema: 2 mio. dokumenter, 5.000 leverandører, 50 tenants, certifikater med udløbsdatoer, audit-log — og skæv fordeling, hvor én tenant har 40 procent af dataen. Skriv otte forespørgsler i hånden: filtreret paging, nyeste certifikat per leverandør, eksistenscheck, aggregat over datointerval, tekstsøgning, join over fire tabeller, en rapportforespørgsel, og en der rammer den skæve tenant. **Kravet:** prædiker plan, logical reads og varighed før hver kørsel. Indeksér derefter og mål igen. Ingen EF Core i denne spike overhovedet. Output: prædiktion-versus-faktisk-tabel før og efter indeksering — det er selve dybdetesten — ADR-004 om indeksstrategi inklusive de indekser du **fravalgte**, plan-screenshots, og `sp_BlitzIndex`-kritikken af dit eget skema med din kommentar. Den skæve tenant er ikke pynt: det er der parameter sniffing og statistik-skævhed bliver virkelige, og det er jeres virkelighed.

**Spike 6 — isolationsniveauer.** Kør Hermitage mod SQL Server i en Testcontainer og prædiker hvert resultat før kørsel. Byg derefter anomalien for alvor: et dokumentgodkendelsesflow hvor to samtidige godkendelser begge passerer en check-then-act-validering, så et krav om dobbelt godkendelse omgås. Reproducer den deterministisk, fix den på tre måder, og mål prisen.

| Fix | Forhindrer racen | Pris du skal måle |
|---|---|---|
| Unique constraint | Ja, hårdt | Throughput, plus fejlhåndtering på constraint-violation |
| Optimistic concurrency (rowversion) | Ja, med retry | Throughput, retry-rate under samtidighed |
| Eksplicit låsning eller serializable | Ja | Throughput, deadlock-rate, ventetid |

Kør hele øvelsen både med RCSI slået til (Azure SQL default) og fra (on-prem default), og forklar forskellen. Det er fælden de fleste .NET-udviklere aldrig lærer, og det er hele forklaringen bag et stort antal "det virker på min maskine"-fejl.

**Spike 9 — multi-tenancy.** Samme feature tre gange: leverandørdokument-listning med certifikatudløbsfilter, implementeret som (a) shared schema med tenant-diskriminator og EF global query filters, med og uden row-level security, (b) schema-per-tenant, (c) database-per-tenant. Mål for hver: performance med den skæve tenant fra spike 4, omkostning ved 50 / 500 / 5.000 tenants, blast radius ved en fejlbehæftet migration, og den faktiske indsats for at gendanne **én** tenants data uden at røre de andre. Leverancen er en skriftlig anbefaling der angiver det præcise tenant-antal og det præcise compliancekrav hvor anbefalingen vender. En anbefaling uden et vendepunkt er en holdning. Kør "gendan én tenant"-runbooken igennem i praksis og noter tidsforbruget — det tal kan meget få mennesker i Danmark oplyse fra egen erfaring.

Og drift-sporet, som ikke er valgfrit: spike 1 deployes til Azure og driftes resten af året. Over perioden kræves en defineret SLO med alarmering der faktisk fyrer, en pipeline med rollback du har brugt mindst én gang i vrede, mindst to skemaændringer kørt som expand-migrate-contract mod levende data, mindst to API-ændringer uden at brække den consumer du selv skrev, og mindst én rigtig hændelse med en skreven postmortem. Fristelsen til at forlade den i måned 4, når den er kedelig, er den enkeltbeslutning der oftest sænker denne slags planer.

## 12 måneders progression

| Måned | Spikes | Læsning | Timer/uge |
|---|---|---|---|
| 1 | 1, 2 | Supportpolitik, diagnostics-docs, Cleary, Programmer's Brain Del 1 | 12-14 |
| 2 | 3, start drift | Use The Index Luke, DATAS-posten, Kokosa målrettet | 12-14 |
| 3 | 4 | Use The Index Luke færdig, DDIA Storage and Retrieval, eShop som læseøvelse | 13-15 |
| 4 | 5, 6 | DDIA Transactions (to gange), Kendra Little, Toub-posten | 13-15 |
| 5 | 6 færdig, 7 | DDIA Encoding and Evolution, RFC 9457, versionerings-posten | 12-14 |
| 6 | 8 | DDIA Replication, idempotency-draftet | 13-15 |
| 7 | 9 | DDIA Sharding, Azure tenancy models, **Fundamentals 2e begynder** | 13-15 |
| 8 | 10, 11 | Fundamentals 2e, Khononov strategisk halvdel | 11-13 |
| 9 | 12, kompetenceport | Fundamentals 2e færdig, The Hard Parts udvalgte kapitler | 11-13 |
| 10-12 | Drift plus én valgfri spike drevet af det porten afslørede | The Hard Parts, DDIA data privacy og regulering | 8-10 |

Timeregnskabet: spikeserien er ca. 240 timer, drift-sporet ca. 90, læsningen ca. 120, ADR-skrivning og retroer ca. 40. I alt ca. 490 timer over 48 arbejdsuger er ca. 10,2 timer om ugen. Det ligger i den lave ende af dit loft, og det er med vilje: buffer til at en spike tager halvanden gang så lang tid som anslået, hvilket mindst tre af dem gør. Bruger du 14 timer hver uge fra måned 1, brænder du ud i måned 5. Fra måned 7 falder dybdesporets timeforbrug bevidst, fordi positioneringen skal have plads — og dybdesporet føles aldrig færdigt, så det skal skæres på kalenderen, ikke på fornemmelse.

## På jobbet: sådan konverterer dybden til autoritet uden mandat

Ni ansatte betyder at du ikke skal bede nogen om lov til noget af det her. Du skal bare gøre det.

- **Vedhæft et tal til hver eneste performance-nær ticket.** "p95 gik fra 340 ms til 95 ms, logical reads fra 41.000 til 1.200" i PR-beskrivelsen. Ændrer inden for en måned hvordan folk læser dine PR'er.
- **Log og læs den genererede SQL for hver EF-forespørgsel du rører.** Er den ikke-triviel, indsæt planen i PR'en. Det er den hurtigste vej til N+1-problemer ingen har opdaget, fordi ingen andre kigger.
- **Tag ejerskab over .NET 8/9 end-of-life-uret.** Begge udløber 10. november 2026. Skriv uopfordret et to-siders assessment: hvilke projekter, hvilke NuGet-pakker der blokerer, hvilke EF Core 10 breaking changes der rammer (særligt at `UseAzureSql` genererer en migration der ændrer alle eksisterende `nvarchar(max)`-JSON-kolonner til den native json-type), estimat og risikoordnet rækkefølge. Man beder ikke om lov til at skrive et dokument.
- **Skriv retroaktive ADR'er.** Hver gang du spørger en kollega "hvorfor er det bygget sådan?", skriv svaret som en énsides ADR og send den tilbage med "ret mig hvis jeg har misforstået". Efter ti af dem ejer du kodebasens beslutningshistorik.
- **Stil ét spørgsmål per PR-review:** "hvad sker der hvis det her kaldes to gange, eller samtidig, eller med en null tenant?" Ikke et forslag — et spørgsmål. Spørgsmål koster ingen politisk kapital.
- **Tag de kedelige tværgående tickets ingen vil have:** støjende logging, den flaky test, langsom CI, dependency-opgraderinger. Det er arkitekturarbejde forklædt som pligtarbejde, og det giver dig legitim anledning til at røre hvert eneste modul. I et mikrofirma er det din genvej til en bredde en junior i en 500-mands virksomhed aldrig får.
- **Reproducer enhver concurrency-fejl fra produktion i en test før du fixer den.** Det er den enkeltvane der klarest signalerer forståelse frem for gætværk, og den efterlader et artefakt.

Ét forbehold der gælder specifikt jer: hvis kodebasen bruger MassTransit, er det en åben opgave. Version 9 gik kommercielt og kræver runtime license key (100 procents rabat for organisationer under 1 mio. USD omsætning), og v8 når end-of-life ved udgangen af 2026. Alternativer med MIT-licens er Wolverine og Rebus. Et kort notat om det er arkitektarbejde du kan levere i denne måned.

## Faldgruber

1. **At læse arkitekturbøger før du kan bygge og drifte én service.** Symptomerne er synlige for alle andre end dig selv: ordforrådet vokser hurtigere end målingerne, du foreslår at splitte noget op før du har profileret det, du bruger "eventual consistency" korrekt men kan ikke svare på "hvad er p99 i dag". Den person afsløres i løbet af ét sprint.
2. **At bygge et produkt i stedet for spikes.** Hver time på en formular er en time ikke brugt på en query-plan.
3. **At måle én gang og kalde det et benchmark.** Ikke-reproducerbare tal er værre end ingen tal, fordi de skaber falsk selvtillid du tager med ind i et designmøde.
4. **At lære EF Core før SQL.** Producerer udviklere der ikke kan diagnosticere deres eget ORM.
5. **Clean Architecture-cargo cult.** Seks projekter og et interface per klasse for ét deployment. Ser ud som arkitektur for juniorer og som uerfarenhed for seniorer. Det stærkeste en junior kan gøre i et designmøde er at argumentere for den **simplere** løsning med et tal bag.
6. **At læse DDIA lineært fra ende til anden.** Det er en referencebog. Læs kapitlet der matcher den spike du kører, i den uge du kører den.
7. **At bygge tolv spikes og aldrig drifte noget.** De dyreste arkitekturfejl er driftsfejl: manglende backpressure, ikke-idempotente retries, migrationer uden rollback, cache uden invalidering, retry-storme. De bliver først virkelige når du selv er blevet vækket af dem.
8. **At droppe retrospektivet.** Uden det komprimeres læringen ikke til noget der kan genkaldes koldt ni måneder senere.
9. **At antage at lokal adfærd er lig produktionsadfærd.** RCSI-forskellen mellem Azure SQL og on-prem er det konkrete eksempel du vil møde.
10. **At lade dybdesporet æde måned 7-12.** Der er altid en spike mere. Positioneringen starter på kalenderen, ikke på følelsen af at være klar.
11. **At tro dybde kan bevises i en samtale.** Forløber en samtale om din tekniske dybde uden at du har nævnt et konkret tal fra noget du selv har målt, gik den ikke godt — uanset hvordan den føltes.
12. **At undervurdere hvor meget af rollen der er skrift.** ADR'en er ikke magisk; evnen til at skrive en beslutning ned så en fremmed kan anvende den uden dig er selve jobbet.

## Sådan ved du at du kan det: kompetenceporten i måned 9-10

Dette er kriterierne du ikke kan snyde dig igennem, fordi de kræver artefakter med datoer eller andre menneskers adfærd. Ja til mindst 11 af 14. Er der færre, er svaret at dybdesporet fortsætter, ikke at porten var for hård.

| # | Kriterium | Beviset |
|---|---|---|
| 1 | Prædiktionsloggens fejlmargin er faldet målbart over seks måneder | Loggen, ikke fornemmelsen |
| 2 | Du kan udpege den dyreste operator i en execution plan og forklare hvorfor, uden værktøjshjælp | Demonstreres koldt |
| 3 | Du kan sige hvilken SQL en ukendt EF-forespørgsel genererer, før den køres, og rammer oftere rigtigt end forkert | PR-historik hvor du gjorde det og blev bekræftet |
| 4 | Du kan reproducere en concurrency-anomali deterministisk på under 30 minutter uden noter | Repoet plus en live demonstration |
| 5 | Du har en service du selv har deployet, som har kørt i mindst tre måneder og haft mindst én rigtig hændelse | Oppetidsrapport, trace, root cause, fix |
| 6 | Du har ændret den services API-kontrakt og skema mindst to gange hver uden at brække consumeren | Migrationslogs plus den CI-check der ville have fanget en fejl |
| 7 | Der ligger mindst otte komplette spike-artefaktsæt, og du kan gennemgå et vilkårligt af dem koldt | Repoet plus en gennemgang uden forberedelse |
| 8 | Du kan levere dataflow, tre fejlmønstre og én sundhedsmetrik for et ukendt modul på under 45 minutter | Testes med en tilfældig del af kodebasen |
| 9 | Du har mindst én gang argumenteret imod den mere sofistikerede løsning med et tal du selv havde målt | Mødet, og hvad der blev besluttet |
| 10 | Mindst fem ADR'er er blevet refereret til, rettet i eller bygget videre på af andre | Andres engagement, ikke antallet af dokumenter |
| 11 | Dine PR-beskrivelser indeholder rutinemæssigt tal og fejlmønstre, og kolleger er begyndt at efterligne formatet | Andres PR'er |
| 12 | En kollega har spurgt **dig** om noget i kodebasen, og du svarede ud fra dokumentation du selv har produceret | Kan dateres |
| 13 | Du kan navngive tre ting du var sikker på og tog fejl om, og præcis hvad målingen viste | Retroerne |
| 14 | Dit uopfordrede arkitekturnotat er blevet læst af nogen med beslutningskompetence og har ført til en konkret handling — eller en konkret beslutning om ikke at handle | Effekt, ikke levering |

Kriterium 3, 9, 10, 11 og 12 kan du ikke opfylde alene. Det er tilsigtet: de er de eneste i tabellen der kræver at andre mennesker reagerer på dit arbejde, og de er derfor de eneste der beviser at dybden er blevet synlig. Fordi der ikke sidder en arkitekt hos LeanLinking der kan give dig kvalificeret modspil på et designvalg, skal mindst tre af dine spike-artefaktsæt desuden have været igennem en ekstern læser inden porten — en mentor, et code review-bytte, eller offentliggørelse et sted hvor kritik faktisk kommer. Ellers risikerer du at have målt flittigt i ni måneder på en forkert mental model, og porten vil ikke fange det, fordi du selv har designet den.
