# Supplerende ressourcer: huller i karriereplanen

> Denne guide dækker emner der er tynde eller mangler i de 12 moduler. Den er researched september 2026 og skal revalideres halvårligt — URL'er rådner, versioner ændres, og bøger udkommer.
> Prioriteter: **Kritisk** = blokerer karrieremålet hvis det springes over. **Vigtig** = mærkbar forskel i troværdighed. **Støtte** = nyttigt men ikke afgørende. **Valgfri** = kun hvis tiden er der.

---

## 1. DevOps & CI/CD

Karriereplanen dækker deployment og observability, men CI/CD-pipeline-design, IaC-strategi og driftskulturteori er tynde. En Solution Architect i et ni-personers firma ejer hele leverancekæden — det er ikke et specialistområde, det er dagligt arbejde.

### 1.1 GitHub Actions for .NET monorepos

| | |
|---|---|
| **Prioritet** | Vigtig |
| **Ressource** | GitHub Community Discussion #25661 + Graphite guide + WarpBuild blog |
| **URL'er** | https://github.com/orgs/community/discussions/25661 · https://graphite.com/guides/monorepo-with-github-actions · https://www.warpbuild.com/blog/github-actions-monorepo-guide |
| **Pris** | Gratis |
| **Tidsforbrug** | 3-4 timer samlet læsning; 4-6 timer at implementere i jeres repo |
| **Hvorfor** | Med én repo og tre-fem udviklere er path-filtrering og reusable workflows den hurtigste forbedring af feedback-loop. Uden det bygger I alt ved hvert push |
| **Spring over** | Nx/Turborepo-specifikke guides (det er JavaScript-tooling). Self-hosted runners medmindre GitHub-hosted minutterne faktisk er en flaskehals. Matrix builds med 20+ kombinationer — I har én platform |

**Kerneprincipper at implementere:**

1. **Path-baserede triggers** — `paths:` filtre i workflow YAML så kun ændrede projekter bygger
2. **Reusable workflows** — ét fælles build/test/deploy workflow kaldt med `workflow_call`
3. **NuGet-cache** — `actions/cache` på `~/.nuget/packages` sparer 30-60 sekunder per build
4. **Environment-baseret deployment** — GitHub Environments med required reviewers til produktion

### 1.2 Bicep vs. Terraform for små Azure-hold

| | |
|---|---|
| **Prioritet** | Vigtig |
| **Ressource** | Microsoft Learn: "Comparing Terraform and Bicep" + Spacelift sammenligning |
| **URL'er** | https://learn.microsoft.com/en-us/azure/developer/terraform/comparing-terraform-and-bicep · https://spacelift.io/blog/bicep-vs-terraform |
| **Pris** | Gratis |
| **Tidsforbrug** | 2 timer læsning; beslutningen tager 30 min |
| **Hvorfor** | Karriereplanen anbefaler Bicep og fraråder to IaC-sprog på 12 måneder. Denne ressource giver dig argumenterne til at forsvare det valg — og vide hvornår Terraform alligevel er svaret |
| **Spring over** | Multi-cloud scenarier (I er Azure-only). Terraform Cloud/Enterprise pricing (irrelevant ved ni ansatte) |

**Anbefaling for jeres kontekst:** Bicep. Ingen state-fil at vedligeholde, ingen provider-versioner at koordinere, og Azure Verified Modules (AVM) er modnet betydeligt i 2025-2026. Terraform er kun relevant hvis I begynder at bruge AWS eller GCP, hvilket ikke er på roadmap.

### 1.3 Team Topologies — nøglebegreber

| | |
|---|---|
| **Prioritet** | Støtte |
| **Ressource** | *Team Topologies* — Matthew Skelton & Manuel Pais (IT Revolution, 2019) |
| **URL** | https://teamtopologies.com/key-concepts |
| **Pris** | Bog: ca. 250 DKK. Key concepts-siden er gratis |
| **Tidsforbrug** | 1 time på key concepts-siden; 4-5 timer på bogen |
| **Hvorfor** | Karriereplanen nævner korrekt at Team Topologies "kræver flere end tre teams". Men ordforrådet (stream-aligned, platform team, cognitive load, interaction modes) dukker op i jobsamtaler og i *Fundamentals of Software Architecture* 2. udg., som planen anbefaler. Kend begreberne, implementér dem ikke |
| **Spring over** | Alt om skalering til 10+ teams. Interaction mode-ceremonier. Faciliteringsroller. Læs kun kapitel 1-4 og appendix A |

**De fire teamtyper:** Stream-aligned (leverer forretningsværdi), Platform (reducerer kognitiv last for stream-aligned), Enabling (hjælper teams med nye kompetencer), Complicated-subsystem (isolerer specialviden). **Tre interaktionsmønstre:** Collaboration, X-as-a-Service, Facilitating.

### 1.4 DORA-metrikker og Accelerate-forskningen — nuværende status

| | |
|---|---|
| **Prioritet** | Vigtig |
| **Ressource** | DORA 2024-rapport + DORA 2025 State of AI-Assisted Software Development |
| **URL'er** | https://dora.dev/research/2024/dora-report/ · https://cloud.google.com/resources/content/2025-dora-ai-assisted-software-development-report |
| **Pris** | Gratis |
| **Tidsforbrug** | 3-4 timer på begge rapporter |
| **Hvorfor** | DORA er lingua franca i arkitektsamtaler om leveranceperformance. Men landskabet har ændret sig: 2025-rapporten pensionerede fire-tier-rankeringen til fordel for syv teamprofiler, og AI-adoption komplicerer metrikkerne fundamentalt. Du skal kende den aktuelle status, ikke 2023-versionen |
| **Spring over** | Enterprisecases og "transformation"-afsnit. Fokusér på de fire kernemetrikker (Deployment Frequency, Lead Time for Changes, Change Failure Rate, Mean Time to Recovery), de syv teamprofiler, og AI-implikationerne |

**Kritisk nuance 2025-2026:** AI-adoption øger individuel produktivitet men korrelerer med *højere* instabilitet — Change Failure Rate og Deployment Rework Rate forværres. Uden stærk automatiseret test og hurtige feedback-loops forstærker AI eksisterende svagheder. Den pointe er guld i en arkitektsamtale.

### 1.5 Google SRE — gratis bøger online

| | |
|---|---|
| **Prioritet** | Støtte |
| **Ressource** | *Site Reliability Engineering* (2016) + *The Site Reliability Workbook* (2018) |
| **URL'er** | https://sre.google/sre-book/table-of-contents/ · https://sre.google/workbook/table-of-contents/ |
| **Pris** | Gratis — fulde bøger online |
| **Tidsforbrug** | 8-12 timer selektivt; bøgerne er 500+ sider tilsammen |
| **Hvorfor** | SRE-begreberne (error budgets, SLO/SLI/SLA, toil) bruges dagligt i Azure-verdenen og dukker op i AZ-305. Workbook'en er mere praktisk end hovedbogen |
| **Spring over** | Alt der forudsætter Google-skala: Borg, global load balancing, Chubby. Kapitel 27-34 i hovedbogen (meget Google-intern). Fokusér på kap. 1-4 (principper), kap. 6 (monitoring), kap. 17-18 (testing), kap. 19 (load balancing-koncepter), og hele del II af Workbook'en |

**Mest relevante kapitler for jeres kontekst:**

- Kap. 4: Service Level Objectives — oversæt direkte til jeres SaaS-kontrakter
- Kap. 6: Monitoring Distributed Systems — grundlag for observability-modulet
- Workbook kap. 2: Implementing SLOs — praktisk guide til at sætte tal på

---

## 2. Business/arkitektur-krydsfeltet

Karriereplanen dækker arkitektur og den dækker forretning, men krydsfeltet — hvordan arkitekturbeslutninger oversættes til forretningsstrategi og prissætning — mangler næsten helt. Det er præcis der en Solution Architect adskiller sig fra en senior udvikler.

### 2.1 Technology Strategy Patterns

| | |
|---|---|
| **Prioritet** | Vigtig |
| **Ressource** | *Technology Strategy Patterns: Architecture as Strategy* — Eben Hewitt |
| **Forlag** | O'Reilly Media, 2018 |
| **ISBN** | 978-1-492-04087-3 |
| **Pris** | Ca. 350 DKK (e-bog), inkluderet i O'Reilly-abonnement |
| **Tidsforbrug** | 6-8 timer |
| **Hvorfor** | 39 mønstre til at formulere og kommunikere teknologistrategi i en form ledelsen forstår. Bogen er skrevet af en CTO/CIO og er den eneste bogstavelige "arkitektur møder strategi"-bog der ikke er McKinsey-jargon. Direkte relevant for at give stifteren arkitekturbeslutninger i et format han kan handle på |
| **Spring over** | Del IV (Communicating) kan skimmes — mest relevant for store organisationer. Fokusér på del I-II: mønstrene Context, Direction og Challenge |

### 2.2 Inspired — produktledelse

| | |
|---|---|
| **Prioritet** | Støtte |
| **Ressource** | *Inspired: How to Create Tech Products Customers Love* — Marty Cagan, 2. udgave |
| **Forlag** | Wiley, 2018 |
| **ISBN** | 978-1-119-38750-3 |
| **Pris** | Ca. 250 DKK |
| **Tidsforbrug** | 5-6 timer |
| **Hvorfor** | Karriereplanen nævner korrekt at Cagan "forudsætter en organisation med flere etager". Men kapitel 1-15 om discovery, produktteamets roller og teknologiens rolle i produktbeslutninger er direkte relevant. Cagans definition af "empowered teams" er det modsatte af jeres virkelighed — men at kunne artikulere forskellen er værdifuldt i en samtale |
| **Spring over** | Del III og IV om skalering af produktorganisationer. Product trio-konceptet (I er ikke et product trio). OKR-afsnittene |

**Bemærk:** Der er ikke udkommet en 3. udgave. Cagans nyere bøger *Empowered* (2020) og *Transformed* (2024) handler om organisationstransformation og er irrelevante for jeres kontekst.

### 2.3 Monetizing Innovation

| | |
|---|---|
| **Prioritet** | Støtte |
| **Ressource** | *Monetizing Innovation: How Smart Companies Design the Product Around the Price* — Madhavan Ramanujam & Georg Tacke |
| **Forlag** | Wiley, 2016 |
| **ISBN** | 978-1-119-24086-0 |
| **Pris** | Ca. 220 DKK |
| **Tidsforbrug** | 4-5 timer |
| **Hvorfor** | Bogen argumenterer for at prissætte *før* man bygger — "design the product around the price". For et compliance-SaaS med regulatorisk drevne køb er det operativt: kunderne køber ikke funktioner, de køber risikoreduktion, og prismodellen skal afspejle det. Direkte relevant for roadmap-modulet (modul 10) |
| **Spring over** | Case studies fra consumer tech (kapitel 8-9). Fokusér på kapitel 1-5 (de ni fejltyper i monetarisering) og kapitel 10-11 (pricing architecture) |

### 2.4 Azure Pricing Calculator — best practices for arkitekter

| | |
|---|---|
| **Prioritet** | Kritisk |
| **Ressource** | Azure Pricing Calculator + Azure Retail Prices REST API |
| **URL'er** | https://azure.microsoft.com/en-us/pricing/calculator/ · https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices |
| **Pris** | Gratis |
| **Tidsforbrug** | 4-6 timer initial, derefter løbende |
| **Hvorfor** | Allerede i karriereplanen (modul 3), men underbetonet. Calculatoren er et *estimat* der udelader forhandlede rabatter, variabelt forbrug og skjulte omkostninger (egress, logging, monitoring — 30-40% af reel spend). Brug altid 30 dages faktisk forbrug før Reserved Instances. Parér med TCO Calculator til migrationsargumenter og Cost Management til live spend |
| **Spring over** | EA- og Partner Center-scenarier (irrelevante ved jeres størrelse) |

**Praktisk regel:** Calculatorens tal er et *gulv*. Læg 20-30% oveni for den virkelige verden. Og brug Retail Prices API'et programmatisk — det er uautentificeret og kan automatiseres.

### 2.5 B2B SaaS-prissætning og arkitektur

| | |
|---|---|
| **Prioritet** | Støtte |
| **Ressource** | CloudZero SaaS Pricing Guide (2026) + CRV SaaS Pricing Models |
| **URL'er** | https://www.cloudzero.com/blog/saas-pricing/ · https://www.crv.com/content/saas-pricing-models |
| **Pris** | Gratis |
| **Tidsforbrug** | 2-3 timer |
| **Hvorfor** | I 2026 er ren per-seat-prissætning på vej ud; hybrid- og forbrugsbaserede modeller dominerer. For jeres compliance-SaaS er spørgsmålet: prissætter I per bruger, per leverandør, per certifikatvolumen, eller per complianceramme? Svaret er en arkitekturbeslutning fordi det bestemmer multi-tenancy-model, metering-pipeline og faktureringsintegration |
| **Spring over** | Consumer SaaS og freemium-modeller. PLG-strategier (product-led growth) — irrelevante for B2B compliance |

---

## 3. Projektledelse for arkitekter

Karriereplanen dækker estimering og forecasting (modul 10), men projektledelsesrammer og risikoprioritering er tynde.

### 3.1 Shape Up — Basecamp

| | |
|---|---|
| **Prioritet** | Kritisk |
| **Ressource** | *Shape Up: Stop Running in Circles and Ship Work that Matters* — Ryan Singer |
| **URL** | https://basecamp.com/shapeup (fuld bog, gratis online) |
| **PDF** | https://basecamp.com/shapeup/shape-up.pdf |
| **Pris** | Gratis |
| **Tidsforbrug** | 3-4 timer (del 1-2) |
| **Hvorfor** | Allerede anbefalet i modul 10 med korrekt URL. Gentaget her fordi det er den vigtigste enkeltressource i hele sektionen. "Fixed appetite, variable scope" er den eneste prioriteringsmodel der giver mening med tre-fem udviklere. Læs del 1 (Shaping) og del 2 (Betting) |
| **Spring over** | Betting table (forudsætter flere teams). Seks-ugers-cyklusser (dogmatisk tidsramme). Hill charts (nice-to-have, ikke kritisk) |

### 3.2 Evidence-Based Management Guide — Scrum.org

| | |
|---|---|
| **Prioritet** | Vigtig |
| **Ressource** | *Evidence-Based Management Guide* — Ken Schwaber / Scrum.org, opdateret maj 2024 |
| **URL** | https://www.scrum.org/resources/evidence-based-management-guide |
| **Online interaktiv version** | https://www.scrum.org/resources/online-evidence-based-management-guide |
| **Pris** | Gratis |
| **Tidsforbrug** | 1 time læsning + 1 time på egne mål |
| **Hvorfor** | Allerede anbefalet i modul 10. Fire Key Value Areas (Current Value, Unrealized Value, Ability to Innovate, Time to Market) er en ramme du kan bruge til at sætte tal på jeres produktudvikling uden at indføre Scrum-ceremoni. PAL-EBM-kurset (~975 USD) er unødvendigt |
| **Spring over** | Organisationsafsnittene (skrevet til 50+ personers organisationer). Assessment-delen |

### 3.3 Monte Carlo-forecasting for små teams

| | |
|---|---|
| **Prioritet** | Vigtig |
| **Ressource** | ActionableAgile Analytics + Scrum.org-artikel om Monte Carlo |
| **URL'er** | https://www.scrum.org/resources/blog/monte-carlo-forecasting-scrum · https://www.55degrees.se/blog/post/agile-forecasting-monte-carlo-simulations-and-flow-metrics |
| **Pris** | ActionableAgile: fra ~15 USD/md for små teams. Scrum.org-artiklen er gratis |
| **Tidsforbrug** | 2-3 timer på metoden; 4-6 timer på at bygge jeres egen i Excel/Python |
| **Hvorfor** | Modulet 10 beskriver Monte Carlo-metoden (trin 4 i forecasting-tabellen). Denne ressource giver implementeringsdetaljer. Kræver 12-24 måneders throughput-data — som I allerede har i jeres issue tracker |
| **Spring over** | Enterprise-skalerings-features. SAFe-integration. Brug simpel throughput-baseret simulation, ikke velocity-baseret |

**Praktisk tilgang uden betalt værktøj:** Træk cycle time-data fra Azure DevOps/Jira. 10.000 Monte Carlo-simulationer i et Python-script på 30 linjer. Udtryk som percentiler: "85% sandsynlighed for levering inden dato X".

### 3.4 Risiko-baseret prioritering

| | |
|---|---|
| **Prioritet** | Støtte |
| **Ressource** | Risk Prioritization Matrix (Six Sigma) + Triskell guide |
| **URL'er** | https://www.6sigma.us/six-sigma-in-focus/risk-prioritization-matrix/ · https://triskellsoftware.com/blog/project-prioritization/ |
| **Pris** | Gratis |
| **Tidsforbrug** | 2 timer |
| **Hvorfor** | Compliance-domænet har iboende risici der skal prioriteres systematisk. En impact/probability-matrice med fire kvadranter er simpel nok til ni ansatte og seriøs nok til en audit |
| **Spring over** | Kybernetisk risiko-rammeværk (NIST CSF, ISO 27005) — det er specialistområder. CVSS-scoring (medmindre I bygger sikkerhedsfeatures). Fokusér på forretnings- og projektrisiko, ikke teknisk sårbarhedsanalyse |

---

## 4. Arkitekturfællesskab og læring

Karriereplanen er stærk på individuel læring men tynd på fællesskab og sparring — en reel risiko når man er den eneste arkitektaspirant i firmaet.

### 4.1 O'Reilly Architecture Katas

| | |
|---|---|
| **Prioritet** | Vigtig |
| **Ressource** | O'Reilly Architectural Katas (løbende events, modereret af Sam Newman) |
| **URL** | https://www.oreilly.com/live-events/architectural-katas/0636920054100/ |
| **Pris** | Kræver O'Reilly-abonnement (~449 USD/år) + team på 3-5 personer |
| **Tidsforbrug** | 6-8 uger per kata (deltid) |
| **Hvorfor** | Den bedste simulering af arkitektarbejde der findes uden en faktisk arkitektstilling. Du får et realistisk problem, laver et design, præsenterer det, og får feedback fra dommere. 2025-kataerne fokuserede på AI-enabled architecture. 100 første tilmeldte teams vælges |
| **Spring over** | Hvis du ikke kan samle et team. Solo-deltagelse er ikke muligt. Alternativ: løs de offentligt tilgængelige kata-problemer fra nealford.com selv og bed om review i et arkitekturforum |

**Status 2026:** Kataerne kører kvartalsvis. Q4 2025 var modereret af Sam Newman med finaler 13. november 2025. Hold øje med 2026-annoncering på O'Reilly Live Events-siden.

### 4.2 Podcasts

| Podcast | URL | Frekvens | Tidsforbrug | Prioritet |
|---|---|---|---|---|
| **Software Engineering Radio** | https://se-radio.net/ | Ugentlig | 45-60 min/episode | Vigtig |
| **Software Architecture Bookclub** (Mark Richards & Neal Ford) | https://developertoarchitect.com/bookclub-podcast.html | Månedlig | 30-45 min/episode | Vigtig |
| **InfoQ Podcast** | https://www.infoq.com/podcasts/ | 2x/md | 45-60 min/episode | Støtte |
| **.NET Rocks!** | https://www.dotnetrocks.com/ | Ugentlig | 60 min/episode | Støtte |

**Anbefaling:** SE Radio er den vigtigste — 738+ episoder, 20 års arkiv, og dækker arkitektur, distributed systems, sikkerhed og deployment. Bookclub-podcasten er særlig relevant fordi den gennemgår *Fundamentals of Software Architecture* 2. udg. kapitel for kapitel (episode 13-25).

**Spring over:** Latent Space (AI-fokuseret, ikke arkitektur). Semaphore Uncut (for generel).

### 4.3 Architecture Decision Records — skabeloner og værktøjer

| | |
|---|---|
| **Prioritet** | Kritisk |
| **Ressource** | adr.github.io + MADR-skabelonen |
| **URL'er** | https://adr.github.io/ · https://adr.github.io/madr/ |
| **Pris** | Gratis |
| **Tidsforbrug** | 1 time at vælge skabelon; derefter 20-45 min per ADR |
| **Hvorfor** | Karriereplanen nævner ADR'er i modul 1 og 10 men giver ingen skabelon. ThoughtWorks Tech Radar har haft lightweight ADR'er i Adopt-ringen siden 2018 og stadig i april 2025 (Volume 31). Start med Nygards originale firesektions-skabelon (Title, Status, Context, Decision, Consequences). Skift til MADR kun hvis teamet har brug for eksplicitte decision drivers og overvejede alternativer |
| **Spring over** | Log4brains og andre tunge ADR-management-værktøjer medmindre loggen skal læses af ikke-udviklere. `adr-tools` CLI er fint til at komme i gang |

**Bedste praksis:**

- Nygard-skabelonen (fire sektioner) er nok for 90% af teams
- MADR tilføjer decision drivers og considered options — brug den hvis I har brug for at dokumentere *hvorfor* alternativer blev fravalgt
- Gem ADR'er i repo'en, ikke i Confluence. De skal versioneres med koden
- Én ADR per beslutning, ikke én per møde

### 4.4 Danske IT-arkitekturfællesskaber og events 2026

| Event | Dato | Sted | Pris | Prioritet |
|---|---|---|---|---|
| **Arkitekturdagen 2026** (Dansk IT) | 17. juni 2026 | Center for Ledelse, København | Medlemspris ~2.500-3.500 DKK (estimat) | Vigtig |
| **NDC Copenhagen 2026** | 1.-4. juni 2026 | Øksnehallen, København | 3-dages konference ~6.000-9.000 DKK | Støtte |
| **IT-arkitektur i praksis** (Dansk IT netværksgruppe) | 5. feb, 21. maj, 15. sep, 24. nov 2026 | Drejervej 15, 2400 KBH NV | Dansk IT-medlemskab | Vigtig |
| **FDA-konference** (Fællesoffentlig Digital Arkitektur) | 25. november 2026 | TBA | Gratis (forventet) | Støtte |
| **Copenhagen Composable Conference** | 30. oktober 2026 | København | TBA | Valgfri |

**Anbefaling:** Prioritér Dansk ITs netværksgruppe "IT-arkitektur i praksis" — fire møder om året, lavt engagement (du dukker bare op), og du møder folk der faktisk arbejder med IT-arkitektur i Danmark. Arkitekturdagen er det årlige samlingspunkt. NDC er dyrt men har stærke arkitektur-tracks — overvej det kun hvis firmaet betaler.

**URL'er:**
- Arkitekturdagen: https://dit.dk/arkitekturdagen/
- IT-arkitektur i praksis: https://dit.dk/Netvaerksgrupper/It-arkitektur-praksis
- NDC Copenhagen: https://ndccopenhagen.com/
- FDA: https://arkitektur.digst.dk/

---

## 5. .NET-økosystemet — versionsstatus september 2026

Karriereplanen bygger på .NET 10 og nævner specifikke datoer. Her er verifikation og korrektioner.

### 5.1 .NET-versioner og supportstatus

| Version | Type | Udgivet | End of Support | Status sept. 2026 |
|---|---|---|---|---|
| **.NET 8** | LTS | 14. nov. 2023 | **10. nov. 2026** | **Aktiv — udløber om 2 måneder.** Karriereplanen siger "10. november 2026" — det er korrekt |
| **.NET 9** | STS (18 md.) | 12. nov. 2024 | **12. maj 2026** | **Udløbet.** STS-support er 18 måneder. .NET 9 nåede EOL fire måneder før denne dato |
| **.NET 10** | LTS | **11. nov. 2025** | **10. nov. 2028** | **Aktiv — anbefalet.** Karriereplanen siger "support til 14. november 2028" — den præcise dato er **10. november 2028** ifølge Microsofts officielle supportpolitik. Forskellen er ubetydelig men bør rettes |

**Kilde:** https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core

**Kritisk handling:** .NET 8 (LTS) udløber 10. november 2026. .NET 9 (STS) nåede allerede EOL 12. maj 2026. Hvis I stadig kører produktion på .NET 8, er migrering til .NET 10 en tidskritisk opgave. Start nu, ikke i oktober.

**Karriereplanens påstand vs. virkelighed:**
- ".NET 8 udløber 10. november 2026" — **Korrekt**
- ".NET 9 nåede EOL 12. maj 2026" — **Rettet** (STS = 18 måneder, ikke 24)
- ".NET 10 support til 10. november 2028" — **Korrekt** (rettet fra 14. nov.)
- "Jag ikke .NET 11; den er STS" — **Korrekt råd** (forudsat .NET 11 udkommer november 2026 som STS med 18 måneders support)

### 5.2 .NET Aspire

| | |
|---|---|
| **Nuværende version** | **Aspire 13.5.3** (25. august 2026) |
| **Udgivet med .NET 10** | Aspire 13.0 (11. november 2025) |
| **URL** | https://aspire.dev/ |
| **Support policy** | https://dotnet.microsoft.com/en-us/platform/support/policy/aspire |
| **Prioritet** | Støtte — relevant for lokal udvikling og service discovery, ikke for produktion endnu |

**Nøglefunktioner i 13.5:** AppHost-interaktivitet, TypeScript GA-support, terminal sessions. Aspire er primært et udviklingsværktøj (service discovery, dashboard, health checks i dev) — det erstatter ikke container-orchestration i produktion.

### 5.3 BenchmarkDotNet

| | |
|---|---|
| **Nuværende version** | **0.15.8** (NuGet) |
| **URL** | https://benchmarkdotnet.org/ · https://www.nuget.org/packages/BenchmarkDotNet |
| **Nyt i 0.15.x** | .NET 10-support, WakeLock (forhindrer system-sleep under benchmarks), Roslyn analyzers til compile-time fejlfinding, forbedret MemoryDiagnoser |
| **Prioritet** | Kritisk — allerede i karriereplanen (modul 2), men versionsinformation mangler |

### 5.4 EF Core 10

| | |
|---|---|
| **Status** | **Stabil release** — 10.0.0 udgivet 11. november 2025 |
| **URL** | https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew |
| **Næste version** | EF Core 11 forventes november 2026 |
| **Prioritet** | Vigtig — brug EF Core 10 i nye projekter |

**Nøglefunktioner i EF Core 10:**

- `LeftJoin` / `RightJoin` LINQ-operatorer (endelig!)
- Vector data type support til Azure SQL og SQL Server 2025
- Forbedret Cosmos DB-support
- Nemmere bulk updates
- Kun mindre breaking changes fra EF Core 9

---

## 6. Bogverifikation

Karriereplanen refererer til specifikke udgaver. Her er faktuel verifikation.

### 6.1 Designing Data-Intensive Applications, 2. udgave

| | |
|---|---|
| **Eksisterer?** | **Ja** |
| **Titel** | *Designing Data-Intensive Applications*, 2nd Edition |
| **Forfattere** | Martin Kleppmann & **Chris Riccomini** (ny medforfatter) |
| **Forlag** | O'Reilly Media |
| **Udgivelse** | **Marts 2026** |
| **ISBN** | 978-1-098-11905-8 |
| **Sider** | ~650 |
| **Pris** | Ca. 450 DKK (paperback), inkluderet i O'Reilly-abonnement |
| **URL** | https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ |
| **Hvad er nyt** | Cloud-native arkitekturer som default, object storage som first-class building block, AI-drevne workloads (storage formats, query engines, indexing), embedded/edge deployments |
| **Karriereplanens reference** | Planen nævner DDIA men specificerer ikke udgave. **Anbefaling: brug 2. udgave.** 1. udgave (2017) mangler cloud-native og AI-perspektiver |

### 6.2 Fundamentals of Software Architecture, 2. udgave

| | |
|---|---|
| **Eksisterer?** | **Ja** |
| **Titel** | *Fundamentals of Software Architecture: A Modern Engineering Approach*, 2nd Edition |
| **Forfattere** | Mark Richards & Neal Ford |
| **Forlag** | O'Reilly Media |
| **Udgivelse** | **Marts 2025** |
| **ISBN** | 978-1-098-17551-1 |
| **Pris** | Ca. 400 DKK (paperback), inkluderet i O'Reilly-abonnement |
| **URL** | https://www.oreilly.com/library/view/fundamentals-of-software/9781098175504/ |
| **Hvad er nyt** | Fem nye kapitler, herunder generativ AI, team topologies, data i arkitektur |
| **Karriereplanens reference** | Planen nævner "2. udg. (2025)" — **Korrekt** |

### 6.3 The C4 Model (Simon Brown, O'Reilly)

| | |
|---|---|
| **Eksisterer?** | **Ja — men udgivelsesdatoen afviger fra planens påstand** |
| **Titel** | *The C4 Model: Visualizing Software Architecture* |
| **Forfatter** | Simon Brown |
| **Forlag** | O'Reilly Media |
| **Udgivelse** | **Juli-september 2026** (kilder varierer; Amazon angiver september 2026) |
| **ISBN** | 979-8-341-66012-0 |
| **Sider** | ~150-177 |
| **Pris** | Ca. 400 DKK ($56,99) |
| **URL** | https://www.oreilly.com/library/view/the-c4-model/9798341660113/ |
| **Karriereplanens reference** | Hvis planen nævner "O'Reilly 2026" — **Korrekt.** Bemærk at bogen erstatter den tidligere Leanpub-udgave (*Visualising Software Architecture*, nu pensioneret) |

### 6.4 Your Code as a Crime Scene, 2. udgave

| | |
|---|---|
| **Eksisterer?** | **Ja** |
| **Titel** | *Your Code as a Crime Scene, Second Edition: Use Forensic Techniques to Arrest Defects, Bottlenecks, and Bad Design in Your Programs* |
| **Forfatter** | Adam Tornhill |
| **Forlag** | The Pragmatic Programmers |
| **Udgivelse** | **April 2024** |
| **ISBN** | 979-8-888-65032-5 |
| **Pris** | Ca. 350 DKK |
| **URL** | https://pragprog.com/titles/atcrime2/your-code-as-a-crime-scene-second-edition/ |
| **Karriereplanens reference** | Planen nævner Tornhill & Borgs "Code Red"-paper (arXiv:2203.04374) — korrekt reference. Bogen uddyber metoden bag paperet |

### 6.5 Pro .NET Memory Management, 2. udgave

| | |
|---|---|
| **Eksisterer?** | **Ja** |
| **Titel** | *Pro .NET Memory Management: For Better Code, Performance, and Scalability*, 2nd Edition |
| **Forfattere** | Konrad Kokosa, **Christophe Nasarre & Kevin Gosse** (nye medforfattere) |
| **Forlag** | Apress |
| **Udgivelse** | **Oktober 2024** |
| **ISBN** | 979-8-868-80452-6 |
| **Pris** | Ca. 500 DKK |
| **URL** | https://link.springer.com/book/10.1007/979-8-8688-0453-3 |
| **Bemærkning** | Dækker op til .NET 8. Principper gælder for .NET 10, men GC-specifik adfærd kan have ændret sig |
| **Karriereplanens reference** | Planen nævner GC og allokering i modul 2 uden at nævne denne bog. **Anbefaling: tilføj som Støtte-prioritet for niveau 2-3.** |

---

## Samlet overblik: hvad der mangler og hvad der er forkert

### Faktuelle korrektioner i den eksisterende plan

| Modul | Påstand | Virkelighed | Vigtighed |
|---|---|---|---|
| 02 | ".NET 10 support til 14. november 2028" | Reel dato er **10. november 2028** | Lav — fire dages forskel |
| 02 | (Ingen versionsinformation for BenchmarkDotNet) | Nuværende version er **0.15.8** med .NET 10-support | Lav |

### Prioriteret tilføjelsesliste

| # | Emne | Prioritet | Timer | Modul det supplerer |
|---|---|---|---|---|
| 1 | GitHub Actions .NET-monorepo patterns | Vigtig | 7-10 | 02 (drift/deploy) |
| 2 | DORA 2024/2025-rapporter | Vigtig | 3-4 | 06 (observability), 07 (governance) |
| 3 | ADR-skabeloner og -værktøjer | Kritisk | 1 + løbende | 01 (rollen), 10 (produkt) |
| 4 | Shape Up (allerede i planen) | Kritisk | 3-4 | 10 |
| 5 | SRE-bøger (gratis online) | Støtte | 8-12 | 06 |
| 6 | Technology Strategy Patterns | Vigtig | 6-8 | 12 (mandat) |
| 7 | Dansk IT netværksgruppe + Arkitekturdagen | Vigtig | 4 møder + 1 dag/år | Alle |
| 8 | Bicep vs. Terraform argumentation | Vigtig | 2 | 03 (Azure) |
| 9 | DDIA 2. udgave (marts 2026) | Vigtig | 15-20 | 04 (systemdesign) |
| 10 | Monte Carlo-forecasting implementation | Vigtig | 6-9 | 10 |
| 11 | B2B SaaS-prissætning | Støtte | 2-3 | 09 (domæne), 10 |
| 12 | SE Radio podcast | Vigtig | 45 min/uge | Alle |
| 13 | O'Reilly Architecture Katas | Vigtig | 6-8 uger | 01, 04 |
| 14 | Team Topologies (begreber) | Støtte | 1-5 | 07, 12 |
| 15 | Pro .NET Memory Management 2. udg. | Støtte | 15-20 | 02 |

**Samlet ekstra tidsinvestering:** 80-120 timer over 12 måneder, fordelt jævnt. Det svarer til 2-3 timer om ugen oven i den eksisterende plan.

---

*Researched 13. september 2026. Næste revalidering: marts 2027.*
